from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="kion-vectorstore",
    version="1.2.0",
    description="Kion Consulting Postgres vector database file management library and web GUI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Kion Consulting",
    author_email="thoriso@kion.co.za",
    url="https://github.com/Thoriso-Molefe/kion-vectorstore",
    project_urls={
        "Bug Tracker": "https://github.com/Thoriso-Molefe/kion-vectorstore/issues",
        "Documentation": "https://github.com/Thoriso-Molefe/kion-vectorstore",
    },
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "kion_vectorstore": [
            "static/*",
            ".env",
            "app.py",
            "dotenv_finder.py",
        ]
    },
    install_requires=[
        "python-dotenv",
        "flask",
        "flask-cors",
        "psycopg2-binary",
        "PyPDF2",
        "pgvector",
        "openai",
        "sqlalchemy",
        "tiktoken",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "env-init = kion_vectorstore.cli_init_env:main",
        ],
    },
)