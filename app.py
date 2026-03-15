import gradio as gr
import os
import time
from dotenv import load_dotenv
from gtts import gTTS
import tempfile
from groq import Groq

# Langchain and API integrations
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Internal modules
from data_loader import DataLoader
from rag_engine import RagEngine
from telegram_notifier import TelegramNotifier

load_dotenv()

# Initialize our components based on the original structure
data_loader = DataLoader(data_dir=os.path.join(os.path.dirname(__file__), "data"))
rag_engine = RagEngine(model_name="all-MiniLM-L6-v2")

print("Initializing and fetching user context...")
chunks = data_loader.load_all_data()
rag_engine.index_documents(chunks)

# Initialize Telegram Notification logic
def on_telegram_reply(text):
    print(f"\n[TELEGRAM LEARNING RECIEVED]: {text}")
    data_loader.add_learned_fact(text)
    rag_engine.add_document(text)

notifier = TelegramNotifier(callback=on_telegram_reply)
        
groq_api_key = os.getenv("GROQ_API_KEY", "")
if not groq_api_key:
    print("WARNING: GROQ_API_KEY is not set. You won't be able to query the LLM.")

from langchain_groq import ChatGroq

llm = ChatGroq(
    temperature=0, 
    model_name="llama-3.1-8b-instant",
    groq_api_key=groq_api_key
)

groq_client = Groq(api_key=groq_api_key)

def process_audio(audio_path):
    if not audio_path:
        return ""
    try:
        with open(audio_path, "rb") as file:
            transcription = groq_client.audio.transcriptions.create(
                file=("audio.wav", file.read()),
                model="whisper-large-v3-turbo",
                language="en",
            )
            return transcription.text
    except Exception as e:
        print(f"Transcription Error: {e}")
        return ""

def chat_interface(user_input, history):
    if not user_input.strip():
        return ""
        
    # Get Top-K matches from our dynamic local index
    docs = rag_engine.search(user_input, k=5)
    context = "\n\n".join(docs)
    
    system_prompt = f"""You are a Digital Twin representing your creator (Purnika or the author of the provided context).
Speak professionally, clearly, and confidently. Prefer practical, real-world explanations.
Use first-person ("I", "my") when answering.
You must base your answer ONLY on the provided Context below.
Do NOT hallucinate, guess, or make up information under any circumstances.
If the information required to answer is NOT in the Context, explicitly output EXACTLY "I don't know." and nothing else.

Context:
{context}
"""
    messages = [SystemMessage(content=system_prompt)]
    
    for msg in history:
        if isinstance(msg, dict):
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") in ["assistant", "ai"]:
                messages.append(AIMessage(content=msg.get("content", "")))
        else:
            # Fallback if somehow history still sends tuples or objects
            try:
                if hasattr(msg, 'role') and hasattr(msg, 'content'):
                    if msg.role == 'user':
                        messages.append(HumanMessage(content=msg.content))
                    else:
                        messages.append(AIMessage(content=msg.content))
            except:
                pass
        
    messages.append(HumanMessage(content=user_input))
    
    try:
        raw_response = llm.invoke(messages).content
        
        # Fallback Trigger if AI does not know based on context
        if "I don't know" in raw_response or "I do not know" in raw_response:
            alert_sent = notifier.send_message(
                f"🚨 <b>Unanswered Query!</b>\nSomeone asked your Digital Twin:\n\n<i>'{user_input}'</i>\n\nReply to this message with the answer to directly inject it into your memory database!"
            )
            return "Hmm, that's a great question, but I actually don't have the answer to that in my current memory! 📱 I've pinged my actual creator on Telegram. Try asking me again in a bit if they reply!"
            
        return raw_response
    except Exception as e:
        return f"Error connecting to LLM: {str(e)}"

custom_css = """
body {
    background: linear-gradient(-45deg, #1e1e2f, #232338, #181824, #10101a);
    background-size: 400% 400%;
}
.gradio-container {
    background: rgba(255, 255, 255, 0.03) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 15px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
}
/* Style the user message bubbles */
.user {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
}
/* Style the bot message bubbles */
.bot {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}
/* Primary button styling */
.primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    transition: all 0.3s ease !important;
}
.primary:hover {
    box-shadow: 0 0 15px rgba(118, 75, 162, 0.7) !important;
    transform: translateY(-1px) !important;
}
/* Hide the API and "Built with Gradio" footer */
footer {
    display: none !important;
}
"""

# Define Gradio Chat UI 
with gr.Blocks() as demo:
    gr.HTML("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h2>Purnika 2.0</h2>
        <p>I am Purnika Malhotra's AI twin. I will answer questions on her behalf.</p>
    </div>
    """)
    
    chatbot = gr.Chatbot(height=500, label="Chatbot")
    audio_output = gr.Audio(label="Voice Output", autoplay=True, visible=False)
    
    with gr.Row():
        msg = gr.Textbox(placeholder="Ask me something...", label="Your Question", lines=1, scale=6)
        voice_input = gr.Audio(sources=["microphone"], type="filepath", label="🎙️ Voice Input", scale=2)
        submit_btn = gr.Button("Send", variant="primary", scale=2)
        
    with gr.Row():
        clear = gr.ClearButton([msg, chatbot])
        
    gr.Examples(
        examples=[
            "What are your core skills?",
            "Tell me about your latest project.",
            "Where did you study?",
            "What is your experience with AI?"
        ],
        inputs=msg
    )
    
    # When user records audio and stops, transcribe it directly into the msg textbox
    voice_input.change(fn=process_audio, inputs=voice_input, outputs=msg)

    def respond(message, chat_history):
        if not message.strip():
            yield "", chat_history, None
            return
            
        # Simulate loading by yielding user input immediately, then calculating response
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": "Thinking..."})
        yield "", chat_history, None
        
        bot_message = chat_interface(message, chat_history[:-2])
        chat_history[-1]["content"] = bot_message
        
        try:
            tts = gTTS(text=bot_message, lang='en')
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(temp_audio.name)
            audio_path = temp_audio.name
        except Exception:
            audio_path = None
            
        yield "", chat_history, audio_path

    msg.submit(respond, [msg, chatbot], [msg, chatbot, audio_output])
    submit_btn.click(respond, [msg, chatbot], [msg, chatbot, audio_output])

if __name__ == "__main__":
    demo.queue().launch(
        server_name="0.0.0.0", 
        server_port=8000, 
        theme=gr.themes.Soft(primary_hue="purple", secondary_hue="indigo"), 
        css=custom_css
    )
