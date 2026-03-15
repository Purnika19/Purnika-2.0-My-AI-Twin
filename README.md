#  Purnika AI Twin

An interactive **AI Digital Twin / Conversational Resume** that represents me online.  
Users can chat with the AI to learn about my background, projects, skills, and interests as if they were speaking directly with me.

The system uses **Retrieval Augmented Generation (RAG)** to answer questions accurately using my personal data sources.

## Live Demo  
Check it here : https://huggingface.co/spaces/Purnika19/Purnika-AI-Twin

---

#  Features

### 1. Conversational Resume
Visitors can chat with an AI version of me and ask questions about:
- my projects
- technical skills
- education
- experience
- interests

---

### 2. Retrieval Augmented Generation (RAG)
The system uses a vector knowledge base to ensure answers are **factual and grounded in real data** rather than hallucinated.

---

### 3. Multi-Source Knowledge Base

The AI is trained on multiple data sources:

- `resume.json`
- LinkedIn data
- portfolio information
- GitHub repositories (auto-fetched)

---

### 4. Fast AI Responses

The system uses **Groq's LPU infrastructure** to generate responses extremely quickly.

Model used:

`llama-3.1-8b-instant`

---

### 5. ntfy Notification System

If the AI encounters a question that it cannot answer from its knowledge base:

1. It refuses to hallucinate.
2. A notification is sent to my phone via **ntfy**.
3. I can add the answer manually so the AI learns it for the future.

---

### 6. Teacher Mode (Hugging Face)

The Hugging Face Space includes a **Teacher Mode** that allows me to:

- add new Q&A pairs
- expand the AI knowledge base
- improve responses over time

This makes the AI Twin **continually improvable**.

---

# 7. System Architecture

The AI Twin system is composed of several modular components.

```
User
 │
 ▼
Gradio UI (Hugging Face Space)
 │
 ▼
AI Engine (LangChain + Groq)
 │
 ▼
RAG Engine
 │
 ▼
Vector Database (FAISS)
 │
 ▼
Knowledge Sources
(resume / LinkedIn / portfolio / GitHub)
```

---

#  Core Components

## 1️⃣ AI Engine

**File:** `app.py`

Responsible for:

- defining the AI personality
- managing the chat conversation
- communicating with the language model

Technology:

- LangChain
- Groq API
- Llama-3.1-8B model

Groq runs inference on **LPUs (Language Processing Units)** which enables extremely fast responses.

---

## 2️⃣ RAG Knowledge Engine

**File:** `rag_engine.py`

Large language models do not inherently know personal information.  
We use **Retrieval Augmented Generation (RAG)** to provide context.

Process:

1. User asks a question
2. Question converted to vector
3. FAISS searches most relevant knowledge chunks
4. Context injected into LLM prompt

Technologies used:

- SentenceTransformers
- FAISS vector database

Embedding model:

`all-MiniLM-L6-v2`

---

## 3️⃣ Data Ingestion Pipeline

**File:** `data_loader.py`

Responsible for loading and structuring knowledge data.

Sources:

- `resume.json`
- `linkedin.txt`
- `portfolio.txt`
- GitHub repositories via GitHub API

The system automatically fetches the latest GitHub repositories every time the server starts.

---

## 4️⃣ Live Notification System

If the AI cannot answer a question:

1. The model outputs an **unknown response**
2. The system triggers an **ntfy notification**
3. I receive the question instantly on my phone
4. I can update the knowledge base

This prevents hallucination and allows continuous improvement.

---

## 5️⃣ Application Frontend

The interface is built using **Gradio Blocks** and hosted on Hugging Face.

Features:

- chat interface
- suggested questions
- dark glassmorphism UI
- teacher mode controls

Custom CSS is injected into Gradio to create a modern AI interface.

---

#  Tech Stack

### Frontend
- Gradio
- Custom CSS
- Hugging Face Spaces

### Backend
- Python
- LangChain
- FastAPI-style architecture

### AI Stack
- Groq API
- Llama-3.1-8B
- SentenceTransformers

### Vector Database
- FAISS

### Notifications
- ntfy

---

# 📂 Project Structure

```
project-root

app.py
rag_engine.py
data_loader.py

data/
 ├ resume.json
 ├ linkedin.txt
 └ portfolio.txt

README.md
requirements.txt
```

---

# ▶️ Running Locally

Create a virtual environment:

```bash
python -m venv venv
source venv/Scripts/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` and add your keys:

```
GROQ_API_KEY=your_groq_key
GITHUB_USERNAME=your_username
NTFY_TOPIC=your_topic
```

Run the application:

```bash
python app.py
```

---

#  Future Improvements

- persistent memory
- better long-term knowledge updates
- analytics dashboard
- recruiter mode
- AI personality customization
- integration with portfolio website

---

#  Motivation

Resumes are static.

Conversations are not.

This project explores the idea of **AI-powered personal representation**, where instead of reading a PDF resume, people can **have a conversation with an AI version of you**.

---

# Credits

Purnika Malhotra
