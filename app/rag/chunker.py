"""
Inquisitors AI Assistant
------------------------
Knowledge Base Chunker

Purpose:
    Convert loaded documents into smaller chunks
    that can later be converted into embeddings.

Pipeline:

    Markdown Documents
            ↓
        loader.py
            ↓
        chunker.py
            ↓
      Smaller Chunks
            ↓
       embeddings.py
"""


from loader import load_documents


# ============================================================
# CHUNK SETTINGS
# ============================================================

# Maximum number of characters in one chunk
CHUNK_SIZE = 500

# Number of characters repeated between consecutive chunks
# This helps preserve context between chunks.
CHUNK_OVERLAP = 100


# ============================================================
# CREATE CHUNKS
# ============================================================

def create_chunks(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """
    Split a document into overlapping chunks.

    Args:
        text (str):
            Full document text.

        chunk_size (int):
            Maximum size of each chunk.

        overlap (int):
            Number of characters shared between chunks.

    Returns:
        list[str]:
            List of text chunks.
    """

    chunks = []

    start = 0

    text_length = len(text)

    while start < text_length:

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        # Move forward while keeping overlap
        start = end - overlap

    return chunks


# ============================================================
# CHUNK ALL DOCUMENTS
# ============================================================

def chunk_documents(documents):
    """
    Create chunks from all loaded documents.

    Each chunk keeps the source document name.
    """

    all_chunks = []

    for document in documents:

        text = document["content"]
        source = document["source"]

        chunks = create_chunks(text)

        for chunk_number, chunk in enumerate(
            chunks,
            start=1
        ):

            chunk_data = {
                "text": chunk,
                "source": source,
                "chunk_id": chunk_number
            }

            all_chunks.append(chunk_data)

    return all_chunks


# ============================================================
# DISPLAY CHUNK INFORMATION
# ============================================================

def show_chunks(chunks):

    print("\n" + "=" * 60)
    print("CHUNKING RESULTS")
    print("=" * 60)

    print(
        f"Total chunks created: {len(chunks)}"
    )

    print("-" * 60)


    for chunk in chunks:

        print(
            f"Source: {chunk['source']} "
            f"| Chunk: {chunk['chunk_id']} "
            f"| Characters: {len(chunk['text'])}"
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    # Load documents
    documents = load_documents()

    # Create chunks
    chunks = chunk_documents(documents)

    # Display results
    show_chunks(chunks)