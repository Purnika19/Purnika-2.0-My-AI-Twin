# AI Digital Twin / Conversational Resume

An interactive AI system that represents you and can answer questions about your background, projects, experience, and interests as if someone were directly talking to you.

## Features

- **Retrieval Augmented Generation (RAG)** architecture for factual, personalized answers.
- **Multiple Data Sources**: Ingests JSON resumes, unformatted text files (like LinkedIn/Portfolio data), and automatically fetches latest GitHub repositories.
- **FAISS & SentenceTransformers**: Creates high-query-speed local vector databases for relevant context extraction.
- **Groq & Llama3**: Harnesses `llama-3-8b-8192` through the ultra-fast Groq API.
- **Telegram Notifications**: Graceful fallback mechanism. The model refuses to hallucinate when you ask it an unlearned question; instead, it sends an alert to your Telegram directly.

## Installation

1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/Scripts/activate # On Windows PowerShell
   ```

2. Install the necessary dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Rename `.env.example` to `.env` and fill in your keys:
   - `GROQ_API_KEY`: Get this from [Groq Console](https://console.groq.com/keys)
   - `TELEGRAM_BOT_TOKEN`: Use [@BotFather](https://t.me/BotFather) on Telegram
   - `TELEGRAM_CHAT_ID`: Viewable via bots like [@userinfobot](https://t.me/userinfobot)
   - `GITHUB_USERNAME`: (Optional) Automatically indexes your repos.

## Feeding Your Knowledge Base

Data is loaded from the `data/` folder and external APIs:

- **`data/resume.json`**: Populate this with your structured resume data.
- **`data/linkedin.txt`**: Dump any extra context from LinkedIn or your cover letter here.
- **`data/portfolio.txt`**: Additional info from your personal website.

*Simply use double enters (empty lines) to separate chunks of information in text files.*

## Running the Application

Execute the entry point:
```bash
python app.py
```
Your browser will open up to the Gradio web UI.
