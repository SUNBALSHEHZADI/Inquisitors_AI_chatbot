# Inquisitors Chatbot - Use Cases & Scenarios

**Project:** Inquisitors AI Assistant  
**Version:** 1.0.0  
**Date:** 2024-08-20  

---

## 1. Primary Use Cases

### UC001: Answer Frequently Asked Questions

**Actor:** Student/User

**Description:** User asks common questions about the society.

**Preconditions:**
- Chatbot is online
- Knowledge base is loaded
- User has access to frontend

**Main Flow:**
1. User opens chatbot interface
2. User asks "What is Inquisitors Society?"
3. System retrieves relevant knowledge from KB
4. System generates response using LLM
5. System displays answer to user
6. User reads the answer
7. User may ask follow-up question

**Example Questions:**
- "What is Inquisitors Society?"
- "Does Inquisitors organize workshops?"
- "How can I become a member?"
- "What internship domains are available?"

**Expected Outcome:**
- User receives accurate, well-formatted answer
- Answer is based on verified knowledge
- Response is within 2 seconds

**Postconditions:**
- Conversation stored in SQLite
- Session maintained for follow-ups
- No information fabrication

---

### UC002: Get Information About Specific Topics

**Actor:** Student/User

**Description:** User requests detailed information about society topics.

**Topics Covered:**
1. **Society Information**
   - Mission and vision
   - Organizational structure
   - Department details

2. **Membership**
   - Benefits
   - Requirements
   - Registration process

3. **Internships**
   - Available domains
   - Application process
   - Duration and commitment

4. **Events**
   - Upcoming events
   - Competitions
   - Workshops and training

5. **Services**
   - Programs offered
   - Support channels
   - Training opportunities

6. **Contact Information**
   - Phone numbers
   - Email addresses
   - Social media links

**Main Flow:**
1. User asks about specific topic
2. Chatbot retrieves 3 most relevant chunks
3. Chatbot verifies relevance
4. Chatbot generates comprehensive answer
5. Answer provided to user
6. Session maintained for context

**Example:**
```
User: "Tell me about internship programs"
Bot: "[Detailed internship information from KB]"
User: "What domains are available?"
Bot: "[Uses context to provide domain-specific details]"
```

**Outcome:**
- User gets detailed, accurate information
- Information is knowledge-grounded
- Follow-ups understood in context

---

### UC003: Guide User Navigation

**Actor:** Student/User

**Description:** User needs help understanding society structure and navigation.

**Guidance Topics:**
- How to register for membership
- How to apply for internship
- How to join a department
- Where to find support
- How to contact administration

**Main Flow:**
1. User asks for guidance (e.g., "How do I register?")
2. System retrieves step-by-step information
3. System provides clear instructions
4. User follows guidance
5. User may ask clarification questions
6. System provides additional details

**Example Dialogue:**
```
User: "How do I become a member?"
Bot: "To become a member: 1) Follow the membership registration 
     procedure, 2) Submit required documents, 3) Wait for approval"
User: "Where do I register?"
Bot: "You should contact the official Inquisitors administration 
     channels for the registration procedure"
User: "What's the contact number?"
Bot: "+92 309 6888664"
```

**Outcome:**
- User understands process
- User gets actionable information
- Navigation made easier

---

### UC004: Answer Event-Related Questions

**Actor:** Student/User

**Description:** User inquires about upcoming events, competitions, and workshops.

**Event Information Available:**
- Event dates and times
- Event descriptions
- Registration details
- Contact for event inquiries

**Main Flow:**
1. User asks about events
2. Chatbot retrieves events.md
3. Chatbot extracts relevant event details
4. Chatbot presents event information
5. User may ask for more details
6. Chatbot provides additional context

**Example Questions:**
- "What events are happening?"
- "When is the next competition?"
- "How do I register for the workshop?"
- "Are there any internship events?"

**Outcome:**
- User informed about events
- User can plan attendance
- User has contact info for event inquiries

---

### UC005: Handle Out-of-Scope Questions

**Actor:** Student/User

**Description:** User asks question not covered by knowledge base.

**Scope Boundaries:**
- ✅ In scope: Inquisitors Society information
- ❌ Out of scope: External topics, personal assistance, etc.

**Main Flow:**
1. User asks out-of-scope question
2. Chatbot attempts retrieval
3. Relevance check fails
4. Chatbot provides fallback response
5. Fallback directs user to support
6. User may contact support or ask different question

**Example:**
```
User: "Can you help me with my homework?"
Bot: "I'm sorry, but I couldn't find reliable information about 
     this question in the current Inquisitors Society knowledge base. 
     Please contact the official Inquisitors administration for 
     verified information."
```

**Outcome:**
- Chatbot stays within scope
- User directed to appropriate resources
- No fabricated information provided

---

### UC006: Maintain Conversation Context

**Actor:** Student/User

**Description:** User has multi-turn conversation with context.

**Main Flow:**
1. User asks initial question
2. System stores message in SQLite
3. System generates response
4. System stores response in SQLite
5. User asks follow-up based on context
6. System retrieves conversation history
7. System understands follow-up in context
8. System provides contextual answer
9. Process continues for multiple turns

**Example Dialogue:**
```
Turn 1:
User: "What internships are available?"
Bot: "Inquisitors offers internships in AI, ML, Data Science, 
     Web Dev, Content Writing, and Graphic Design"

Turn 2:
User: "Tell me more about AI internship"
Bot: "[Provides AI-specific details using context]"

Turn 3:
User: "How do I apply?"
Bot: "[Application process for AI internship]"
```

**Outcome:**
- Conversation feels natural
- Context preserved across turns
- History available for future reference

---

### UC007: Provide Multiple Source Attribution

**Actor:** Student/User

**Description:** User wants to know which documents were used for answer.

**Main Flow:**
1. User asks question
2. Chatbot retrieves results from multiple sources
3. Chatbot generates answer using best matches
4. Chatbot identifies source files used
5. Source files can be returned to user
6. User can verify information

**Example:**
```
User: "What's the contact number?"
Bot: "The official contact number for the Inquisitors Society is:
     +92 309 6888664"
Sources: contact.md

(Note: Frontend currently hides sources for cleaner UX,
but they are tracked in backend)
```

**Outcome:**
- Information is traceable
- Sources can be verified
- User has reference materials

---

## 2. Secondary Use Cases

### UC008: Technical Support

**Actor:** Support Staff/Administrator

**Description:** Support team troubleshoots chatbot issues.

**Scenarios:**
1. Chatbot gives wrong answer
   - Review knowledge base
   - Update relevant .md file
   - Reload vector store

2. Chatbot can't answer question
   - Check if topic in KB
   - Add missing information
   - Retrain with new data

3. Performance issues
   - Check server logs
   - Monitor response times
   - Optimize FAISS queries

**Troubleshooting:**
- Check server logs
- Verify knowledge base files
- Test with sample queries
- Monitor performance metrics

---

### UC009: System Administration

**Actor:** Administrator

**Description:** Admin manages chatbot system.

**Tasks:**
1. **Knowledge Base Management**
   - Add/update markdown files
   - Run loader to refresh index
   - Verify content accuracy

2. **Configuration**
   - Set environment variables
   - Adjust RAG parameters
   - Configure API keys

3. **Monitoring**
   - Check server status
   - Review error logs
   - Track usage statistics

4. **Maintenance**
   - Backup databases
   - Clear old sessions
   - Update dependencies

---

### UC010: Analytics & Improvement

**Actor:** Product Manager

**Description:** Manager analyzes chatbot usage for improvements.

**Metrics Tracked:**
- Total conversations
- Average response time
- Fallback rate
- User satisfaction signals
- Most common questions
- Unanswered questions

**Improvements Based On:**
- High fallback rate → Expand KB
- Slow responses → Optimize RAG
- Common questions → Add FAQ
- User feedback → Refine prompts

---

## 3. Actor Roles

### 3.1 End User (Student)

**Goals:**
- Get quick answers about society
- Learn about opportunities
- Find contact information
- Get guidance on processes

**Pain Points:**
- Incomplete information
- Slow response
- Information not found
- Confusion about processes

**Tools Used:**
- Web browser
- Chat interface
- LocalStorage for sessions

---

### 3.2 Support Staff

**Goals:**
- Understand chatbot capabilities
- Troubleshoot user issues
- Provide backup support
- Escalate complex questions

**Responsibilities:**
- Monitor chatbot logs
- Handle escalations
- Update knowledge base
- Provide feedback for improvements

---

### 3.3 Administrator

**Goals:**
- Keep system running
- Maintain knowledge base
- Ensure security
- Monitor performance

**Responsibilities:**
- Backup data
- Update dependencies
- Configure system
- Handle incidents

---

## 4. Workflow Scenarios

### Scenario A: New Student Journey

```
1. Student visits website
2. Opens chat (first time)
3. Asks "What is Inquisitors?"
4. Gets brief overview
5. Asks "How can I join?"
6. Gets membership process
7. Asks "How do I register?"
8. Gets contact information and steps
9. Student has session ID saved
10. Student can return later to continue
```

---

### Scenario B: Internship Inquiry

```
1. Student opens chat
2. Asks about internships
3. Learns about available domains
4. Asks about specific domain (AI)
5. Gets detailed AI internship info
6. Asks about application process
7. Gets step-by-step instructions
8. Asks "Is there an internship event?"
9. Learns about upcoming event
10. Student ready to apply
```

---

### Scenario C: Event Registration

```
1. User asks "What events are happening?"
2. Chatbot lists upcoming events
3. User interested in specific event
4. Asks "How do I register?"
5. Gets registration instructions
6. Asks for contact details
7. Receives contact information
8. User ready to register
```

---

### Scenario D: Fallback Scenario

```
1. User asks "What's the capital of France?"
2. Chatbot cannot find relevant info
3. Chatbot provides fallback response
4. User told to contact administration
5. User asks follow-up about Inquisitors instead
6. Chatbot answers new question
7. Conversation returns to normal
```

---

## 5. Data Requirements by Use Case

### UC001: FAQ Answering
- **Input:** User question (string)
- **Processing:** FAISS retrieval, LLM generation
- **Output:** Answer (string)
- **Storage:** Conversation history

### UC002: Topic Information
- **Input:** Topic question (string)
- **Processing:** KB retrieval, context building
- **Output:** Detailed answer (string)
- **Storage:** Session context

### UC003: Navigation Guidance
- **Input:** How-to question (string)
- **Processing:** Step-by-step retrieval
- **Output:** Instructions (string)
- **Storage:** Session tracking

### UC004: Event Information
- **Input:** Event question (string)
- **Processing:** Events.md retrieval
- **Output:** Event details (string)
- **Storage:** Session history

### UC005: Out-of-Scope Handling
- **Input:** Any question (string)
- **Processing:** Relevance check
- **Output:** Fallback response (string)
- **Storage:** Error logging

### UC006: Context Maintenance
- **Input:** Follow-up question (string)
- **Processing:** History + new query
- **Output:** Contextual answer (string)
- **Storage:** Updated history

### UC007: Source Attribution
- **Input:** Any question (string)
- **Processing:** Source extraction
- **Output:** Answer + sources (string + list)
- **Storage:** Session data

---

## 6. Non-Functional Requirements by Use Case

| Use Case | Response Time | Accuracy | Availability | Security |
|----------|---------------|----------|--------------|----------|
| FAQ Answering | <2s | 95% | 99.5% | Medium |
| Topic Info | <2s | 98% | 99.5% | Medium |
| Navigation | <2s | 95% | 99.5% | Low |
| Events | <2s | 98% | 99.5% | Medium |
| Fallback | <1s | 100% | 99.9% | Low |
| Context | <2s | 95% | 99.5% | Medium |
| Sources | <2s | 100% | 99.5% | Medium |

---

## 7. Success Criteria

### For Each Use Case

**UC001-004:** User gets answer
- ✅ Response time < 2 seconds
- ✅ Answer is relevant
- ✅ Answer is from knowledge base
- ✅ No information fabrication

**UC005:** Graceful fallback
- ✅ Fallback message shown
- ✅ User directed to support
- ✅ No incorrect information given

**UC006:** Context preserved
- ✅ Follow-ups understood
- ✅ History accessible
- ✅ Conversation feels natural

**UC007:** Sources available
- ✅ Sources tracked internally
- ✅ Can be displayed if needed
- ✅ Information traceable

---

## Conclusion

The Inquisitors Chatbot successfully addresses the core use cases of:
1. Answering FAQs
2. Providing topic information
3. Guiding navigation
4. Event information
5. Handling out-of-scope queries
6. Maintaining conversation context
7. Attributing sources

All use cases are supported by the RAG pipeline with proper error handling and knowledge grounding.
