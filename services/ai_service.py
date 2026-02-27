import requests
from fastapi import HTTPException

OLLAMA_URL = "http://localhost:11434/api/generate"

def run_model(prompt: str):

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "mistral",   # or llama3
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json()["response"]

    except:
        raise HTTPException(status_code=500, detail="Ollama not running")