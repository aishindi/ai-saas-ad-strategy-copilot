import json
import time

from llm.model_loader import call_model
from llm.prompts import (
    SYSTEM_PROMPT,
    BASELINE_PROMPT_TEMPLATE,
    META_PROMPT_TEMPLATE,
    SELF_REFLECTION_PROMPT,
)
from llm.caching import get_cached_response, set_cached_response


def normalize_query(query: str) -> str:
    return " ".join(query.lower().strip().split())


def build_cache_key(model_name: str, prompt_strategy: str, user_query: str) -> str:
    normalized = normalize_query(user_query)
    return f"{model_name}:{prompt_strategy}:{normalized}"


def generate_strategy_response(
    user_query: str,
    tool_context: dict,
    model_name: str = "mistral",
    prompt_strategy: str = "meta_reflect",
    use_cache: bool = True
):
    start_time = time.time()

    cache_key = build_cache_key(model_name, prompt_strategy, user_query)

    if use_cache:
        cached_response = get_cached_response(cache_key)
        if cached_response is not None:
            return {
                "cached": True,
                "response": cached_response,
                "response_time_sec": 0.0,
                "prompt_strategy": prompt_strategy,
                "model_name": model_name
            }

    tool_context_str = json.dumps(tool_context, indent=2)

    if prompt_strategy == "baseline":
        prompt = SYSTEM_PROMPT + "\n\n" + BASELINE_PROMPT_TEMPLATE.format(
            user_query=user_query,
            tool_context=tool_context_str
        )

        final_answer = call_model(model_name, prompt)

    elif prompt_strategy == "meta":
        prompt = SYSTEM_PROMPT + "\n\n" + META_PROMPT_TEMPLATE.format(
            user_query=user_query,
            tool_context=tool_context_str
        )

        final_answer = call_model(model_name, prompt)

    elif prompt_strategy == "meta_reflect":
        draft_prompt = SYSTEM_PROMPT + "\n\n" + META_PROMPT_TEMPLATE.format(
            user_query=user_query,
            tool_context=tool_context_str
        )

        first_draft = call_model(model_name, draft_prompt)

        reflection_prompt = SYSTEM_PROMPT + "\n\n" + SELF_REFLECTION_PROMPT.format(
            user_query=user_query,
            tool_context=tool_context_str,
            draft_answer=first_draft
        )

        final_answer = call_model(model_name, reflection_prompt)

    else:
        prompt = SYSTEM_PROMPT + "\n\n" + META_PROMPT_TEMPLATE.format(
            user_query=user_query,
            tool_context=tool_context_str
        )

        final_answer = call_model(model_name, prompt)

    if use_cache:
        set_cached_response(cache_key, final_answer)

    end_time = time.time()

    return {
        "cached": False,
        "response": final_answer,
        "response_time_sec": round(end_time - start_time, 3),
        "prompt_strategy": prompt_strategy,
        "model_name": model_name
    }