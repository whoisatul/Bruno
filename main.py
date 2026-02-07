import os
import gradio as gr
import time
import groot  # Importing our brain
import sys
import shutil
import logging
from colorama import Fore, Style

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Bruno-Interface")

# --- Custom Theme & CSS ---
# Using a soft, professional theme suitable for a "Vault" application
theme = gr.themes.Soft(
    primary_hue="cyan",
    secondary_hue="slate",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui"]
)

custom_css = """
.gradio-container {max-width: 900px !important; margin-top: 20px;}
h1 {text-align: center; color: #0f172a;}
.chatbot {min-height: 500px; border-radius: 12px; border: 1px solid #e2e8f0;}
footer {visibility: hidden}
"""

def type_writer_effect(text):
    """Simulates a streaming response for better UX."""
    for i in range(len(text)):
        yield text[:i+1]
        time.sleep(0.005) # Adjust speed of typing

def upload_file(history, file_obj):
    """
    Handles file upload -> Ingests into Bruno -> Updates UI.
    """
    if file_obj is None:
        return history

    try:
        file_path = file_obj.name
        file_name = os.path.basename(file_path)
        
        # UI Feedback: Processing
        history.append((None, f"🔄 *Processing {file_name}...*"))
        
        # Read & Ingest
        with open(file_path, "r", encoding="utf-8") as f:
            text_content = f.read()
            
        groot.ingest_document(file_name, text_content)
        
        # UI Feedback: Success (Replace previous message)
        history[-1] = (None, f" **Secure Ingestion Complete:** `{file_name}` has been encrypted and vaulted.")
        
    except Exception as e:
        history.append((None, f" **Error:** Failed to process file. {str(e)}"))
        
    return history

def respond(message, chat_history):
    """
    Main chat loop with simulated streaming.
    """
    if not message:
        return "", chat_history
    
    # 1. Append User Message
    chat_history.append((message, ""))
    
    # 2. Get Response from Bruno (Blocking call)
    # Note: For true backend streaming, we'd need to update groot.py to yield tokens.
    # For now, we simulate the UI feel.
    try:
        full_response = groot.query_bruno(message)
    except Exception as e:
        full_response = f"⚠️ **System Error:** {str(e)}"

    # 3. Simulate Streaming (Updates the last message in history repeatedly)
    for partial_text in type_writer_effect(full_response):
        chat_history[-1] = (message, partial_text)
        yield "", chat_history

# --- UI Layout ---
with gr.Blocks(theme=theme, css=custom_css, title="Bruno - Secure RAG") as demo:
    
    # Header
    gr.Markdown(
        """
        # 🛡️ Bruno
        ### Secure Document Vault | IIIT Vadodara
        """
    )
    
    # Chat Window
    chatbot = gr.Chatbot(
        label="Bruno Terminal",
        show_label=False,
        bubble_full_width=False,
        avatar_images=(None, "https://ui-avatars.com/api/?name=Bruno+AI&background=0D8ABC&color=fff&rounded=true&size=128"),
        elem_classes="chatbot",
        type="messages" # Updated for Gradio 4.x best practices if available, else standard
    )
    
    # Input Area
    with gr.Row():
        with gr.Column(scale=8):
            msg = gr.Textbox(
                show_label=False,
                placeholder="Ask about your secure documents...",
                container=False,
                autofocus=True
            )
        with gr.Column(scale=1, min_width=100):
            upload_btn = gr.UploadButton("📂 Upload", file_types=["text"])
            
    # Controls
    with gr.Row():
        clear = gr.ClearButton([msg, chatbot], value="Clear Chat")

    # --- Interaction Events ---
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    upload_btn.upload(upload_file, [chatbot, upload_btn], [chatbot])

# --- Startup Logic ---
if __name__ == "__main__":
    print(Fore.CYAN + "\n  * Initializing Bruno System Protocol..." + Style.RESET_ALL)
    
    # 1. Ensure directories
    os.makedirs("Dataset", exist_ok=True)
    os.makedirs("Dataset/Embedded", exist_ok=True)
    
    # 2. Auto-Ingest Logic
    files = [f for f in os.listdir("Dataset") if os.path.isfile(os.path.join("Dataset", f)) and not f.endswith(".json")]
    
    if len(files) > 0:
        print(Fore.YELLOW + f"  * Found {len(files)} new files. Encrypting..." + Style.RESET_ALL)
        for file in files:
            src_path = os.path.join("Dataset", file)
            dest_path = os.path.join("Dataset/Embedded", file)
            try:
                with open(src_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    groot.ingest_document(file, content)
                shutil.move(src_path, dest_path)
                print(Fore.GREEN + f"    -> Secured: {file}" + Style.RESET_ALL)
            except Exception as e:
                print(Fore.RED + f"    -> Error: {file} | {e}" + Style.RESET_ALL)
    
    print(Fore.CYAN + "  * Bruno Interface Online: http://127.0.0.1:7860" + Style.RESET_ALL)
    demo.launch()