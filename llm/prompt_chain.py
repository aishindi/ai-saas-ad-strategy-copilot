import json
import time

from llm.prompts import (
    SYSTEM_PROMPT,
    BASELINE_PROMPT_TEMPLATE,
    META_PROMPT_TEMPLATE,
    SELF_REFLECTION_PROMPT,
)
from llm.model_loader import call_model
from llm.caching import get_cached_response, set_cached_response


def generate_strategy_response(
    user_query: str,
    tool_context: dict,
    model_name: str = "mistral",
    prompt_strategy: str = "meta",
    use_cache: bool = True,
):
    """
    prompt_strategy:
    - baseline
    - meta
    - self_reflect
    """
    cache_key = f"{model_name}:{prompt_strategy}:{user_query}:{json.dumps(tool_context, sort_keys=True)}"

    if use_cache:
        cached = get_cached_response(cache_key)
        if cached:
            return {
                "cached": True,
                "response": cached,
                "response_time_sec": 0.0,
                "prompt_strategy": prompt_strategy,
                "model_name": model_name,
            }

    start = time.time()

    tool_context_str = json.dumps(tool_context, indent=2)

    if prompt_strategy == "baseline":
        prompt = SYSTEM_PROMPT + "\n" + BASELINE_PROMPT_TEMPLATE.format(
            user_query=user_query,
            tool_context=tool_context_str,
        )
        final_answer = call_model(model_name, prompt)

    elif prompt_strategy == "meta":
        prompt = SYSTEM_PROMPT + "\n" + META_PROMPT_TEMPLATE.format(
            user_query=user_query,
            tool_context=tool_context_str,
        )
        final_answer = call_model(model_name, prompt)

    elif prompt_strategy == "self_reflect":
        first_prompt = SYSTEM_PROMPT + "\n" + META_PROMPT_TEMPLATE.format(
            user_query=user_query,
            tool_context=tool_context_str,
        )
        first_draft = call_model(model_name, first_prompt)

        reflection_prompt = SELF_REFLECTION_PROMPT.format(
            user_query=user_query,
            tool_context=json.dumps(tool_context, indent=2),
            draft_answer=first_draft
        )
        final_answer = call_model(model_name, reflection_prompt)

    else:
        final_answer = "Invalid prompt strategy selected."

    elapsed = round(time.time() - start, 3)

    result = {
        "cached": False,
        "response": final_answer,
        "response_time_sec": elapsed,
        "prompt_strategy": prompt_strategy,
        "model_name": model_name,
    }

    if use_cache:
        set_cached_response(cache_key, result["response"])

    return result