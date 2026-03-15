import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

class DigitalTwinRAG:
    def __init__(self):
        self.vector_db = None
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        # Use Groq API with ChatOpenAI for Llama 3
        groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.llm = ChatOpenAI(
            temperature=0, 
            model_name="llama3-8b-8192",
            openai_api_base="https://api.groq.com/openai/v1",
            openai_api_key=groq_api_key
        )
        
    def initialize(self):
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(data_dir, exist_ok=True)
        
        expected_files = ["resume.txt", "linkedin.txt", "projects.txt", "about_me.txt"]
        for filename in expected_files:
            file_path = os.path.join(data_dir, filename)
            if not os.path.exists(file_path):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"This is the placeholder for {filename}. Edit this file and restart the server.\n")
                    
        loader = DirectoryLoader(data_dir, glob="*.txt", loader_cls=TextLoader)
        docs = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(docs)
        
        if len(chunks) == 0:
            print("Warning: No documents loaded.")
            return

        self.vector_db = FAISS.from_documents(chunks, self.embeddings)
        print(f"RAG Initialized with {len(chunks)} chunks.")
        
    def chat(self, user_input: str, history: list) -> str:
        if not self.vector_db:
            return "Knowledge base is empty. Please populate the /data directory and restart."
            
        docs = self.vector_db.similarity_search(user_input, k=4)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        system_prompt = f"""You are a Digital Twin representing me.
Speak professionally, clearly, and confidently. Prefer practical, real-world explanations.
Use first-person ("I", "my") when answering.
You must base your answer ONLY on the provided Context below.
Do NOT hallucinate, guess, or make up information under any circumstances.
If the information required to answer is NOT in the Context, explicitly say: "I don't know."

Context:
{context}
"""
        messages = [SystemMessage(content=system_prompt)]
        
        # history comes from Frontend in the format: [{"sender": "user", "text": "Hello"}, {"sender": "ai", "text": "Hi"}]
        # Let's map it back to Langchain
        # Actually in FastAPI we typed it as: List[Dict[str, str]] with keys 'role' and 'content' maybe?
        # I defined History as generic Dict, let's assume 'role' and 'content' is used.
        for msg in history:
            role = msg.get("role")
            content = msg.get("content")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant" or role == "ai":
                messages.append(AIMessage(content=content))
                
        # current message
        messages.append(HumanMessage(content=user_input))
        
        response = self.llm(messages)
        return response.content
