import os, requests
from openai import OpenAI

# --- OLLAMA (REST) ---
def chat_ollama(prompt: str, model: str | None = None) -> str:
    base = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    model = model or os.getenv("OLLAMA_MODEL", "llama3.2")
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False}
    r = requests.post(f"{base}/api/chat", json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    return (data.get("message") or {}).get("content", "")

# --- OpenAI-compatible (vLLM/LitServe en Lightning) ---
def chat_openai(prompt: str, model: str | None = None) -> str:
    base = os.getenv("VLLM_BASE_URL")       # ej: https://.../v1
    api_key = os.getenv("VLLM_API_KEY", "EMPTY")
    model = model or os.getenv("VLLM_MODEL", "TU-MODELO")
    if not base:
        return "(Configura VLLM_BASE_URL en .env)"
    client = OpenAI(base_url=base, api_key=api_key)
    r = client.chat.completions.create(model=model,
        messages=[{"role":"user","content": prompt}],
        temperature=0.7, max_tokens=256)
    return r.choices[0].message.content
