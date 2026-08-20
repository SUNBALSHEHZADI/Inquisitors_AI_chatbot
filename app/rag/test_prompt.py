"""
Test Prompt Builder
"""

from app.rag.retriever import (
    load_vector_store,
    load_model,
    retrieve
)

from app.rag.prompt import (
    build_prompt
)


if __name__ == "__main__":

    # Load vector store
    index, chunks = load_vector_store()

    # Load embedding model
    model = load_model()

    # Test question
    question = (
        "What internship domains are available?"
    )

    # Retrieve relevant knowledge
    results = retrieve(
        question,
        model,
        index,
        chunks,
        top_k=3
    )

    # Build LLM prompt
    prompt = build_prompt(
        question,
        results
    )

    print("\n")
    print("=" * 70)
    print("GENERATED RAG PROMPT")
    print("=" * 70)

    print(prompt)