import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1:8b"

def generate_answer(question: str, context: list[str]) -> str:
    prompt = (
    "You are an expert teaching assistant. Only answer the question based on the provided context. "
    "If the answer is not present in the context, say 'I don't know based on the provided material.'\n\n"
    f"Context:\n{chr(10).join(context)}\n\n"
    f"Question: {question}\nAnswer:"
)
    print("🔍 Retrieved context:\n", context)



    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    })

    if response.status_code != 200:
        raise RuntimeError(f"Ollama error: {response.status_code} {response.text}")

    return response.json()["response"].strip()
