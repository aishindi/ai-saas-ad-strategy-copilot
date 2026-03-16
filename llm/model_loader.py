def call_model(model_name: str, prompt: str) -> str:
    """
    Placeholder model call.
    Replace later with Ollama or Hugging Face inference.
    """
    return f"[{model_name}] Generated response based on prompt:\n{prompt[:1000]}"


# If you use Ollama later, replace with something like:

# import ollama
#
# def call_model(model_name: str, prompt: str) -> str:
#     response = ollama.chat(
#         model=model_name,
#         messages=[{"role": "user", "content": prompt}]
#     )
#     return response["message"]["content"]
