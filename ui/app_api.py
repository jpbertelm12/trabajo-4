import os
import json
import time
import requests
import gradio as gr
from dotenv import load_dotenv

# --- Cargar .env desde la raíz del proyecto ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

# --- Defaults / Vars ---
DEFAULT_BACKEND = os.getenv("DEFAULT_BACKEND", "ollama")  # "ollama" | "openai"
OLLAMA_HOST     = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "llama3.2")
VLLM_BASE_URL   = os.getenv("VLLM_BASE_URL", "")
VLLM_API_KEY    = os.getenv("VLLM_API_KEY", "EMPTY")
VLLM_MODEL      = os.getenv("VLLM_MODEL", "TU-MODELO")

THEME = gr.themes.Soft(
    primary_hue="indigo",
    secondary_hue="slate",
    neutral_hue="slate",
).set(
    body_background_fill="#0b1020",
    block_background_fill="#0f172a",
    block_border_width="1px",
    block_border_color="#1f2937",
    input_background_fill="#0b1020",
    input_border_width="1px",
    input_border_color="#1f2937",
)

CUSTOM_CSS = """
#app-title { 
  font-size: 28px; font-weight: 800; 
  letter-spacing: .3px; margin-bottom: 4px;
}
#app-sub { 
  color: #94a3b8; margin-top: -4px; 
}
#footer { color:#94a3b8; font-size:12px; text-align:center; padding:8px 0 0; }
.gradio-container { max-width: 1200px !important; margin: 0 auto; }
.rounded-card .gr-box { border-radius: 16px !important; }
"""

# ---------- Backends ----------
def chat_ollama(prompt: str, model: str, temperature: float, max_tokens: int, system_prompt: str):
    msgs = []
    if system_prompt.strip():
        msgs.append({"role": "system", "content": system_prompt})
    msgs.append({"role": "user", "content": prompt})
    payload = {"model": model or OLLAMA_MODEL,
               "messages": msgs,
               "stream": False,
               # algunos backends ignoran temp/max; se incluyen por claridad
               "options": {"temperature": float(temperature)}}
    r = requests.post(f"{OLLAMA_HOST}/api/chat", json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    return (data.get("message") or {}).get("content", "").strip()

def chat_openai(prompt: str, model: str, temperature: float, max_tokens: int, system_prompt: str):
    try:
        from openai import OpenAI
    except ImportError:
        return "(Falta instalar 'openai': pip install openai)"
    base = VLLM_BASE_URL
    if not base:
        return "(Configura VLLM_BASE_URL en .env)"
    client = OpenAI(base_url=base, api_key=VLLM_API_KEY or "EMPTY")
    messages = []
    if system_prompt.strip():
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    resp = client.chat.completions.create(
        model=model or VLLM_MODEL,
        messages=messages,
        temperature=float(temperature),
        max_tokens=int(max_tokens) if max_tokens else None,
    )
    return resp.choices[0].message.content.strip()

# ---------- App Logic ----------
def infer(message, history, backend, model, temperature, max_tokens, system_prompt):
    # message: puede ser str o {"role":"user","content":"..."} si type="messages"
    text = message["content"] if isinstance(message, dict) else str(message)
    try:
        if backend == "ollama":
            out = chat_ollama(text, model or OLLAMA_MODEL, temperature, max_tokens, system_prompt)
        else:
            out = chat_openai(text, model or VLLM_MODEL, temperature, max_tokens, system_prompt)
        return {"role": "assistant", "content": out}
    except Exception as e:
        return {"role": "assistant", "content": f"⚠️ Error: {e}"}

def clear_chat():
    return None

def download_transcript(history):
    # history es lista de mensajes (role/content) si type="messages"
    ts = int(time.time())
    name = f"chat_transcript_{ts}.json"
    data = json.dumps(history or [], ensure_ascii=False, indent=2)
    with open(name, "w", encoding="utf-8") as f:
        f.write(data)
    return name

# ---------- UI ----------
with gr.Blocks(theme=THEME, css=CUSTOM_CSS, fill_height=True) as demo:
    # HEADER
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("<div id='app-title'>⚡ Chat LLM – Taller 1.1 ~ 1.3</div><div id='app-sub'>Cambia backend entre Ollama y vLLM (Lightning). Ajusta temperatura, tokens y prompt de sistema.</div>")

    with gr.Row():
        # SIDEBAR / CONTROLES
        with gr.Column(scale=4, min_width=320, elem_classes=["rounded-card"]):
            gr.Markdown("### ⚙️ Configuración")
            backend_dd = gr.Dropdown(
                label="Backend", choices=["ollama","openai"], value=DEFAULT_BACKEND
            )
            model_tb = gr.Textbox(
                label="Modelo (opcional)",
                value="" if DEFAULT_BACKEND=="ollama" else VLLM_MODEL,
                placeholder="Ej: llama3.2  |  mistralai/Mistral-7B-Instruct-v0.2"
            )
            temperature_sl = gr.Slider(0.0, 1.5, value=0.7, step=0.1, label="Temperatura")
            max_tokens_sl = gr.Slider(32, 2048, value=256, step=32, label="Máx. tokens (límite)")
            system_tb = gr.Textbox(label="Prompt de sistema (opcional)", value="", lines=3, placeholder="Instrucciones de estilo/rol...")

            with gr.Row():
                clear_btn = gr.Button("🧹 Limpiar chat", variant="secondary")
                dl_btn    = gr.Button("⬇️ Descargar chat", variant="secondary")

            gr.Markdown("<div id='footer'>Hecho para la demo de la Tarea 4 — UI unificada (Ollama / vLLM). </div>")

        # CHAT
        with gr.Column(scale=7, elem_classes=["rounded-card"]):
            chat = gr.ChatInterface(
                fn=lambda m,h,be,mo,tmp,mtok,sys: infer(m,h,be,mo,tmp,mtok,sys),
                title="",
                type="messages",
                multimodal=False,
                additional_inputs=[backend_dd, model_tb, temperature_sl, max_tokens_sl, system_tb],
                textbox=gr.Textbox(placeholder="Escribe tu mensaje aquí...", scale=7),
            )

    # ACCIONES
    clear_btn.click(fn=clear_chat, outputs=chat.chatbot)
    dl_file = gr.File(label="Archivo", visible=False)
    dl_btn.click(fn=download_transcript, inputs=chat.chatbot, outputs=dl_file)

if __name__ == "__main__":
    # Cambia share=True si quieres el enlace gradio.live
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True)
