"""
Inquisitors AI Assistant
------------------------
Chat API Router

Purpose:
    Connect the frontend with the complete
    RAG + SQLite + LLM pipeline.

Flow:

    Frontend
        ↓
    POST /api/chat
        ↓
    Session ID
        ↓
    RAG Retrieval
        ↓
    Grounded Prompt
        ↓
    Groq LLM
        ↓
    SQLite Conversation Memory
        ↓
    JSON Response

Features:
    - RAG-based answers
    - SQLite conversation history
    - Session-based conversations
    - Source tracking
    - Follow-up questions
    - Error handling
    - Input validation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.rag.retriever import (
    retrieve,
    is_relevant
)

from app.rag.prompt import (
    build_prompt,
    get_sources
)

from app.rag.llm import (
    generate_response
)

from app.rag.memory import (
    get_history,
    clear_history
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api",
    tags=["Chat"]
)


# ============================================================
# RAG COMPONENTS
# ============================================================

index = None

chunks = None

model = None

client = None


# ============================================================
# INITIALIZE RAG
# ============================================================

def initialize_rag(
    rag_index,
    rag_chunks,
    embedding_model,
    llm_client
):
    """
    Store initialized RAG components so the
    API routes can use them.
    """

    global index
    global chunks
    global model
    global client

    index = rag_index

    chunks = rag_chunks

    model = embedding_model

    client = llm_client

    print(
        "RAG components initialized successfully."
    )


# ============================================================
# CHECK RAG INITIALIZATION
# ============================================================

def check_rag_ready():
    """
    Make sure all required RAG components
    have been initialized.
    """

    if index is None:

        raise HTTPException(
            status_code=503,
            detail="FAISS vector store is not initialized."
        )

    if chunks is None:

        raise HTTPException(
            status_code=503,
            detail="Knowledge chunks are not initialized."
        )

    if model is None:

        raise HTTPException(
            status_code=503,
            detail="Embedding model is not initialized."
        )

    if client is None:

        raise HTTPException(
            status_code=503,
            detail="Groq client is not initialized."
        )


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    """
    Request body received from the frontend.
    """

    message: str = Field(
        ...,
        min_length=1,
        description="User's chatbot message."
    )

    session_id: str = Field(
        default="default-session",
        min_length=1,
        description="Unique conversation session ID."
    )


# ============================================================
# RESPONSE MODEL
# ============================================================

class ChatResponse(BaseModel):
    """
    Response returned to the frontend.
    """

    answer: str

    sources: list[str]

    session_id: str


# ============================================================
# CHAT ENDPOINT
# ============================================================

@router.post(
    "/chat",
    response_model=ChatResponse
)
def chat(request: ChatRequest):
    """
    Main chatbot endpoint.

    Pipeline:

    User question
          ↓
    FAISS retrieval
          ↓
    Relevance check
          ↓
    RAG prompt
          ↓
    Groq LLM
          ↓
    SQLite memory
          ↓
    Response
    """

    # --------------------------------------------------------
    # CHECK SYSTEM
    # --------------------------------------------------------

    check_rag_ready()


    # --------------------------------------------------------
    # CLEAN INPUT
    # --------------------------------------------------------

    question = (
        request.message
        .strip()
    )

    session_id = (
        request.session_id
        .strip()
    )


    # --------------------------------------------------------
    # VALIDATE MESSAGE
    # --------------------------------------------------------

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )


    # --------------------------------------------------------
    # VALIDATE SESSION
    # --------------------------------------------------------

    if not session_id:

        raise HTTPException(
            status_code=400,
            detail="Session ID cannot be empty."
        )


    # --------------------------------------------------------
    # RETRIEVE KNOWLEDGE
    # --------------------------------------------------------

    try:

        results = retrieve(

            question,

            model,

            index,

            chunks,

            top_k=3

        )

    except Exception as error:

        print(
            "RETRIEVAL ERROR:",
            error
        )

        raise HTTPException(

            status_code=500,

            detail=(
                "An error occurred while "
                "searching the knowledge base."
            )

        )


    # --------------------------------------------------------
    # CHECK RELEVANCE
    # --------------------------------------------------------

    if (
        not results
        or not is_relevant(results)
    ):

        fallback = (
            "I'm sorry, but I couldn't find reliable "
            "information about this question in the "
            "current Inquisitors Society knowledge base. "
            "Please contact the official Inquisitors "
            "administration for verified information."
        )

        return ChatResponse(

            answer=fallback,

            sources=[],

            session_id=session_id

        )


    # --------------------------------------------------------
    # BUILD RAG PROMPT
    # --------------------------------------------------------

    try:

        rag_prompt = build_prompt(

            question,

            results

        )

    except Exception as error:

        print(
            "PROMPT ERROR:",
            error
        )

        raise HTTPException(

            status_code=500,

            detail=(
                "An error occurred while "
                "building the RAG prompt."
            )

        )


    # --------------------------------------------------------
    # GENERATE LLM RESPONSE
    # --------------------------------------------------------

    try:

        answer = generate_response(

            user_question=question,

            rag_prompt=rag_prompt,

            client=client,

            session_id=session_id

        )

    except Exception as error:

        print(
            "LLM ERROR:",
            error
        )

        raise HTTPException(

            status_code=500,

            detail=(
                "An error occurred while "
                "generating the AI response."
            )

        )


    # --------------------------------------------------------
    # GET SOURCES
    # --------------------------------------------------------

    try:

        sources = get_sources(results)

    except Exception as error:

        print(
            "SOURCES ERROR:",
            error
        )

        sources = []


    # --------------------------------------------------------
    # RETURN RESPONSE
    # --------------------------------------------------------

    return ChatResponse(

        answer=answer,

        sources=sources,

        session_id=session_id

    )
