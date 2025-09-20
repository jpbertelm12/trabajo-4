Para correcta ejecuccion del repositorio se debe crear un archivo .env con las siguientes especificiaciones:

# Servidor vLLM
VLLM_BASE_URL=https://8001-xxxxx.cloudspaces.litng.ai/v1
VLLM_MODEL=Qwen/Qwen2.5-0.5B-Instruct
VLLM_API_KEY=EMPTY    # clave ficticia, solo porque OpenAI client la requiere

# Servidor Ollama
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.1:8b   # o el modelo que tengas cargado en ollama

Cambiando los link y puertos que se usaran para alojar las conexiones correspondientes con los servidores de OpenAI y Ollama desde lighting AI
