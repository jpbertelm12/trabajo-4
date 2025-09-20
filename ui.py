import gradio as gr
import requests, os, json, traceback

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
MODEL = os.getenv("MODEL", "llama3.2")

def chat_fn(message, history):
    try:
        user_text = message["content"] if isinstance(message, dict) else str(message)
        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": user_text}],
            "stream": False
        }
        r = requests.post(f"{OLLAMA_HOST}/api/chat",
                          headers={"Content-Type":"application/json"},
                          json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()  # ahora sí es un único JSON
        reply = ""
        if isinstance(data, dict):
            msg = data.get("message") or {}
            if isinstance(msg, dict):
                reply = msg.get("content","")
        if not reply:
            reply = f"(Respuesta vacía de Ollama: {json.dumps(data)[:500]})"
        return {"role":"assistant","content": reply}

    except Exception as e:
        print("ERROR UI->OLLAMA:", e); traceback.print_exc()
        return {"role":"assistant","content": f"Error llamando a Ollama: {e}"}

demo = gr.ChatInterface(fn=chat_fn, title="Chat LLM (Ollama vía REST)", type="messages")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True)

