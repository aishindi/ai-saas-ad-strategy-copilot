import json
import time

from llm.prompts import SYSTEM_PROMPT, META_PROMPT_TEMPLATE, SELF_REFLECTION_PROMPT
from llm.model_loader import call_model
from llm.caching import get_cached_response, set_cached_response


def generate_strategy_response(user_query: str, tool_context: dict, model_name: str = "mistral"):
    cache_key = f"{model_name}:{user_query}:{json.dumps(tool_context, sort_keys=True)}"
    cached = get_cached_response(cache_key)

    if cached:
        return {
            "cached": True,
            "response": cached,
            "response_time_sec": 0
        }

    start = time.time()

    # Step 1: Meta prompting
    meta_prompt = META_PROMPT_TEMPLATE.format(
        user_query=user_query,
        tool_context=json.dumps(tool_context, indent=2)
    )
    first_draft = call_model(model_name, SYSTEM_PROMPT + "\n" + meta_prompt)

    # Step 2: Self-reflection
    reflection_prompt = SELF_REFLECTION_PROMPT.format(draft_answer=first_draft)
    final_answer = call_model(model_name, reflection_prompt)

    elapsed = time.time() - start
    set_cached_response(cache_key, final_answer)

    return {
        "cached": False,
        "response": final_answer,
        "response_time_sec": round(elapsed, 3)
    }