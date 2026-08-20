"""
Inquisitors AI Assistant
------------------------

Complete RAG Chatbot

Pipeline:

User Question
      ↓
Retriever
      ↓
Relevant Knowledge
      ↓
Prompt Builder
      ↓
LLM
      ↓
Final Answer
"""

from app.rag.retriever import (
    load_vector_store,
    load_model,
    retrieve,
    is_relevant
)

from app.rag.prompt import (
    build_prompt,
    get_sources
)

from app.rag.llm import (
    create_client,
    generate_response
)

from app.rag.memory import (
    add_message
)


# ============================================================
# CONFIGURATION
# ============================================================

TOP_K = 3


# ============================================================
# INITIALIZE RAG SYSTEM
# ============================================================

def initialize():

    print("\n" + "=" * 60)
    print("INITIALIZING INQUISITORS AI ASSISTANT")
    print("=" * 60)

    # Load FAISS index and chunks
    index, chunks = load_vector_store()

    # Load embedding model
    model = load_model()

    # Create LLM client
    client = create_client()

    print("\nRAG system initialized successfully.")

    return (
        index,
        chunks,
        model,
        client
    )


# ============================================================
# PROCESS USER QUESTION
# ============================================================

def answer_question(
    question,
    index,
    chunks,
    model,
    client,
    session_id="cli-session"
):

    # --------------------------------------------------------
    # Step 1: Retrieve relevant knowledge
    # --------------------------------------------------------

    results = retrieve(
        question,
        model,
        index,
        chunks,
        top_k=TOP_K
    )


    # --------------------------------------------------------
    # Step 2: Check retrieval confidence
    # --------------------------------------------------------

    if not is_relevant(results):

        fallback = (
            "I'm sorry, but I couldn't find reliable "
            "information about this question in the "
            "current Inquisitors Society knowledge base. "
            "Please contact the official Inquisitors "
            "administration for verified information."
        )

        return fallback, results


    # --------------------------------------------------------
    # Step 3: Build RAG prompt
    # --------------------------------------------------------

    rag_prompt = build_prompt(
        question,
        results
    )


    # --------------------------------------------------------
    # Step 4: Generate LLM response
    # --------------------------------------------------------

    answer = generate_response(
        user_question=question,
        rag_prompt=rag_prompt,
        client=client,
        session_id=session_id
    )

    # --------------------------------------------------------
    # Step 5: Save to conversation memory
    # --------------------------------------------------------

    add_message(
        session_id=session_id,
        role="user",
        content=question
    )

    add_message(
        session_id=session_id,
        role="assistant",
        content=answer
    )

    return answer, results


# ============================================================
# DISPLAY SOURCES
# ============================================================

def display_sources(results):

    sources = get_sources(results)

    if not sources:
        return

    print("\n" + "-" * 60)
    print("KNOWLEDGE SOURCES")
    print("-" * 60)

    for source in sources:

        print(f"• {source}")


# ============================================================
# MAIN CHAT LOOP
# ============================================================

def main():

    index, chunks, model, client = initialize()

    print("\n")
    print("=" * 60)
    print("INQUISITORS AI ASSISTANT")
    print("=" * 60)

    print(
        "\nAsk questions about Inquisitors Society."
    )

    print(
        "Type 'exit' to close the chatbot."
    )

    print("=" * 60)


    while True:

        print()

        question = input(
            "You: "
        ).strip()


        # ----------------------------------------------------
        # Exit
        # ----------------------------------------------------

        if question.lower() in [
            "exit",
            "quit",
            "q"
        ]:

            print(
                "\nAssistant: Goodbye! "
                "Have a great day."
            )

            break


        # ----------------------------------------------------
        # Empty question
        # ----------------------------------------------------

        if not question:

            print(
                "Assistant: "
                "Please enter a question."
            )

            continue


        # ----------------------------------------------------
        # Generate answer
        # ----------------------------------------------------

        try:

            answer, results = answer_question(
                question,
                index,
                chunks,
                model,
                client,
                session_id="cli-session"
            )


            print("\nAssistant:")
            print(answer)


            # Show retrieved sources
            display_sources(
                results
            )


        except Exception as error:

            print(
                "\nAssistant: "
                "Sorry, I was unable to process "
                "your question."
            )

            print(
                f"\nTechnical error: {error}"
            )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()