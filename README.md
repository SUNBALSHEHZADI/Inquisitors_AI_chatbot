# Inquisitors AI Assistant Chatbot

An intelligent, knowledge-grounded chatbot for the Inquisitors Society powered by RAG (Retrieval-Augmented Generation), FAISS vector search, and Groq LLM.

Project deliverables include the requirements audit, technical documentation,
user guide, presentation outline, 40 manual scenarios, automated tests, and
frontend screenshots in `screenshots/`.

## 🎯 Overview

The Inquisitors AI Assistant provides real-time, accurate answers to questions about:
- Society introduction and objectives
- Departments and structure
- Membership information
- Internship opportunities
- Events and competitions
- Training programs and workshops
- Services and support
- FAQs and contact information

The chatbot uses a **RAG pipeline** to ground responses in official, verified knowledge rather than hallucinating information.

## 🏗️ Architecture

```
Frontend (HTML/CSS/JS)
        ↓
FastAPI Backend
        ↓
RAG Pipeline
├─ FAISS Vector Search
├─ Embedding Model (Sentence Transformers)
└─ Knowledge Base (Markdown files)
        ↓
Groq LLM (openai/gpt-oss-20b)
        ↓
SQLite Conversation Memory
        ↓
JSON Response
```

## 📋 Requirements

- Python 3.9+
- GROQ API Key (free from https://console.groq.com)
- 2GB RAM minimum
- 500MB disk space

## 🚀 Quick Start

### 1. Clone/Setup Project

```bash
cd inquisitors_chatbot
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

Create `.env` file in project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get your free GROQ API key from: https://console.groq.com/keys

### 5. Initialize Vector Store (First Time Only)

```bash
python -m app.rag.loader
```

This will:
- Load markdown files from `knowledge_base/processed/`
- Generate embeddings using Sentence Transformers
- Create FAISS index at `vector_store/inquisitors.index`

### 6. Run the Backend

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     INITIALIZING INQUISITORS AI ASSISTANT
```

### 7. Open Frontend

In your browser, navigate to the HTML file:
```
File → Open → frontend/index.html
```

Or use a simple HTTP server:
```bash
cd frontend
python -m http.server 8080
# Then visit http://localhost:8080
```

## 📁 Project Structure

```
inquisitors_chatbot/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration
│   ├── api/
│   │   ├── routes.py           # API endpoints
│   │   └── chat.py             # Chat API handler
│   ├── chatbot/
│   │   ├── chat.py             # Chatbot logic
│   │   ├── fallback.py         # Fallback responses
│   │   └── prompts.py          # Prompt templates
│   └── rag/
│       ├── __init__.py
│       ├── chat.py             # CLI chatbot
│       ├── chunker.py          # Text chunking
│       ├── embeddings.py       # Embedding logic
│       ├── llm.py              # LLM integration
│       ├── loader.py           # Knowledge loader
│       ├── memory.py           # SQLite memory
│       ├── prompt.py           # Prompt builder
│       ├── retriever.py        # FAISS retriever
│       └── vector_store.py     # Vector store utils
├── knowledge_base/
│   ├── processed/              # Markdown files (11 topics)
│   └── raw/                    # Source documents
├── frontend/
│   ├── index.html              # Main UI
│   ├── script.js               # Chat logic
│   ├── style.css               # Styling
│   └── assets/                 # Logo and images
├── vector_store/
│   └── inquisitors.index       # FAISS index
├── data/
│   ├── chatbot.db              # SQLite memory
│   └── chat_history.db         # Backup
├── test/
│   ├── test_cases.csv          # Test scenarios
│   ├── test_chatbot.py         # Chatbot tests
│   └── test_rag.py             # RAG pipeline tests
├── docs/
│   ├── requirements.md         # Requirements analysis
│   ├── feature_specification.md# Feature specs
│   ├── use_cases.md            # Use cases
│   ├── conversation_flow.md    # Conversation flow
│   ├── system_architecture.md  # Architecture details
│   ├── knowledge_base.md       # Knowledge structure
│   ├── testing_report.md       # Test results
│   └── user_guide.md           # User manual
├── screenshots/                # UI screenshots
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔌 API Endpoints

### Chat Endpoint
**POST** `/api/chat`

Request:
```json
{
  "message": "What is Inquisitors Society?",
  "session_id": "web-session-123"
}
```

Response:
```json
{
  "answer": "Inquisitors Society is a student-focused...",
  "sources": ["society.md", "departments.md"],
  "session_id": "web-session-123"
}
```

### Get Conversation History
**GET** `/api/history/{session_id}`

Returns all messages in a conversation session.

### Clear Conversation
**DELETE** `/api/history/{session_id}`

Deletes conversation history for a session.

## 🧠 How RAG Works

1. **User Question** → Sent to backend
2. **Embedding** → Question converted to vector using Sentence Transformers
3. **Retrieval** → Top-3 similar chunks found in FAISS index
4. **Relevance Check** → Verify retrieved content is relevant
5. **Prompt Building** → Create RAG prompt with question + context
6. **LLM Generation** → Groq generates grounded answer
7. **Memory Storage** → Save conversation to SQLite
8. **Response** → Return answer and sources to frontend

## 🔐 Security

- **No API Keys in Code** → Uses `.env` file (add to `.gitignore`)
- **Input Validation** → All inputs sanitized and validated
- **Error Handling** → Graceful fallback for errors
- **Knowledge-Grounded** → Only official information used
- **Session Isolation** → Users isolated by session ID

## 📊 Knowledge Base

The chatbot is trained on 11 verified documents:

1. **society.md** - Society introduction, mission, vision
2. **departments.md** - Departments and organizational structure
3. **membership.md** - Membership benefits, eligibility, registration
4. **internships.md** - Internship programs, domains, application
5. **events.md** - Upcoming events, competitions, workshops
6. **training.md** - Training programs, skill development
7. **services.md** - Services offered by the society
8. **faq.md** - Frequently asked questions
9. **contact.md** - Contact information, support channels
10. **social_media.md** - Social media links and handles
11. **sources.md** - Information sources and references

## 🧪 Testing

Run 30+ test cases:

```bash
# View test cases
cat test/test_cases.csv

# Run the automated tests
python -m pytest test/test_rag.py test/test_chatbot.py -q
pytest test/test_chatbot.py -v
pytest test/test_rag.py -v
```

## 🛠️ Development

### Add New Knowledge

1. Create `.md` file in `knowledge_base/processed/`
2. Run loader: `python -m app.rag.loader`
3. FAISS index updates automatically

### Modify System Prompt

Edit `app/rag/prompt.py` - `SYSTEM_PROMPT` constant

### Change LLM Model

Edit `app/rag/llm.py` - `MODEL_NAME` variable

### Adjust RAG Settings

Edit `app/api/routes.py` - `top_k=3` parameter

## 📈 Features

### ✅ Implemented
- Natural language interaction
- Knowledge-based responses
- Conversation history (SQLite)
- Error handling & fallbacks
- Session management
- RAG pipeline with FAISS
- Multiple API endpoints

### 🔄 Optional (Planned)
- Voice input/output
- Multilingual support
- User authentication
- Analytics dashboard
- Suggested questions
- Human support escalation

## 🐛 Troubleshooting

### "GROQ_API_KEY not found"
- Ensure `.env` file exists
- Check API key is valid at https://console.groq.com

### "FAISS index not found"
- Run: `python -m app.rag.loader`
- Check `vector_store/inquisitors.index` exists

### "Embedding model not loaded"
- First run downloads model (~500MB)
- Ensure internet connection
- Model cached in `~/.cache/huggingface/`

### "Chatbot gives irrelevant answers"
- Knowledge base may not cover topic
- Check fallback message is displayed
- Add relevant knowledge base content

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review test cases for examples
3. Check GROQ API status
4. Review knowledge base coverage

## 📄 Documentation

See `docs/` folder for:
- Requirements analysis
- Feature specifications
- Use cases and workflows
- System architecture
- Testing reports
- User guide

## 👥 Contributors

- Development Team
- Based on Inquisitors Society specifications

## 📝 License

Internal Project - Inquisitors Society

## 🎓 Educational Use

This chatbot demonstrates:
- RAG (Retrieval-Augmented Generation)
- Vector databases and embeddings
- LLM integration
- FastAPI backend design
- SQLite conversation memory
- Full-stack web development
