import os
import json
import requests


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_MODE = os.getenv("MODEL_MODE", "ollama")  # ollama or mock


def call_ollama_model(model_name: str, prompt: str) -> str:
    """
    Calls a local Ollama model.
    Example model names:
    - mistral
    - llama3
    """
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except Exception as e:
        return f"[OLLAMA ERROR] {str(e)}"


def call_mock_model(model_name: str, prompt: str) -> str:
    """
    Fallback model for development if Ollama is not available.
    """
    return (
        f"[MOCK MODEL: {model_name}]\n"
        f"This is a mock generated response.\n\n"
        f"Prompt Preview:\n{prompt[:1200]}"
    )


def call_model(model_name: str, prompt: str) -> str:
    mode = MODEL_MODE.lower()

    if mode == "ollama":
        return call_ollama_model(model_name, prompt)

    return call_mock_model(model_name, prompt)