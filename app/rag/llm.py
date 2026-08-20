"""
Inquisitors AI Assistant
------------------------

LLM Generator

Flow:

User Question
      ↓
Conversation Memory
      ↓
RAG Prompt
      ↓
Groq LLM
      ↓
SQLite Memory
      ↓
Final Response
"""

import os

from dotenv import load_dotenv
from groq import Groq

from app.rag.prompt import (
    SYSTEM_PROMPT
)

from app.rag.memory import (
    get_history,
    add_message
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

API_KEY = os.getenv(
    "GROQ_API_KEY"
)

MODEL_NAME = "openai/gpt-oss-20b"


# ============================================================
# CREATE GROQ CLIENT
# ============================================================

def create_client():
    """
    Create and return the Groq client.
    """

    if not API_KEY:

        raise ValueError(
            "GROQ_API_KEY was not found. "
            "Please add it to your .env file."
        )

    return Groq(
        api_key=API_KEY
    )


# ============================================================
# GENERATE RESPONSE
# ============================================================

def generate_response(
    user_question,
    rag_prompt,
    client,
    session_id
):
    """
    Generate a grounded response using:

    1. System prompt
    2. SQLite conversation history
    3. Current RAG prompt
    4. Groq LLM
    5. Save user + assistant messages to SQLite
    """

    # --------------------------------------------------------
    # VALIDATE INPUT
    # --------------------------------------------------------

    user_question = (
        user_question or ""
    ).strip()

    rag_prompt = (
        rag_prompt or ""
    ).strip()

    session_id = (
        session_id or ""
    ).strip()

    if not user_question:

        raise ValueError(
            "User question cannot be empty."
        )

    if not session_id:

        raise ValueError(
            "Session ID cannot be empty."
        )

    if not rag_prompt:

        raise ValueError(
            "RAG prompt cannot be empty."
        )


    # --------------------------------------------------------
    # GET SQLITE CONVERSATION HISTORY
    # --------------------------------------------------------

    history = get_history(
        session_id
    )


    # --------------------------------------------------------
    # BUILD LLM MESSAGES
    # --------------------------------------------------------

    messages = [

        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }

    ]


    # --------------------------------------------------------
    # ADD PREVIOUS CONVERSATION
    # --------------------------------------------------------

    if history:

        for message in history:

            role = message.get(
                "role"
            )

            content = message.get(
                "content"
            )

            if role in (
                "user",
                "assistant"
            ) and content:

                messages.append(
                    {
                        "role": role,
                        "content": content
                    }
                )


    # --------------------------------------------------------
    # ADD CURRENT RAG PROMPT
    # --------------------------------------------------------

    messages.append(
        {
            "role": "user",
            "content": rag_prompt
        }
    )


    # --------------------------------------------------------
    # CALL GROQ
    # --------------------------------------------------------

    response = client.chat.completions.create(

        model=MODEL_NAME,

        messages=messages,

        temperature=0.2

    )


    # --------------------------------------------------------
    # EXTRACT ANSWER
    # --------------------------------------------------------

    answer = (
        response
        .choices[0]
        .message
        .content
    )


    if not answer:

        raise RuntimeError(
            "Groq returned an empty response."
        )


    answer = answer.strip()


    # --------------------------------------------------------
    # SAVE USER MESSAGE TO SQLITE
    # --------------------------------------------------------

    add_message(

        session_id,

        "user",

        user_question

    )


    # --------------------------------------------------------
    # SAVE ASSISTANT MESSAGE TO SQLITE
    # --------------------------------------------------------

    add_message(

        session_id,

        "assistant",

        answer

    )


    # --------------------------------------------------------
    # RETURN ANSWER
    # --------------------------------------------------------

    return answer


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\nInitializing Inquisitors LLM...\n"
    )

    client = create_client()

    test_session = (
        "llm-direct-test-001"
    )

    test_question = (
        "What internship domains are available?"
    )

    test_rag_prompt = """
Use the following verified knowledge.

Knowledge:

Inquisitors Society offers internship domains
including:

- Artificial Intelligence
- Machine Learning
- Data Science
- Research
- Web Development
- Content Writing
- Graphic Design
- Digital Marketing

Question:

What internship domains are available?

Answer only using the provided knowledge.
Do not invent information.
""".strip()


    try:

        answer = generate_response(

            user_question=test_question,

            rag_prompt=test_rag_prompt,

            client=client,

            session_id=test_session

        )


        print(
            "\n" + "=" * 60
        )

        print(
            "LLM RESPONSE"
        )

        print(
            "=" * 60
        )

        print(
            answer
        )

        print(
            "\n" + "=" * 60
        )

        print(
            "TEST COMPLETED"
        )

        print(
            "=" * 60
        )


    except Exception as error:

        print(
            "\nLLM ERROR:"
        )

        print(
            error
        )