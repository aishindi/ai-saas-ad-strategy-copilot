def evaluate_response(response_text: str):
    text = response_text.lower()

    score = {
        "non_empty": len(response_text.strip()) > 0,
        "has_summary": "summary" in text,
        "has_recommendation": "recommend" in text or "recommendation" in text,
        "has_next_steps": "next step" in text or "next steps" in text,
        "mentions_data": any(word in text for word in ["roi", "budget", "platform", "audience", "campaign", "cac"]),
        "structured_output": any(word in text for word in ["summary", "recommendation", "findings"]),
    }

    score["total_score"] = sum(int(v) for v in score.values())
    return score