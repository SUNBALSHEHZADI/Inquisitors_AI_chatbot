"""
Inquisitors AI Assistant
------------------------
Embedding Generator

Purpose:
    Convert text chunks into numerical vectors.

Pipeline:

    Documents
        ↓
    Loader
        ↓
    Chunker
        ↓
    Embeddings
        ↓
    Vector Database
"""


from sentence_transformers import SentenceTransformer

from chunker import (
    chunk_documents
)

from loader import (
    load_documents
)


# ============================================================
# EMBEDDING MODEL
# ============================================================

MODEL_NAME = "all-MiniLM-L6-v2"


# ============================================================
# LOAD MODEL
# ============================================================

def load_embedding_model():

    print("\nLoading embedding model...")

    model = SentenceTransformer(
        MODEL_NAME
    )

    print("Embedding model loaded successfully.")

    return model


# ============================================================
# CREATE EMBEDDINGS
# ============================================================

def create_embeddings(
    model,
    chunks
):
    """
    Convert all text chunks into embeddings.

    Args:
        model:
            SentenceTransformer model.

        chunks:
            List of chunk dictionaries.

    Returns:
        List of chunk dictionaries containing embeddings.
    """

    texts = [
        chunk["text"]
        for chunk in chunks
    ]


    print(
        f"\nCreating embeddings for "
        f"{len(texts)} chunks..."
    )


    vectors = model.encode(
        texts,
        show_progress_bar=True
    )


    embedded_chunks = []


    for chunk, vector in zip(
        chunks,
        vectors
    ):

        chunk_with_embedding = {
            "text": chunk["text"],
            "source": chunk["source"],
            "chunk_id": chunk["chunk_id"],
            "embedding": vector
        }

        embedded_chunks.append(
            chunk_with_embedding
        )


    return embedded_chunks


# ============================================================
# DISPLAY RESULTS
# ============================================================

def show_embedding_results(
    embedded_chunks
):

    print("\n" + "=" * 60)

    print(
        "EMBEDDING RESULTS"
    )

    print("=" * 60)


    print(
        f"Total chunks: "
        f"{len(embedded_chunks)}"
    )


    if embedded_chunks:

        first_embedding = (
            embedded_chunks[0]["embedding"]
        )

        print(
            f"Vector dimensions: "
            f"{len(first_embedding)}"
        )


        print(
            f"First source: "
            f"{embedded_chunks[0]['source']}"
        )


        print(
            f"First chunk: "
            f"{embedded_chunks[0]['chunk_id']}"
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # 1. Load documents
    # --------------------------------------------------------

    documents = load_documents()


    # --------------------------------------------------------
    # 2. Create chunks
    # --------------------------------------------------------

    chunks = chunk_documents(
        documents
    )


    # --------------------------------------------------------
    # 3. Load embedding model
    # --------------------------------------------------------

    model = load_embedding_model()


    # --------------------------------------------------------
    # 4. Generate embeddings
    # --------------------------------------------------------

    embedded_chunks = create_embeddings(
        model,
        chunks
    )


    # --------------------------------------------------------
    # 5. Display results
    # --------------------------------------------------------

    show_embedding_results(
        embedded_chunks
    )