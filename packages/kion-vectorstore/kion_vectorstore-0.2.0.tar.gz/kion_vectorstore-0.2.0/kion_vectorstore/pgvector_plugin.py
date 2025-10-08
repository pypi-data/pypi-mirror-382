import ast
import json
import numpy as np
from typing import List, Dict
from sqlalchemy import create_engine, text
from kion_vectorstore.config import Config
from kion_vectorstore.embeddings import SimpleOpenAIEmbeddings
from kion_vectorstore.document import Document
from pgvector.sqlalchemy import Vector


def ensure_float_vector(vec):
    # If already a numpy array, return as is
    if isinstance(vec, np.ndarray):
        return vec.astype(np.float64)
    # If it's a list or tuple
    if isinstance(vec, (list, tuple)):
        return np.array(vec, dtype=np.float64)
    # If it's a string (DB returns a string)
    if isinstance(vec, str):
        # Parse the string representation of the list
        return np.array(ast.literal_eval(vec), dtype=np.float64)
    raise ValueError(f"Vector has unsupported type {type(vec)}: {vec}")

def cosine_similarity(vec1, vec2):
    v1 = np.array(vec1, dtype=np.float64)
    v2 = np.array(vec2, dtype=np.float64)
    if np.all(v1 == 0) or np.all(v2 == 0):
        return 0.0
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

class PGVectorPlugin:
    # Accept 'embedding_model' as a required argument
    def __init__(self, embedding_model):
        # Ensure the configuration is loaded before proceeding
        if not Config._is_loaded:
            raise RuntimeError(
                "Configuration has not been initialized. "
                "Please call kion_vectorstore.initialize_config() at the start of your application."
            )

        # Check param: embedding_model provided
        if embedding_model is None:
            raise ValueError("An embedding_model instance must be provided to PGVectorPlugin.")

        # Store params as the instance variables
        self.embedding_model = embedding_model
        self.connection_string = Config.CONNECTION_STRING
        print(f"Using connection string: {self.connection_string}")

        if not self.connection_string:
            raise ValueError(
                "Database CONNECTION_STRING could not be built. "
                "Please ensure all database settings are defined in your .env file."
            )

        self.engine = create_engine(self.connection_string)

        # Ensure core tables exist (collections table)
        with self.engine.begin() as conn:
            # Enable vector extension
            try:
                conn.execute(text("""
                 CREATE EXTENSION IF NOT EXISTS vector;             
                 CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
                """))
            except Exception as e:
                # Extension creation might require superuser; continue if already available
                print(f"Warning: could not ensure 'vector' extension: {e}")
            # Create collections table if not exists
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS kion_pg_collection (
                    uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    name TEXT UNIQUE NOT NULL
                );
            """))

            # Create embeddings table if not exists, default to 1536 dims.
            # If you use a different embedding size, create the table manually to match that size.
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS kion_pg_embedding (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                collection_id UUID NOT NULL REFERENCES kion_pg_collection(uuid) ON DELETE CASCADE,
                embedding VECTOR(1536),
                document TEXT,
                cmetadata JSONB
            );             
            """))

    def list_collections(self):
        with self.engine.connect() as conn:
            res = conn.execute(text("SELECT name FROM kion_pg_collection ORDER BY name;"))
            return [row[0] for row in res.fetchall()]

    def add_documents(self, documents: list[Document], collection_name):
        print(f"Documents passed to the add_documents function: {len(documents)}")

        with self.engine.begin() as conn:
            # Get collection uuid or create collection if not exists
            res = conn.execute(
                text("SELECT uuid FROM kion_pg_collection WHERE name = :name"),
                {"name": collection_name}
            ).fetchone()
            print(f"Checking if collection named {collection_name} exists: res= {res}")
            if not res:
                # Create collection
                print(f"connection string {self.engine.url}")
                create_res = conn.execute(
                    text("INSERT INTO kion_pg_collection (name) VALUES (:name) RETURNING uuid"),
                    {"name": collection_name}
                ).fetchone()
                collection_uuid = create_res[0]
                print(f"Checking if collection name is created: {collection_name}")
            else:
                collection_uuid = res[0]
                print(f"Checking if collection name is succesfully fetched: {collection_name}")

            print(f"Collection uuid= {collection_uuid}")

            print("Extracting Document text and metadata\n\n")
            document_texts = [
                doc.page_content if hasattr(doc, "page_content") else doc.get("page_content", "")
                for doc in documents
            ]
            document_metas = [
                doc.metadata if hasattr(doc, "metadata") else doc.get("metadata", {})
                for doc in documents
            ]

            # Get vectors
            simple_embedding_model : SimpleOpenAIEmbeddings = self.embedding_model
            vectors = simple_embedding_model.embed_documents(document_texts)

            # Now insert each document+vector in the embedding table
            for content, meta, vector in zip(document_texts, document_metas, vectors):
                # Ensure meta is a JSON string and vector is a list of floats
                try:
                    conn.execute(
                        text("""
                            INSERT INTO kion_pg_embedding
                                (collection_id, cmetadata, document, embedding)
                            VALUES
                                (:collection_id, :cmetadata, :document, :embedding)
                        """),
                        {
                            "collection_id": collection_uuid,
                            "cmetadata": json.dumps(meta),
                            "document": content,
                            "embedding": list(vector) if hasattr(vector, 'tolist') else vector
                        }
                    )
                except Exception as e:
                    print("INSERT ERROR:", e)
                    print(f"Failed document: {content}, metadata: {meta}, vector: {vector}")

        print(f"Added {len(documents)} documents to collection '{collection_name}'")

    def list_files(self, collection_name):
        with self.engine.connect() as conn:
            res = conn.execute(
                text("SELECT uuid FROM kion_pg_collection WHERE name = :name"),
                {"name": collection_name}
            ).fetchone()
            if not res:
                return []
            collection_uuid = res[0]
            files_res = conn.execute(
                text("""
                    SELECT DISTINCT cmetadata->>'file_name' AS file_name
                    FROM kion_pg_embedding
                    WHERE collection_id = :uuid AND cmetadata->>'file_name' IS NOT NULL
                    ORDER BY file_name
                    """), {"uuid": str(collection_uuid)}
            )
            return [row[0] for row in files_res.fetchall()]

    def delete_file(self, collection_name, file_name):
        with self.engine.begin() as conn:
            res = conn.execute(
                text("SELECT uuid FROM kion_pg_collection WHERE name = :name"),
                {"name": collection_name}
            ).fetchone()
            if not res:
                raise ValueError(f"Collection '{collection_name}' not found.")
            collection_uuid = res[0]
            result = conn.execute(
                text("""
                    DELETE FROM kion_pg_embedding
                    WHERE collection_id = :collection_uuid
                    AND cmetadata->>'file_name' = :file_name
                """),
                {"collection_uuid": str(collection_uuid), "file_name": file_name}
            )
            return result.rowcount

    def delete_collection(self, collection_name):
        with self.engine.begin() as conn:
            res = conn.execute(
                text("SELECT uuid FROM kion_pg_collection WHERE name = :name"),
                {"name": collection_name}
            ).fetchone()
            if not res:
                raise ValueError(f"Collection '{collection_name}' not found.")
            collection_uuid = res[0]
            # Remove all embeddings first
            conn.execute(
                text("DELETE FROM kion_pg_embedding WHERE collection_id = :uuid"),
                {"uuid": str(collection_uuid)}
            )
            # Remove the collection itself
            conn.execute(
                text("DELETE FROM kion_pg_collection WHERE uuid = :uuid"),
                {"uuid": str(collection_uuid)}
            )

    def similarity_search_with_scores(self, collection_name, query, k=5):
        # Find collection
        with self.engine.connect() as conn:
            res = conn.execute(
                text("SELECT uuid FROM kion_pg_collection WHERE name = :name"),
                {"name": collection_name}
            ).fetchone()
            if not res:
                return []

            collection_uuid = res[0]

            # Get all embeddings + docs from that collection
            rows = conn.execute(
                text("""
                    SELECT document, embedding, cmetadata
                    FROM kion_pg_embedding
                    WHERE collection_id = :uuid
                """),
                {"uuid": str(collection_uuid)}
            ).fetchall()

            documents = []
            vectors = []
            metadatas = []
            
            for row in rows:
                documents.append(row[0])
                vectors.append(row[1])
                metadatas.append(row[2])

            # Embed the query
            simple_embedding_model : SimpleOpenAIEmbeddings = self.embedding_model
            query_vec = simple_embedding_model.embed_query(query)#The query is a list of float

            # Compute similarities
            # First turn the list of string into a list of floats the perform the similarity search
            scores = [cosine_similarity(query_vec, ensure_float_vector(vec)) for vec in vectors]
            # Get top-K by score (descending)
            top = sorted(zip(documents, metadatas, scores), key=lambda x: x[2], reverse=True)[:k]
            # Return as (doc-dict, score)
            return [
                (
                    {
                        'page_content': doc,
                        'metadata': meta,
                    }, float(score)
                )
                for doc, meta, score in top
            ]