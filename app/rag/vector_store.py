"""
Inquisitors AI Assistant
------------------------
Vector Store

Purpose:
    Store document embeddings in a FAISS index
    so that relevant information can be retrieved
    efficiently.

Pipeline:

    Documents
        ↓
    Chunks
        ↓
    Embeddings
        ↓
    FAISS Vector Store
        ↓
    Retriever
"""


from pathlib import Path
import pickle

import faiss
import numpy as np

from loader import load_documents
from chunker import chunk_documents
from embeddings import (
    load_embedding_model,
    create_embeddings
)


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]


VECTOR_STORE_PATH = (
    PROJECT_ROOT / "vector_store"
)


INDEX_PATH = (
    VECTOR_STORE_PATH
    / "inquisitors.index"
)


CHUNKS_PATH = (
    VECTOR_STORE_PATH
    / "chunks.pkl"
)


# ============================================================
# CREATE VECTOR STORE DIRECTORY
# ============================================================

def create_storage_directory():

    VECTOR_STORE_PATH.mkdir(
        parents=True,
        exist_ok=True
    )


# ============================================================
# CREATE FAISS INDEX
# ============================================================

def create_faiss_index(
    embedded_chunks
):
    """
    Create a FAISS index from embeddings.
    """

    # Convert embeddings to NumPy array

    vectors = np.array(
        [
            chunk["embedding"]
            for chunk in embedded_chunks
        ],
        dtype="float32"
    )


    # Get vector dimensions

    dimension = vectors.shape[1]


    # Create FAISS index

    index = faiss.IndexFlatL2(
        dimension
    )


    # Add vectors

    index.add(
        vectors
    )


    return index


# ============================================================
# SAVE VECTOR STORE
# ============================================================

def save_vector_store(
    index,
    embedded_chunks
):

    create_storage_directory()


    # Save FAISS index

    faiss.write_index(
        index,
        str(INDEX_PATH)
    )


    # Remove embeddings before saving chunks
    # because FAISS already stores the vectors.

    chunks_for_storage = []

    for chunk in embedded_chunks:

        chunks_for_storage.append(
            {
                "text": chunk["text"],
                "source": chunk["source"],
                "chunk_id": chunk["chunk_id"]
            }
        )


    # Save chunk metadata

    with open(
        CHUNKS_PATH,
        "wb"
    ) as file:

        pickle.dump(
            chunks_for_storage,
            file
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)

    print(
        "BUILDING INQUISITORS VECTOR STORE"
    )

    print("=" * 60)


    # --------------------------------------------------------
    # 1. Load documents
    # --------------------------------------------------------

    print("\n[1/5] Loading documents...")

    documents = load_documents()


    # --------------------------------------------------------
    # 2. Create chunks
    # --------------------------------------------------------

    print("\n[2/5] Creating chunks...")

    chunks = chunk_documents(
        documents
    )

    print(
        f"Created {len(chunks)} chunks."
    )


    # --------------------------------------------------------
    # 3. Load embedding model
    # --------------------------------------------------------

    print(
        "\n[3/5] Loading embedding model..."
    )

    model = load_embedding_model()


    # --------------------------------------------------------
    # 4. Create embeddings
    # --------------------------------------------------------

    print(
        "\n[4/5] Creating embeddings..."
    )

    embedded_chunks = create_embeddings(
        model,
        chunks
    )


    # --------------------------------------------------------
    # 5. Create and save FAISS index
    # --------------------------------------------------------

    print(
        "\n[5/5] Creating FAISS vector store..."
    )

    index = create_faiss_index(
        embedded_chunks
    )


    save_vector_store(
        index,
        embedded_chunks
    )


    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    print("\n" + "=" * 60)

    print(
        "VECTOR STORE CREATED SUCCESSFULLY"
    )

    print("=" * 60)

    print(
        f"Vectors stored: {index.ntotal}"
    )

    print(
        f"Vector dimensions: {index.d}"
    )

    print(
        f"\nFAISS index:"
        f"\n{INDEX_PATH}"
    )

    print(
        f"\nChunk metadata:"
        f"\n{CHUNKS_PATH}"
    )