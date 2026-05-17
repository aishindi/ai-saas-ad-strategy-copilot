import json
import os
from datetime import datetime

from evaluation.test_queries import TEST_QUERIES
from evaluation.prompt_injection_tests import PROMPT_INJECTION_TESTS
from tools.query_router import route_query
from llm.prompt_chain import generate_strategy_response
from evaluation.metrics import evaluate_response
from llm.caching import clear_cache
from security.guardrails import is_prompt_injection, get_guardrail_response

OUTPUT_DIR = "evaluation_results"
MODELS = ["mistral", "llama3"]
PROMPT_STRATEGIES = ["baseline", "meta", "meta_reflect"]


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def run_standard_tests():
    results = []

    for model_name in MODELS:
        for prompt_strategy in PROMPT_STRATEGIES:
            for query in TEST_QUERIES:
                tool_context = route_query(query)

                output = generate_strategy_response(
                    user_query=query,
                    tool_context=tool_context,
                    model_name=model_name,
                    prompt_strategy=prompt_strategy,
                    use_cache=False
                )

                response_text = output["response"]
                metrics = evaluate_response(response_text)

                results.append({
                    "query": query,
                    "model": model_name,
                    "prompt_strategy": prompt_strategy,
                    "cached": output.get("cached", False),
                    "response_time_sec": output.get("response_time_sec", None),
                    "metrics": metrics,
                    "tool_used": tool_context.get("tool_used"),
                    "response": response_text
                })

    return results


def run_cache_experiment():
    results = []

    sample_queries = TEST_QUERIES[:5]

    for model_name in MODELS:
        for query in sample_queries:
            clear_cache()

            tool_context = route_query(query)

            first_output = generate_strategy_response(
                user_query=query,
                tool_context=tool_context,
                model_name=model_name,
                prompt_strategy="meta_reflect",
                use_cache=True
            )

            cached_output = generate_strategy_response(
                user_query=query,
                tool_context=tool_context,
                model_name=model_name,
                prompt_strategy="meta_reflect",
                use_cache=True
            )

            results.append({
                "query": query,
                "model": model_name,
                "first_call_time_sec": first_output.get("response_time_sec", None),
                "cached_time_sec": cached_output.get("response_time_sec", None),
                "cached_flag": cached_output.get("cached", False)
            })

    return results


def run_security_tests():
    results = []

    for model_name in MODELS:
        for query in PROMPT_INJECTION_TESTS:
            if is_prompt_injection(query):
                output = get_guardrail_response()
                tool_used = "guardrail"
            else:
                tool_context = route_query(query)

                output = generate_strategy_response(
                    user_query=query,
                    tool_context=tool_context,
                    model_name=model_name,
                    prompt_strategy="meta_reflect",
                    use_cache=False
                )
                tool_used = tool_context.get("tool_used")

            results.append({
                "attack_query": query,
                "model": model_name,
                "tool_used": tool_used,
                "blocked": output["prompt_strategy"] == "guardrail_block",
                "response_time_sec": output.get("response_time_sec", None),
                "response": output["response"]
            })

    return results


def save_json(filename, data):
    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    ensure_output_dir()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("Running standard evaluation...")
    standard_results = run_standard_tests()
    save_json(f"standard_results_{timestamp}.json", standard_results)

    print("Running cache experiment...")
    cache_results = run_cache_experiment()
    save_json(f"cache_results_{timestamp}.json", cache_results)

    print("Running security tests...")
    security_results = run_security_tests()
    save_json(f"security_results_{timestamp}.json", security_results)

    print(f"All evaluation files saved in: {OUTPUT_DIR}")