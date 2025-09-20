from fastapi import FastAPI
from pydantic import BaseModel
import ollama

app = FastAPI()

class ChatIn(BaseModel):
    message: str
    model: str = "llama3.2"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(req: ChatIn):
    resp = ollama.chat(model=req.model, messages=[{"role": "user", "content": req.message}])
    return {"reply": resp["message"]["content"]}
