import os
import gradio as gr
from dotenv import load_dotenv
from backends import chat_ollama, chat_openai

# Cargar .env desde la raíz del proyecto
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

DEFAULT_BACKEND = os.getenv("DEFAULT_BACKEND", "ollama")  # "ollama" | "openai"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
VLLM_MODEL   = os.getenv("VLLM_MODEL", "TU-MODELO")

def infer_backend(message, history, backend, model):
    # Gradio pasa: message, history, backend, model
    text = message["content"] if isinstance(message, dict) else str(message)
    if backend == "ollama":
        out = chat_ollama(text, model or OLLAMA_MODEL)
    else:
        out = chat_openai(text, model or VLLM_MODEL)
    return {"role": "assistant", "content": out}

with gr.Blocks() as demo:
    gr.Markdown("# Chat LLM (Ollama / vLLM)")
    with gr.Row():
        backend_dd = gr.Dropdown(choices=["ollama", "qwen"], value=DEFAULT_BACKEND, label="Backend")
        model_tb   = gr.Textbox(value="", label="Modelo (opcional)")

    gr.ChatInterface(
        fn=infer_backend,                 # <--- función normal (NO lambda)
        title="Chat",
        type="messages",
        additional_inputs=[backend_dd, model_tb],  # <--- pasa 4 args a infer_backend
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True)  # link público gradio.live
