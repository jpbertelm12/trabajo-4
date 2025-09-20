import os
from dotenv import load_dotenv
from openai import OpenAI
from mcp.server.fastmcp import FastMCP

load_dotenv()
BASE  = os.getenv("VLLM_BASE_URL")
MODEL = os.getenv("VLLM_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")
client = OpenAI(base_url=BASE, api_key=os.getenv("VLLM_API_KEY","EMPTY"))

mcp = FastMCP("lightning-tools")

@mcp.tool()
def chat_vllm(prompt: str, max_tokens: int = 128, temperature: float = 0.7) -> str:
    """Llama a tu vLLM en Lightning."""
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role":"user","content": prompt}],
        max_tokens=max_tokens, temperature=temperature
    )
    return r.choices[0].message.content

if __name__ == "__main__":
    mcp.run()
