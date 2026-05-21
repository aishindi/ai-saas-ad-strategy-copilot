PASS_THRESHOLD_SCORE = 4
MAX_SCORE = 6


def evaluate_response(response_text: str):
    """Return rule-based evaluation metrics for one LLM response.

    total_score is out of 6.
    accuracy_percent converts that score into a percentage.
    passed is True when total_score >= PASS_THRESHOLD_SCORE.
    """
    response_text = response_text or ""
    text = response_text.lower()

    score = {
        "non_empty": len(response_text.strip()) > 0,
        "has_summary": "summary" in text,
        "has_recommendation": "recommend" in text or "recommendation" in text,
        "has_next_steps": "next step" in text or "next steps" in text,
        "mentions_data": any(
            word in text
            for word in ["roi", "budget", "platform", "audience", "campaign", "cac"]
        ),
        "structured_output": any(
            word in text
            for word in ["summary", "recommendation", "findings"]
        ),
    }

    total_score = sum(int(v) for v in score.values())
    score["total_score"] = total_score
    score["max_score"] = MAX_SCORE
    score["accuracy_percent"] = round((total_score / MAX_SCORE) * 100, 2)
    score["passed"] = total_score >= PASS_THRESHOLD_SCORE
    score["pass_threshold_score"] = PASS_THRESHOLD_SCORE

    return score
