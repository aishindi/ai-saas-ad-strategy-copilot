import json
import os
from datetime import datetime

from evaluation.test_queries import TEST_QUERIES
from tools.query_router import route_query
from llm.prompt_chain import generate_strategy_response
from llm.caching import clear_cache

OUTPUT_DIR = "evaluation_results"
MODELS = ["mistral", "llama3"]


def run_cache_experiment():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    results = []

    for model_name in MODELS:
        for query in TEST_QUERIES[:3]:
            print(f"Cache experiment | model={model_name} | query={query[:50]}")

            clear_cache()
            tool_context = route_query(query)

            first_output = generate_strategy_response(
                user_query=query,
                tool_context=tool_context,
                model_name=model_name,
                prompt_strategy="meta",
                use_cache=True
            )

            cached_output = generate_strategy_response(
                user_query=query,
                tool_context=tool_context,
                model_name=model_name,
                prompt_strategy="meta",
                use_cache=True
            )

            results.append({
                "query": query,
                "model": model_name,
                "first_call_time_sec": first_output.get("response_time_sec"),
                "cached_time_sec": cached_output.get("response_time_sec"),
                "first_cached_flag": first_output.get("cached"),
                "second_cached_flag": cached_output.get("cached")
            })

            print("First call:", first_output.get("response_time_sec"), "cached?", first_output.get("cached"))
            print("Second call:", cached_output.get("response_time_sec"), "cached?", cached_output.get("cached"))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(OUTPUT_DIR, f"cache_results_{timestamp}.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Saved cache results to {path}")


if __name__ == "__main__":
    run_cache_experiment()