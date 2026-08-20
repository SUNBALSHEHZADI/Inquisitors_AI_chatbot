"""
Inquisitors AI Assistant
------------------------
Knowledge Base Document Loader
"""

from pathlib import Path


# ============================================================
# PROJECT PATH
# ============================================================

# loader.py
#     ↓
# app/rag
#     ↓
# app
#     ↓
# _chatbot  ← PROJECT ROOT

PROJECT_ROOT = Path(__file__).resolve().parents[2]

KNOWLEDGE_BASE_PATH = (
    PROJECT_ROOT
    / "knowledge_base"
    / "processed"
)


# ============================================================
# LOAD DOCUMENTS
# ============================================================

def load_documents():

    documents = []

    markdown_files = sorted(
        KNOWLEDGE_BASE_PATH.glob("*.md")
    )

    if not markdown_files:

        print(
            f"No Markdown files found in:\n"
            f"{KNOWLEDGE_BASE_PATH}"
        )

        return documents


    for file_path in markdown_files:

        try:

            content = file_path.read_text(
                encoding="utf-8"
            )

            document = {
                "content": content,
                "source": file_path.name,
                "path": str(file_path)
            }

            documents.append(document)

            print(
                f"Loaded: {file_path.name}"
            )

        except Exception as error:

            print(
                f"Error loading "
                f"{file_path.name}: {error}"
            )


    return documents


# ============================================================
# DISPLAY INFORMATION
# ============================================================

def show_documents(documents):

    print("\n" + "=" * 60)
    print("KNOWLEDGE BASE")
    print("=" * 60)

    print(
        f"Total documents loaded: {len(documents)}"
    )

    print("-" * 60)

    for index, document in enumerate(
        documents,
        start=1
    ):

        print(
            f"{index}. "
            f"{document['source']} "
            f"({len(document['content'])} characters)"
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    documents = load_documents()

    show_documents(documents)