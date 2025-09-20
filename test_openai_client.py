# test_openai_client.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # <-- carga .env

BASE = os.getenv("VLLM_BASE_URL")         # debe terminar en /v1
KEY  = os.getenv("VLLM_API_KEY", "EMPTY")
MODEL = os.getenv("VLLM_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")

print("BASE:", BASE)  # para confirmar en consola

client = OpenAI(base_url=BASE, api_key=KEY)

resp = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "Dime un haiku sobre Medellín"}],
    max_tokens=64,
    temperature=0.7,
)
print(resp.choices[0].message.content)

