import os
import re
import traceback
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
from sqlalchemy import create_engine, text
from werkzeug.utils import secure_filename

from kion_vectorstore.config import Config
from kion_vectorstore.pgvector_plugin import PGVectorPlugin
from kion_vectorstore.file_loader import FileLoader
from kion_vectorstore.text_file_loader import KionTextFileLoader
from kion_vectorstore.pdf_file_loader import KionPDFFileLoader

from kion_vectorstore.embeddings import SimpleOpenAIEmbeddings
from kion_vectorstore.llm import SimpleChatOpenAI

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / 'static'

app = Flask(__name__, static_folder=str(STATIC_DIR))
CORS(app)

def get_embeddings():
    print(f"Config loaded: {Config._is_loaded}")
    return SimpleOpenAIEmbeddings(api_key=Config.OPENAI_API_KEY, model=Config.OPENAI_EMBEDDING_MODEL)

def get_db(embeddings):
    return PGVectorPlugin(embedding_model=embeddings)

def get_llm_instance():
    return SimpleChatOpenAI(model=Config.OPENAI_MODEL, temperature=0.7, api_key=Config.OPENAI_API_KEY)

# Prompt Template
RAG_PROMPT_TEMPLATE = (
        "You are a helpful assistant. Your role is to provide extremely detailed, step-by-step, "
        "and beginner-friendly tutorials based on questions about uploaded documents."
        "\n\n"
        "Please format your answer with an empty line between each step for clarity."
        "\n\n"
        "Use ONLY the following context, which has been extracted from one or more documents, "
        "to answer the question as accurately and specifically as possible"
        "\n"
        "(Do not use your internal knowledge. If the context is empty simply let the user know that you do not have enough information to answer their question.):"
        "\n\n--- CONTEXT ---\n{context}\n--- END CONTEXT ---\n\n"
        "Question: {question}\n\n"
        "Helpful Answer:"
    )

# GUI Routes
@app.route("/")
def home():
    return send_from_directory(str(STATIC_DIR), "file_loader_gui.html")

@app.route("/file_loader_gui.html")
def page_loader():
    return send_from_directory(str(STATIC_DIR), "file_loader_gui.html")

@app.route("/file_remover_gui.html")
def page_remover():
    return send_from_directory(str(STATIC_DIR), "file_remover_gui.html")

@app.route("/chat.html")
def page_chat():
    return send_from_directory(str(STATIC_DIR), "chat.html")

@app.route('/api/list_collections', methods=['GET'])
def list_collections():
    try:
        vector_db = get_db(get_embeddings())
        collections = vector_db.list_collections()
        return jsonify(collections=collections)
    except Exception as e:
        print(f"Error fetching collections: {e}")
        return jsonify(error=str(e), collections=[]), 500

@app.route('/api/load_vectorstore', methods=['POST'])
def upload():
    vector_db : PGVectorPlugin = get_db(get_embeddings())
    try:
        num_files = int(request.form.get("num_files", 1))
    except (ValueError, TypeError):
        num_files = 1

    results = []
    for i in range(num_files):
        # Retrieve each file's details
        uploaded_file = request.files.get(f'file_{i}')
        if not uploaded_file:
            results.append({"error": f"No file uploaded for group {i+1}."})
            continue

        # Sanitize filename and build paths
        submitted_name = uploaded_file.filename or ""
        file_name = re.sub(r'\s+', '_', submitted_name)
        file_name = secure_filename(file_name)  # extra safety

        # Per-file settings
        try:
            chunk_size = int(request.form.get(f'chunk_size_{i}', 2000))
            chunk_overlap = int(request.form.get(f'chunk_overlap_{i}', 750))
        except (ValueError, TypeError):
            results.append({"error": f"Invalid numeric values in group {i+1}."})
            continue
        collection_name = request.form.get(f'collection_name_{i}', '').strip()

        # Validate
        if not collection_name:
            results.append({"error": f"Collection name is required in group {i+1}."})
            continue
        if chunk_size < 10 or chunk_size > 8000:
            results.append({"error": f"Chunk Size in group {i+1} must be between 10 and 8000."})
            continue
        if chunk_overlap < 0:
            results.append({"error": f"Chunk Overlap in group {i+1} must be >= 0."})
            continue
        if chunk_overlap > int(0.5 * chunk_size):
            results.append({"error": f"Chunk Overlap in group {i+1} exceeds the maximum Overlap Size for chunk_size={chunk_size}."})
            continue
        lower_name = file_name.lower()
        if not (lower_name.endswith('.txt') or lower_name.endswith('.pdf')):
            results.append({"error": f"Unsupported file type in group {i+1}. Please provide a .txt or .pdf file."})
            continue

        print(f"Processing file group {i+1}: file_name: {file_name}, chunk_size={chunk_size}, chunk_overlap={chunk_overlap}, collection_name={collection_name}")
        try:
            # File path
            file_dir = re.sub(r'\s+', '_', f"data/{collection_name}/")
            os.makedirs(file_dir, exist_ok=True)
            file_path = os.path.join(file_dir, file_name)
            uploaded_file.save(file_path)
            print(f"Saved uploaded file to: {file_path}")

            # Process the file based on its type
            file_loader : FileLoader = None
            if lower_name.endswith('.txt'):
                file_loader = KionTextFileLoader(
                    file_path=file_path,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
            elif lower_name.endswith('.pdf'):
                file_loader = KionPDFFileLoader(
                    file_path=file_path,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
                print(f"File loader created for: {file_path}")

            loaded_documents = file_loader.call_file_loader()
            documents = file_loader.split_data(loaded_documents=loaded_documents, collection_name=collection_name)

            vector_db.add_documents(documents, collection_name)

            print(f"Completed: file_name={file_name}, chunk_size={chunk_size}, chunk_overlap={chunk_overlap}, collection_name={collection_name}")
            results.append({
                "message": "File successfully processed and stored.",
                "file_name": file_name,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "collection_name": collection_name
            })
        except Exception as e:
            print(f"Error during file processing: {e}")
            results.append({"error": f"Failed to process file '{file_name}': {str(e)}"})

    return jsonify(results=results), 200

@app.route('/api/list_files', methods=['GET'])
def list_files():
    collection_name = request.args.get('collection_name')
    if not collection_name:
        return jsonify({"error": "collection_name required"}), 400

    try:
        engine = create_engine(Config.CONNECTION_STRING)
        with engine.connect() as conn:
            # Find collection uuid
            res = conn.execute(
                text("SELECT uuid FROM kion_pg_collection WHERE name = :name"),
                {"name": collection_name}
            ).fetchone()
            if not res:
                return jsonify({"files": []})

            collection_uuid = res[0]
            files_res = conn.execute(
                text("""
                    SELECT DISTINCT cmetadata->>'file_name' AS file_name
                    FROM kion_pg_embedding
                    WHERE collection_id = :uuid AND cmetadata->>'file_name' IS NOT NULL
                    ORDER BY file_name
                """), {"uuid": str(collection_uuid)}
            )
            files = [row[0] for row in files_res.fetchall()]
        return jsonify({"files": files})
    except Exception as e:
        print(f"Error listing files for {collection_name}: {e}")
        return jsonify(error=str(e), files=[]), 500

@app.route('/api/delete_file', methods=['POST'])
def delete_file():
    collection_name = request.form.get('collection_name')
    file_name = request.form.get('file_name')
    if not (collection_name and file_name):
        return jsonify({"error": "Both collection_name and file_name are required."}), 400
    
    vector_db = get_db(get_embeddings())
    try:
        with vector_db.engine.begin() as conn:
            # Find the UUID for the collection name
            collection_id_query = text(
                "SELECT uuid FROM kion_pg_collection WHERE name = :collection_name"
            )
            res = conn.execute(collection_id_query, {"collection_name": collection_name}).fetchone()
            if not res:
                return jsonify({"error": f"Collection '{collection_name}' not found."}), 404
            collection_uuid = res[0]

            # Delete all chunks from that file in the collection
            delete_query = text("""
                DELETE FROM kion_pg_embedding
                WHERE collection_id = :collection_uuid
                AND cmetadata->>'file_name' = :file_name
            """)
            result = conn.execute(delete_query, {
                "collection_uuid": str(collection_uuid),
                "file_name": file_name
            })

        # Delete local file if exists
        try:
            file_dir = re.sub(r'\s+', '_', f"data/{collection_name}/")
            file_path = os.path.join(file_dir, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted local file: {file_path}")
            else:
                print(f"Local file not found for deletion: {file_path}")
        except Exception as local_err:
            print(f"Error deleting local file: {local_err}")

        return jsonify({
            "status": "deleted",
            "collection_name": collection_name,
            "file_name": file_name,
            "rows_affected": result.rowcount
        }), 200
    except Exception as e:
        print(f"Error deleting file {file_name} from {collection_name}: {e}")
        return jsonify({"error": f"Failed to delete file: {str(e)}"}), 500
    
@app.route('/api/delete_collection', methods=['POST'])
def delete_collection():
    collection_name = request.form.get("collection_name")
    if not collection_name:
        return jsonify({"error": "collection_name is required."}), 400
    
    vector_db = get_db(get_embeddings())
    try:
        vector_db.delete_collection(collection_name)
        
        # Delete local folder if exists
        try:
            folder_path = re.sub(r'\s+', '_', f"data/{collection_name}/")
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                import shutil
                shutil.rmtree(folder_path)
                print(f"Deleted local folder: {folder_path}")
            else:
                print(f"Local folder not found for deletion: {folder_path}")
        except Exception as local_err:
            print(f"Error deleting local collection folder: {local_err}")

        return jsonify({"status": "deleted", "collection_name": collection_name})
    except Exception as e:
        print(f"Error deleting collection {collection_name}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/query_rag', methods=["POST"])
def query_rag():
    vector_db_plugin = get_db(get_embeddings())
    llm = get_llm_instance()
    if not vector_db_plugin or not llm:
        return jsonify({"error": "Backend services not initialized."}), 500

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    collection_names = data.get("collection_names")
    user_query = data.get("query")
    k = int(data.get("k", 5))
    temperature = float(data.get("temperature", 0.7))

    if not collection_names or not isinstance(collection_names, list) or len(collection_names) == 0:
        return jsonify({"error": "A list of 'collection_names' is required"}), 400
    if not user_query:
        return jsonify({"error": "'query' is required"}), 400

    try:
        # Aggregate all docs+scores
        all_doc_scores = []
        for collection_name in collection_names:
            results = vector_db_plugin.similarity_search_with_scores(
                collection_name=collection_name,
                query=user_query,
                k=k)
            all_doc_scores.extend([
                (doc, score, collection_name)
                for doc, score in results
            ])

        if not all_doc_scores:
            return jsonify({
                "answer": "I could not find any relevant information in the selected collections to answer your question.",
                "sources": []
            })

        # Sort by descending score (higher is more similar in PGVector)
        all_doc_scores.sort(key=lambda t: t[1], reverse=True)

        # Take top k
        top_doc_scores = all_doc_scores[:k]

        print(f"\n\nEXAMPLE DOC: {top_doc_scores}\n\n")

        # Prepare context and sources
        sources_text = "\n\n".join(
            f"Source from '{doc['metadata'].get('file_name', 'Unknown')}':\n{doc['page_content']}"
            for doc, score, coll in top_doc_scores)
        
        llm.temperature = temperature

        formatted_prompt = RAG_PROMPT_TEMPLATE.format(
            context=sources_text,
            question=user_query
        )

        print("Sending prompt to LLM...")
        resp = llm.invoke(formatted_prompt)
        answer = resp.content

        source_chunks = [
            {
                "page_content": doc['page_content'],
                "metadata": doc['metadata'],
                "score": score,
                "collection_name": coll
            }
            for doc, score, coll in top_doc_scores
        ]

        return jsonify({
            "answer": answer,
            "sources": source_chunks
        })

    except Exception as e:
        print(f"An error occurred during the RAG query:")
        print(traceback.format_exc())
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500
