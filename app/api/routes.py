"""
Inquisitors AI Assistant
------------------------

API Routes

Endpoints:

POST   /api/chat
GET    /api/history/{session_id}
DELETE /api/history/{session_id}

Pipeline:

Frontend
    ↓
FastAPI
    ↓
FAISS Retrieval
    ↓
Relevance Check
    ↓
RAG Prompt
    ↓
Groq LLM
    ↓
SQLite Conversation Memory
    ↓
Response
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

router = APIRouter()


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):

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

    answer: str

    sources: list[str]

    session_id: str


# ============================================================
# HISTORY RESPONSE MODEL
# ============================================================

class HistoryResponse(BaseModel):

    session_id: str

    messages: list[dict]


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

        sources = get_sources(
            results
        )

    except Exception:

        sources = list(
            dict.fromkeys(
                result.get(
                    "source"
                )
                for result in results
                if result.get("source")
            )
        )


    # --------------------------------------------------------
    # RETURN RESPONSE
    # --------------------------------------------------------

    return ChatResponse(

        answer=answer,

        sources=sources,

        session_id=session_id

    )


# ============================================================
# GET CONVERSATION HISTORY
# ============================================================

@router.get(
    "/history/{session_id}",
    response_model=HistoryResponse
)
def history(session_id: str):
    """
    Retrieve conversation history from SQLite.
    """

    session_id = (
        session_id.strip()
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
    # GET SQLITE HISTORY
    # --------------------------------------------------------

    try:

        messages = get_history(
            session_id
        )

    except Exception as error:

        print(
            "HISTORY ERROR:",
            error
        )

        raise HTTPException(

            status_code=500,

            detail=(
                "An error occurred while "
                "retrieving conversation history."
            )

        )


    # --------------------------------------------------------
    # RETURN HISTORY
    # --------------------------------------------------------

    return HistoryResponse(

        session_id=session_id,

        messages=messages

    )


# ============================================================
# DELETE CONVERSATION HISTORY
# ============================================================

@router.delete(
    "/history/{session_id}"
)
def delete_history(session_id: str):
    """
    Delete a complete conversation session
    from SQLite.
    """

    session_id = (
        session_id.strip()
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
    # DELETE SQLITE HISTORY
    # --------------------------------------------------------

    try:

        clear_history(
            session_id
        )

    except Exception as error:

        print(
            "DELETE HISTORY ERROR:",
            error
        )

        raise HTTPException(

            status_code=500,

            detail=(
                "Could not clear conversation history."
            )

        )


    # --------------------------------------------------------
    # RETURN RESULT
    # --------------------------------------------------------

    return {

        "message":
            "Conversation history cleared successfully.",

        "session_id":
            session_id

    }