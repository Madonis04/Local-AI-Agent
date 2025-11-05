# ui/gradio_app.py

import gradio as gr
from llm_host.host_integration import LocalLLMClient, Agent
import configparser # <-- ADD THIS IMPORT

# --- Read configuration from config.ini ---
config = configparser.ConfigParser()
config.read('config.ini')
LLM_MODEL_PATH = config['Paths']['llm_model_path'] # <-- REPLACE THE OLD HARDCODED PATH

# --- Initialization ---
try:
    client = LocalLLMClient(model_path=LLM_MODEL_PATH)
    agent = Agent(client)
    INITIALIZATION_SUCCESS = True
except Exception as e:
    INITIALIZATION_SUCCESS = False
    INIT_ERROR_MESSAGE = f"FATAL: Could not load the AI model. Please check the model path in ui/gradio_app.py and ensure dependencies are installed. Error: {e}"
    print(INIT_ERROR_MESSAGE)

def agent_chat(user_input, history):
    history = history or []
    response = agent.process_command(user_input)
    history.append((user_input, response))
    return history, "" # Return "" to clear the textbox

# --- Gradio UI ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 Local AI Agent")
    
    if not INITIALIZATION_SUCCESS:
        gr.Markdown(f"**Error:** {INIT_ERROR_MESSAGE}")
    else:
        chatbot = gr.Chatbot(label="Conversation", height=600)
        txt = gr.Textbox(show_label=False, placeholder="Type a message or command (e.g., 'generate code for a snake game')...")
        txt.submit(agent_chat, [txt, chatbot], [chatbot, txt])

def start_app():
    if INITIALIZATION_SUCCESS:
        print("Launching Gradio app...")
        demo.launch()
    else:
        print("Gradio app launch aborted due to initialization failure.")

if __name__ == "__main__":
    start_app()