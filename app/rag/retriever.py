"""
Inquisitors AI Assistant
------------------------

RAG Retriever

Purpose:
    Convert the user's question into an embedding,
    search the FAISS vector store, determine relevance,
    build the knowledge context, and return sources.

Pipeline:

    User Question
          ↓
    Search Query Builder
          ↓
    Sentence Transformer
          ↓
       FAISS
          ↓
    Relevance Filtering
          ↓
    Relevant Chunks
          ↓
    Context Builder
          ↓
    LLM
"""


from pathlib import Path
import pickle

import faiss
import numpy as np

from sentence_transformers import SentenceTransformer


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]


# ============================================================
# VECTOR STORE PATH
# ============================================================

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
# EMBEDDING MODEL
# ============================================================

MODEL_NAME = "all-MiniLM-L6-v2"


# ============================================================
# RETRIEVAL SETTINGS
# ============================================================

TOP_K = 5

# For your current FAISS setup.
# Lower distance = better match.
DISTANCE_THRESHOLD = 1.15


# ============================================================
# LOAD VECTOR STORE
# ============================================================

def load_vector_store():
    """
    Load the FAISS index and chunk metadata.
    """

    if not INDEX_PATH.exists():

        raise FileNotFoundError(
            f"FAISS index was not found:\n"
            f"{INDEX_PATH}\n\n"
            f"Run vector_store.py first."
        )

    if not CHUNKS_PATH.exists():

        raise FileNotFoundError(
            f"Chunk metadata was not found:\n"
            f"{CHUNKS_PATH}\n\n"
            f"Run vector_store.py first."
        )

    print(
        "Loading FAISS vector store..."
    )

    index = faiss.read_index(
        str(INDEX_PATH)
    )

    with open(
        CHUNKS_PATH,
        "rb"
    ) as file:

        chunks = pickle.load(file)

    print(
        f"Loaded {index.ntotal} vectors."
    )

    if index.ntotal != len(chunks):

        raise ValueError(
            "FAISS index and chunk metadata "
            "are out of sync.\n"
            f"Vectors: {index.ntotal}\n"
            f"Chunks: {len(chunks)}\n\n"
            f"Rebuild the vector store."
        )

    return index, chunks


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

def load_model():
    """
    Load the Sentence Transformer model.
    """

    print(
        "Loading embedding model..."
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    print(
        "Embedding model loaded."
    )

    return model


# ============================================================
# BUILD SEARCH QUERY
# ============================================================

def build_search_query(
    question,
    history=None
):
    """
    Build a search query for the vector store.

    For normal questions, the original question
    is sufficient.

    For follow-up questions such as:

        "What about its internships?"

    recent conversation can help create a more
    meaningful retrieval query.

    This function does NOT call the LLM.
    """

    if not question:

        return ""

    question = str(
        question
    ).strip()

    if not question:

        return ""

    # --------------------------------------------------------
    # No history
    # --------------------------------------------------------

    if not history:

        return question

    # --------------------------------------------------------
    # Use only a small amount of recent context.
    # --------------------------------------------------------

    recent_messages = history[-4:]

    context_parts = []

    for message in recent_messages:

        role = message.get(
            "role",
            ""
        )

        content = message.get(
            "content",
            ""
        )

        if not content:

            continue

        # Avoid sending extremely large history
        # into the retrieval query.

        content = str(
            content
        )[:500]

        context_parts.append(
            f"{role}: {content}"
        )

    if not context_parts:

        return question

    history_context = "\n".join(
        context_parts
    )

    return (
        f"Recent conversation:\n"
        f"{history_context}\n\n"
        f"Current question:\n"
        f"{question}"
    )


# ============================================================
# RETRIEVE
# ============================================================

def retrieve(
    question,
    model,
    index,
    chunks,
    top_k=TOP_K
):
    """
    Retrieve relevant knowledge-base chunks.

    Returns:

        [
            {
                "text": "...",
                "source": "...",
                "chunk_id": 1,
                "distance": 0.42
            }
        ]
    """

    if not question:

        return []

    if model is None:

        raise ValueError(
            "Embedding model is not loaded."
        )

    if index is None:

        raise ValueError(
            "FAISS index is not loaded."
        )

    if not chunks:

        return []

    # --------------------------------------------------------
    # Clean question
    # --------------------------------------------------------

    question = str(
        question
    ).strip()

    if not question:

        return []

    # --------------------------------------------------------
    # Limit TOP_K safely
    # --------------------------------------------------------

    top_k = max(
        1,
        min(
            int(top_k),
            len(chunks)
        )
    )

    # --------------------------------------------------------
    # Create embedding
    # --------------------------------------------------------

    question_vector = model.encode(
        [question],
        convert_to_numpy=True
    )

    question_vector = np.asarray(
        question_vector,
        dtype="float32"
    )

    # --------------------------------------------------------
    # FAISS search
    # --------------------------------------------------------

    distances, indices = index.search(
        question_vector,
        top_k
    )

    # --------------------------------------------------------
    # Collect results
    # --------------------------------------------------------

    results = []

    for distance, index_position in zip(
        distances[0],
        indices[0]
    ):

        if index_position == -1:

            continue

        index_position = int(
            index_position
        )

        if index_position >= len(
            chunks
        ):

            continue

        chunk = chunks[
            index_position
        ]

        result = {
            "text": chunk.get(
                "text",
                ""
            ),

            "source": chunk.get(
                "source",
                "unknown"
            ),

            "chunk_id": chunk.get(
                "chunk_id",
                index_position
            ),

            "distance": float(
                distance
            )
        }

        results.append(
            result
        )

    return results


# ============================================================
# RELEVANCE CHECK
# ============================================================

def is_relevant(
    results,
    threshold=DISTANCE_THRESHOLD
):
    """
    Determine whether at least one retrieved
    result is sufficiently relevant.

    Lower FAISS distance means a better match.
    """

    if not results:

        return False

    best_distance = results[0][
        "distance"
    ]

    return (
        best_distance <= threshold
    )


# ============================================================
# FILTER RELEVANT RESULTS
# ============================================================

def filter_relevant_results(
    results,
    threshold=DISTANCE_THRESHOLD
):
    """
    Return only chunks within the relevance threshold.
    """

    if not results:

        return []

    return [
        result
        for result in results
        if result["distance"] <= threshold
    ]


# ============================================================
# BUILD CONTEXT
# ============================================================

def build_context(
    results,
    max_chunks=5
):
    """
    Convert retrieved chunks into a structured
    knowledge context for the LLM.

    Only relevant chunks are included.

    Example:

        SOURCE 1: internships.md

        ...

        SOURCE 2: society.md

        ...
    """

    if not results:

        return ""

    relevant_results = (
        filter_relevant_results(
            results
        )
    )

    if not relevant_results:

        return ""

    relevant_results = (
        relevant_results[:max_chunks]
    )

    context_parts = []

    for number, result in enumerate(
        relevant_results,
        start=1
    ):

        source = result.get(
            "source",
            "unknown"
        )

        text = result.get(
            "text",
            ""
        ).strip()

        if not text:

            continue

        context_parts.append(
            f"SOURCE {number}: {source}\n\n"
            f"{text}"
        )

    return "\n\n".join(
        context_parts
    )


# ============================================================
# GET SOURCES
# ============================================================

def get_sources(
    results,
    relevant_only=True
):
    """
    Return unique knowledge-base source filenames.
    """

    if not results:

        return []

    if relevant_only:

        results = (
            filter_relevant_results(
                results
            )
        )

    sources = []

    for result in results:

        source = result.get(
            "source"
        )

        if (
            source
            and source not in sources
        ):

            sources.append(
                source
            )

    return sources


# ============================================================
# COMPLETE RETRIEVAL PIPELINE
# ============================================================

def retrieve_knowledge(
    question,
    model,
    index,
    chunks,
    history=None,
    top_k=TOP_K
):
    """
    Complete retrieval pipeline.

    Steps:

        1. Build search query
        2. Embed query
        3. Search FAISS
        4. Check relevance
        5. Build context
        6. Extract sources

    Returns:

        {
            "query": "...",
            "results": [...],
            "context": "...",
            "sources": [...],
            "relevant": True/False
        }
    """

    search_query = build_search_query(
        question,
        history
    )

    results = retrieve(
        search_query,
        model,
        index,
        chunks,
        top_k=top_k
    )

    relevant = is_relevant(
        results
    )

    context = build_context(
        results
    )

    sources = get_sources(
        results
    )

    return {
        "query": search_query,
        "results": results,
        "context": context,
        "sources": sources,
        "relevant": relevant
    }


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results(
    question,
    results
):
    """
    Display retrieval results for debugging
    and development.
    """

    print()
    print("=" * 70)
    print("RETRIEVAL RESULTS")
    print("=" * 70)

    print(
        f"\nQuestion:\n{question}"
    )

    if not results:

        print(
            "\nNo results found."
        )

        return

    print(
        "\n" + "-" * 70
    )

    for number, result in enumerate(
        results,
        start=1
    ):

        print(
            f"\nResult {number}"
        )

        print(
            f"Source: "
            f"{result['source']}"
        )

        print(
            f"Chunk: "
            f"{result['chunk_id']}"
        )

        print(
            f"Distance: "
            f"{result['distance']:.4f}"
        )

        print(
            f"Relevant: "
            f"{result['distance'] <= DISTANCE_THRESHOLD}"
        )

        print(
            f"\nContent:\n"
            f"{result['text']}"
        )

        print(
            "\n" + "-" * 70
        )


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("INQUISITORS RAG RETRIEVER TEST")
    print("=" * 70)

    # --------------------------------------------------------
    # Load FAISS
    # --------------------------------------------------------

    index, chunks = load_vector_store()

    # --------------------------------------------------------
    # Load embedding model
    # --------------------------------------------------------

    model = load_model()

    # --------------------------------------------------------
    # Test questions
    # --------------------------------------------------------

    questions = [

        "What internship domains are available?",

        "How can I become a member?",

        "What events does the society organize?",

        "What is Inquisitors Society?"

    ]

    # --------------------------------------------------------
    # Run retrieval
    # --------------------------------------------------------

    for question in questions:

        results = retrieve(
            question,
            model,
            index,
            chunks
        )

        display_results(
            question,
            results
        )

        print(
            f"\nRelevant: "
            f"{is_relevant(results)}"
        )

        print(
            f"Sources: "
            f"{get_sources(results)}"
        )

        context = build_context(
            results
        )

        print(
            "\nKnowledge Context:"
        )

        print(
            context
        )

        print(
            "\n" + "=" * 70
        )