"""
Inquisitors AI Assistant
------------------------

FastAPI Application

Architecture:

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

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import (
    router,
    initialize_rag
)

from app.rag.retriever import (
    load_vector_store,
    load_model
)

from app.rag.llm import (
    create_client
)

from app.config import (
    ALLOWED_ORIGINS,
    API_PREFIX,
    APP_NAME,
    APP_VERSION
)


# ============================================================
# APPLICATION STARTUP
# ============================================================

def initialize_system():
    """
    Initialize all AI/RAG components.

    Components:

    1. FAISS vector store
    2. Embedding model
    3. Groq client
    """

    print("\n" + "=" * 60)
    print("INITIALIZING INQUISITORS AI ASSISTANT")
    print("=" * 60)

    # --------------------------------------------------------
    # Load FAISS vector store
    # --------------------------------------------------------

    print("\n[1/3] Loading FAISS vector store...")

    index, chunks = load_vector_store()

    # --------------------------------------------------------
    # Load embedding model
    # --------------------------------------------------------

    print("\n[2/3] Loading embedding model...")

    model = load_model()

    # --------------------------------------------------------
    # Create Groq client
    # --------------------------------------------------------

    print("\n[3/3] Creating Groq client...")

    client = create_client()

    # --------------------------------------------------------
    # Give components to API router
    # --------------------------------------------------------

    initialize_rag(
        index,
        chunks,
        model,
        client
    )

    print("\n" + "=" * 60)
    print("RAG SYSTEM READY")
    print("=" * 60)
    print("FAISS:       READY")
    print("Embeddings:  READY")
    print("Groq LLM:    READY")
    print("SQLite:      ENABLED")
    print("API:         READY")
    print("=" * 60 + "\n")


# ============================================================
# CREATE APPLICATION
# ============================================================

app = FastAPI(
    title=APP_NAME,

    description=(
        "RAG-based educational chatbot for "
        "Inquisitors Society with FAISS retrieval, "
        "Groq LLM and SQLite conversation memory."
    ),

    version=APP_VERSION
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_PATH = PROJECT_ROOT / "frontend"

app.mount(
    "/assets",
    StaticFiles(directory=FRONTEND_PATH / "assets"),
    name="assets"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=ALLOWED_ORIGINS,

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],
)


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def startup_event():

    initialize_system()


# ============================================================
# API ROUTES
# ============================================================

app.include_router(
    router,
    prefix=API_PREFIX
)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/api-info")
def root():
    """
    Basic API information.
    """

    return {
        "name": APP_NAME,
        "status": "running",
        "version": APP_VERSION,
        "architecture": (
            "FastAPI + FAISS + RAG + Groq + SQLite"
        )
    }


@app.get("/style.css")
def stylesheet():
    """Serve the frontend stylesheet for the same-origin app."""

    return FileResponse(FRONTEND_PATH / "style.css", media_type="text/css")


@app.get("/script.js")
def frontend_script():
    """Serve the frontend script for the same-origin app."""

    return FileResponse(
        FRONTEND_PATH / "script.js",
        media_type="application/javascript"
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    """
    Health-check endpoint.
    """

    return {
        "status": "healthy",
        "rag": "ready",
        "database": "sqlite",
        "llm": "groq",
        "version": APP_VERSION
    }


@app.get("/")
def frontend():
    """Serve the single-page frontend from the same Space origin."""

    return FileResponse(FRONTEND_PATH / "index.html")