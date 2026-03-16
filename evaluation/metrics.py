def evaluate_response(response_text: str):
    score = {
        "has_recommendation": "recommend" in response_text.lower(),
        "mentions_data": any(word in response_text.lower() for word in ["roi", "budget", "platform", "audience"]),
        "non_empty": len(response_text.strip()) > 0
    }
    return score