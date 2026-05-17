# security/guardrails.py

import re


BLOCKED_PATTERNS = [
    r"ignore (all )?(previous|prior) instructions",
    r"reveal.*system prompt",
    r"show.*system prompt",
    r"tell me.*system prompt",
    r"print.*system prompt",
    r"hidden prompt",
    r"developer message",
    r"system message",
    r"internal instructions",
    r"backend settings",
    r"internal configuration",
    r"cached prompts",
    r"forget.*instructions",
    r"act as.*hacker",
    r"you are now",
    r"override.*instructions",
    r"bypass.*rules",
]


SAFE_REFUSAL = """
I cannot reveal or modify internal system instructions, hidden prompts, backend settings, or security rules.

I can still help with SaaS advertising strategy questions using the available campaign data and tool context. For example, you can ask about budget allocation, audience targeting, ROI, CAC, platform comparison, or competitor trends.
"""


def is_prompt_injection(query: str) -> bool:
    query_lower = query.lower()

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, query_lower):
            return True

    return False


def get_guardrail_response():
    return {
        "cached": False,
        "response": SAFE_REFUSAL.strip(),
        "response_time_sec": 0.0,
        "prompt_strategy": "guardrail_block",
        "model_name": "none"
    }