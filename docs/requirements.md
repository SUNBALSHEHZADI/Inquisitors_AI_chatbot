# Inquisitors Chatbot - Requirements

## 1. Objective

Develop a standalone intelligent chatbot prototype
for the Inquisitors Society.

The chatbot should answer user questions using
official and administration-approved information.

## 2. Scope

The chatbot will provide information about:

- Society introduction and objectives
- Departments
- Membership
- Internships
- Events
- Competitions
- Workshops
- Training programs
- Services
- FAQs
- Contact information
- Official communication channels

## 2.1 Target Users

- Students exploring the society, departments, training, and events
- Prospective members seeking registration guidance
- Internship applicants seeking domains and application information
- Staff or volunteers answering routine information requests
- Visitors seeking verified contact and social-media channels

## 2.2 Scope Boundaries

The assistant may summarize only information present in the approved
knowledge base. It may provide official links and contact details, but it
must not invent registration URLs, fees, deadlines, eligibility rules,
personal advice, or actions on behalf of a user. Unsupported questions must
receive a clear fallback and a route to official support.

## 3. Architecture

User
↓
Chat Interface
↓
Backend
↓
RAG Pipeline
↓
Knowledge Base
↓
LLM
↓
Response

## 4. Knowledge Source

Only official and approved information provided
by the Inquisitors administration will be used.

## 5. Out of Scope

- Website development
- Unapproved information
- Unsupported external information
- Autonomous actions not specified by the administration