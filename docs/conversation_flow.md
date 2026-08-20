# Inquisitors Chatbot - Conversation Flow

**Project:** Inquisitors AI Assistant  
**Version:** 1.0.0  
**Date:** 2024-08-20  

---

## 1. High-Level Conversation Flow

```
START
  │
  ├─→ User Opens Chat
  │   └─→ Session ID created/retrieved
  │
  ├─→ User Enters Message
  │   └─→ Frontend validation
  │
  ├─→ Message Sent to Backend
  │   └─→ HTTP POST /api/chat
  │
  ├─→ Backend Processing
  │   ├─→ RAG Pipeline
  │   └─→ SQLite Storage
  │
  ├─→ Response Received
  │   └─→ Display to user
  │
  ├─→ User Reads Answer
  │   └─→ May ask follow-up
  │
  └─→ Continue or Exit
      ├─→ Conversation continues
      └─→ Session saved for later
```

---

## 2. Single Exchange Flow

```
User Input
    │
    ├─ Frontend Validation
    │  ├─ Not empty ✓
    │  ├─ < 4000 chars ✓
    │  └─ Valid characters ✓
    │
    ├─ Session Management
    │  ├─ Check for existing session
    │  ├─ Create new if needed
    │  └─ Preserve in localStorage
    │
    ├─ HTTP Request
    │  └─ POST /api/chat
    │     ├─ message: "User question"
    │     └─ session_id: "web-123-abc"
    │
    ├─ Backend Processing
    │  │
    │  ├─ Pydantic Validation ✓
    │  │
    │  ├─ RAG Pipeline
    │  │  ├─ Step 1: Embed question
    │  │  ├─ Step 2: Search FAISS
    │  │  ├─ Step 3: Check relevance
    │  │  ├─ Step 4: Build prompt
    │  │  ├─ Step 5: Call LLM
    │  │  └─ Step 6: Get response
    │  │
    │  ├─ SQLite Storage
    │  │  ├─ Save user message
    │  │  └─ Save assistant response
    │  │
    │  └─ Response Preparation
    │     ├─ answer: "Generated response"
    │     ├─ sources: ["file1.md", "file2.md"]
    │     └─ session_id: "web-123-abc"
    │
    ├─ HTTP Response
    │  └─ 200 OK + JSON
    │
    ├─ Frontend Display
    │  ├─ Hide "Thinking..."
    │  ├─ Show user message
    │  ├─ Show assistant response
    │  ├─ Update chat history
    │  └─ Save session_id
    │
    └─ Ready for Next Input
       └─ User can ask follow-up
```

---

## 3. Detailed Message Processing

### 3.1 Frontend (script.js)

```javascript
// User submits message
sendMessage()
  ├─ Get text from input
  ├─ Validate (not empty)
  ├─ Display as user message
  ├─ Clear input field
  ├─ Show "Thinking..." indicator
  │
  ├─ Call getAPIResponse()
  │  ├─ Prepare JSON payload
  │  ├─ Fetch POST to /api/chat
  │  ├─ Wait for response
  │  └─ Parse JSON
  │
  ├─ On Success
  │  ├─ Remove "Thinking..."
  │  ├─ Display answer
  │  ├─ Update session_id
  │  └─ Save to localStorage
  │
  └─ On Error
     ├─ Remove "Thinking..."
     ├─ Display error message
     └─ User can retry
```

### 3.2 Backend (routes.py)

```python
chat(request: ChatRequest)
  ├─ Check RAG ready()
  │  └─ Validate all components loaded
  │
  ├─ Clean Input
  │  ├─ Strip whitespace
  │  └─ Validate length
  │
  ├─ Retrieve Knowledge
  │  ├─ retrieve(question, model, index, chunks)
  │  └─ Get top-3 results from FAISS
  │
  ├─ Check Relevance
  │  ├─ is_relevant(results)
  │  └─ If not relevant → Return fallback
  │
  ├─ Build RAG Prompt
  │  ├─ build_prompt(question, results)
  │  └─ Combine Q + knowledge context
  │
  ├─ Generate Response
  │  ├─ generate_response(user_question, rag_prompt, client)
  │  └─ Call Groq LLM
  │
  ├─ Store in SQLite
  │  ├─ add_message(session_id, "user", question)
  │  └─ add_message(session_id, "assistant", answer)
  │
  └─ Return JSON Response
     ├─ answer: response text
     ├─ sources: [file names]
     └─ session_id: session identifier
```

---

## 4. Multi-Turn Conversation Flow

### Example: Internship Inquiry

```
TURN 1: Initial Question
┌──────────────────────────────────────┐
│ User: "What internships available?"  │
├──────────────────────────────────────┤
│ System:                              │
│  1. Embed question                   │
│  2. Retrieve from KB (internship)    │
│  3. Build RAG prompt                 │
│  4. Generate answer                  │
│  5. Save to SQLite                   │
│                                      │
│ Response: "Internships include AI,   │
│  ML, Data Science, Web Dev, etc"     │
│                                      │
│ Session Memory: {turn_1_user,        │
│                  turn_1_assistant}   │
└──────────────────────────────────────┘

TURN 2: Follow-up with Context
┌──────────────────────────────────────┐
│ User: "Tell me about AI internship"  │
├──────────────────────────────────────┤
│ System:                              │
│  1. Retrieve previous context        │
│  2. Understand follow-up topic (AI)  │
│  3. Embed "AI internship"            │
│  4. Retrieve specific AI info        │
│  5. Generate answer using context    │
│  6. Save to SQLite                   │
│                                      │
│ Response: "AI internship offers      │
│  machine learning, deep learning,    │
│  NLP projects. Duration: 3-6 months" │
│                                      │
│ Session Memory: {turn_1_*,           │
│                  turn_2_user,        │
│                  turn_2_assistant}   │
└──────────────────────────────────────┘

TURN 3: Application Process
┌──────────────────────────────────────┐
│ User: "How do I apply?"              │
├──────────────────────────────────────┤
│ System:                              │
│  1. Context knows: AI internship     │
│  2. Embed "apply"                    │
│  3. Retrieve application info        │
│  4. Generate steps                   │
│  5. Save to SQLite                   │
│                                      │
│ Response: "To apply: 1) Submit CV,   │
│  2) Write statement, 3) Interview"   │
│                                      │
│ Session Memory: {turn_1_*,           │
│                  turn_2_*,           │
│                  turn_3_*}           │
└──────────────────────────────────────┘
```

---

## 5. Error Handling Flow

### 5.1 Input Validation Error

```
User Input: "" (empty)
    │
    ├─ Frontend: .trim() empty
    │  └─→ Don't send to backend
    │  └─→ Show local error
    │
    └─ User tries again
```

### 5.2 Out-of-Scope Query

```
User Query: "What's the weather?"
    │
    ├─ Backend retrieves KB chunks
    │  └─ Similarity scores all < 0.5
    │
    ├─ Relevance check FAILS
    │  └─→ is_relevant() returns False
    │
    ├─ Return fallback response
    │  └─→ "I couldn't find information..."
    │
    └─ Store in SQLite for analysis
       └─ Track out-of-scope queries
```

### 5.3 Backend Error

```
Backend Error (e.g., LLM API down)
    │
    ├─ Exception caught in routes.py
    │
    ├─ Log error for debugging
    │
    ├─ Return JSON error response
    │  └─→ 500 Server Error
    │  └─→ Generic error message (no details)
    │
    ├─ Frontend displays error
    │  └─→ "Sorry, I couldn't connect..."
    │
    └─ User can retry
```

---

## 6. Session Management Flow

```
First Visit
│
├─ No session_id in localStorage
│
├─ Frontend creates: "web-[timestamp]-[random]"
│
├─ Save to localStorage
│
├─ Send with first message
│
├─ Backend creates SQLite session entry
│
└─ Future messages use same session_id

Later Visits
│
├─ Frontend reads from localStorage
│
├─ Retrieves existing session_id
│
├─ Send with new message
│
├─ Backend finds existing session
│
├─ Appends to conversation history
│
└─ User can see previous conversation

Manual History Request
│
├─ Frontend: GET /api/history/{session_id}
│
├─ Backend retrieves from SQLite
│
├─ Returns all messages for session
│
└─ Display in chat

Clear Conversation
│
├─ Frontend: DELETE /api/history/{session_id}
│
├─ Backend deletes SQLite records
│
├─ Session cleared
│
└─ New messages start fresh
```

---

## 7. RAG Pipeline Flow Detail

```
User Question Input
│
├─ Step 1: EMBEDDING
│  ├─ Tokenize question
│  ├─ Pass to Sentence Transformers
│  ├─ Generate 384-dim vector
│  └─ Output: [0.12, 0.45, ..., 0.78]
│
├─ Step 2: VECTOR SEARCH (FAISS)
│  ├─ Load FAISS index from memory
│  ├─ Compute similarity to all vectors
│  ├─ Return top-3 closest matches
│  └─ Output: [result_1, result_2, result_3]
│           with similarity scores
│
├─ Step 3: RELEVANCE CHECK
│  ├─ Check if score > threshold (0.5)
│  ├─ If all scores < 0.5 → Fallback
│  ├─ Otherwise → Continue
│  └─ Output: Filtered results
│
├─ Step 4: PROMPT BUILDING
│  ├─ Format system prompt
│  ├─ Add user question
│  ├─ Add retrieved knowledge chunks
│  ├─ Create instruction for LLM
│  └─ Output: Complete RAG prompt
│
├─ Step 5: LLM GENERATION
│  ├─ Call Groq API with prompt
│  ├─ LLM generates response tokens
│  ├─ Stream response back
│  └─ Output: Generated answer (string)
│
└─ Step 6: POST-PROCESSING
   ├─ Extract sources from results
   ├─ Format response
   ├─ Prepare JSON output
   └─ Return to frontend
```

---

## 8. Knowledge Retrieval Example

```
Question: "What's the contact number?"

Embedding:
  Sentence Transformers converts to vector
  [0.15, 0.42, 0.18, ..., 0.93]

FAISS Search Results:
  Result 1: "Phone: +92 309 6888664"
           File: contact.md
           Similarity: 0.92 ✓

  Result 2: "Email: info@inquisitors.com"
           File: contact.md  
           Similarity: 0.78 ✓

  Result 3: "Social media links on..."
           File: social_media.md
           Similarity: 0.65 ✓

Relevance Check:
  0.92 > 0.5 ✓
  0.78 > 0.5 ✓
  0.65 > 0.5 ✓
  → All relevant

RAG Prompt:
  [System: Answer using only provided knowledge]
  [Question: What's the contact number?]
  [Context: Phone: +92 309 6888664, Email: ..., Social: ...]

LLM Response:
  "The official contact number for the Inquisitors 
   Society is +92 309 6888664. You can also reach 
   them via email or social media..."

Sources:
  ["contact.md", "social_media.md"]
```

---

## 9. Conversation State Machine

```
        ┌─────────────────┐
        │ START: Idle     │
        └────────┬────────┘
                 │
                 ├─→ User Opens Chat
                 │
        ┌────────▼──────────┐
        │ WAITING_INPUT     │
        │ (for message)     │
        └────────┬──────────┘
                 │
                 ├─→ User Types & Submits
                 │
        ┌────────▼──────────┐
        │ SENDING           │
        │ (message to API)  │
        └────────┬──────────┘
                 │
           ┌─────┴──────┐
           │            │
           ↓            ↓
    ┌─────────────┐ ┌──────────┐
    │ PROCESSING  │ │  ERROR   │
    │ (RAG pipe)  │ │ (fallback)│
    └────────┬────┘ └──────┬───┘
             │             │
             └─────┬───────┘
                   │
        ┌──────────▼────────────┐
        │ DISPLAYING_RESPONSE   │
        │ (showing answer)      │
        └──────────┬────────────┘
                   │
        ┌──────────▼────────────┐
        │ WAITING_INPUT         │
        │ (for follow-up)       │
        └───────────────────────┘
                   │
        ┌──────────┴──────────────────────┐
        │                                 │
        ├─→ User Asks Follow-up ────┐    ├─→ User Closes Chat
        │                           │    │
        └─────────────┬─────────────┘    └─→ State: ENDED
                      │
                      └─→ Back to SENDING
```

---

## 10. Session Timeline Example

```
Timeline: "Session web-20240820-123abc"

[10:00:00] User opens chatbot
           → Frontend creates session_id
           → localStorage saves session_id
           → WAITING_INPUT state

[10:00:15] User: "What is Inquisitors?"
           → Message 1 stored
           → Answer generated
           → Response 1 stored
           → SQLite: 2 records

[10:00:45] User: "Tell me about internships"
           → Message 2 stored
           → Answer generated
           → Response 2 stored
           → SQLite: 4 records

[10:01:20] User: "How do I apply?"
           → Message 3 stored
           → Answer generated
           → Response 3 stored
           → SQLite: 6 records

[10:02:00] User closes chat
           → Session saved in localStorage
           → Conversation stored in SQLite

[14:30:00] User returns to website
           → Opens chat again
           → Frontend reads localStorage
           → Finds existing session_id
           → Can view history
           → Can continue conversation
           → new messages appended to same session

[14:30:15] User: "Tell me about events"
           → Message 4 stored
           → Answer generated
           → Response 4 stored
           → SQLite: 8 records (all maintained)
```

---

## 11. Error Recovery Flow

```
User Action
  │
  ├─ Retry on Network Error
  │  ├─ Show error message
  │  ├─ Provide "Retry" button
  │  ├─ User clicks Retry
  │  ├─ Resend same message
  │  └─ Continue if successful
  │
  ├─ Fallback on Invalid Answer
  │  ├─ Query out-of-scope
  │  ├─ Show fallback response
  │  ├─ Suggest contacting support
  │  ├─ User can ask different question
  │  └─ Conversation continues
  │
  └─ Session Persistence
     ├─ Even if error occurs
     ├─ Conversation saved
     ├─ User can return later
     ├─ Pick up where left off
     └─ No loss of context
```

---

## 12. Performance Checkpoints

Each exchange tracks:
- ⏱ User input time
- ⏱ API request time
- ⏱ RAG pipeline time
  - Embedding: <100ms
  - FAISS search: <100ms
  - LLM generation: 1-3s
- ⏱ Response display time
- ⏱ Total end-to-end time (target: <2s)

---

## Conclusion

The conversation flow is designed for:
- ✅ Smooth user experience
- ✅ Multi-turn context awareness
- ✅ Graceful error handling
- ✅ Session persistence
- ✅ Reliable knowledge grounding
- ✅ Fast response times
