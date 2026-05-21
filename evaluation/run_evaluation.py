import csv
import json
import os
from datetime import datetime
from statistics import mean

from evaluation.test_queries import TEST_QUERIES
from evaluation.prompt_injection_tests import PROMPT_INJECTION_TESTS
from tools.query_router import route_query
from llm.prompt_chain import generate_strategy_response
from evaluation.metrics import evaluate_response, MAX_SCORE, PASS_THRESHOLD_SCORE
from llm.caching import clear_cache
from security.guardrails import is_prompt_injection, get_guardrail_response

OUTPUT_DIR = "evaluation_results"
MODELS = ["mistral", "llama3"]
PROMPT_STRATEGIES = ["baseline", "meta", "meta_reflect"]


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_json(filename, data):
    ensure_output_dir()
    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def save_csv(filename, rows, fieldnames):
    ensure_output_dir()
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def print_standard_summary(results):
    print("\n" + "=" * 80)
    print("STANDARD EVALUATION SUMMARY")
    print(f"Pass threshold: {PASS_THRESHOLD_SCORE}/{MAX_SCORE}")
    print("=" * 80)

    for model_name in MODELS:
        model_rows = [r for r in results if r["model"] == model_name]
        if not model_rows:
            continue

        avg_accuracy = mean(r["metrics"]["accuracy_percent"] for r in model_rows)
        pass_rate = mean(1 if r["metrics"]["passed"] else 0 for r in model_rows) * 100
        avg_score = mean(r["metrics"]["total_score"] for r in model_rows)
        avg_latency = mean(
            r["response_time_sec"] for r in model_rows
            if r.get("response_time_sec") is not None
        )

        print(
            f"{model_name}: accuracy={avg_accuracy:.2f}% | "
            f"pass_rate={pass_rate:.2f}% | avg_score={avg_score:.2f}/{MAX_SCORE} | "
            f"avg_latency={avg_latency:.2f}s"
        )

    print("\nBy model + prompt strategy:")
    for model_name in MODELS:
        for prompt_strategy in PROMPT_STRATEGIES:
            rows = [
                r for r in results
                if r["model"] == model_name and r["prompt_strategy"] == prompt_strategy
            ]
            if not rows:
                continue
            avg_accuracy = mean(r["metrics"]["accuracy_percent"] for r in rows)
            pass_rate = mean(1 if r["metrics"]["passed"] else 0 for r in rows) * 100
            avg_score = mean(r["metrics"]["total_score"] for r in rows)
            print(
                f"  {model_name:8s} | {prompt_strategy:12s} | "
                f"accuracy={avg_accuracy:6.2f}% | pass_rate={pass_rate:6.2f}% | "
                f"avg_score={avg_score:.2f}/{MAX_SCORE}"
            )


def build_standard_summary(results):
    model_summary = []
    strategy_summary = []
    model_strategy_summary = []
    query_summary = []

    for model_name in MODELS:
        rows = [r for r in results if r["model"] == model_name]
        if rows:
            model_summary.append({
                "model": model_name,
                "avg_score": round(mean(r["metrics"]["total_score"] for r in rows), 2),
                "accuracy_percent": round(mean(r["metrics"]["accuracy_percent"] for r in rows), 2),
                "pass_rate_percent": round(mean(1 if r["metrics"]["passed"] else 0 for r in rows) * 100, 2),
                "avg_latency_sec": round(mean(r["response_time_sec"] for r in rows if r.get("response_time_sec") is not None), 2),
                "runs": len(rows),
            })

    for prompt_strategy in PROMPT_STRATEGIES:
        rows = [r for r in results if r["prompt_strategy"] == prompt_strategy]
        if rows:
            strategy_summary.append({
                "prompt_strategy": prompt_strategy,
                "avg_score": round(mean(r["metrics"]["total_score"] for r in rows), 2),
                "accuracy_percent": round(mean(r["metrics"]["accuracy_percent"] for r in rows), 2),
                "pass_rate_percent": round(mean(1 if r["metrics"]["passed"] else 0 for r in rows) * 100, 2),
                "runs": len(rows),
            })

    for model_name in MODELS:
        for prompt_strategy in PROMPT_STRATEGIES:
            rows = [
                r for r in results
                if r["model"] == model_name and r["prompt_strategy"] == prompt_strategy
            ]
            if rows:
                model_strategy_summary.append({
                    "model": model_name,
                    "prompt_strategy": prompt_strategy,
                    "avg_score": round(mean(r["metrics"]["total_score"] for r in rows), 2),
                    "accuracy_percent": round(mean(r["metrics"]["accuracy_percent"] for r in rows), 2),
                    "pass_rate_percent": round(mean(1 if r["metrics"]["passed"] else 0 for r in rows) * 100, 2),
                    "runs": len(rows),
                })

    for query_id in range(1, len(TEST_QUERIES) + 1):
        rows = [r for r in results if r["query_id"] == query_id]
        if rows:
            query_summary.append({
                "query_id": query_id,
                "query": rows[0]["query"],
                "avg_score": round(mean(r["metrics"]["total_score"] for r in rows), 2),
                "accuracy_percent": round(mean(r["metrics"]["accuracy_percent"] for r in rows), 2),
                "pass_rate_percent": round(mean(1 if r["metrics"]["passed"] else 0 for r in rows) * 100, 2),
                "runs": len(rows),
            })

    return {
        "model_summary": model_summary,
        "strategy_summary": strategy_summary,
        "model_strategy_summary": model_strategy_summary,
        "query_summary": query_summary,
    }


def save_standard_logs(timestamp, results):
    rows = []
    for item in results:
        metrics = item["metrics"]
        rows.append({
            "query_id": item["query_id"],
            "query": item["query"],
            "model": item["model"],
            "prompt_strategy": item["prompt_strategy"],
            "tool_used": item.get("tool_used"),
            "response_time_sec": item.get("response_time_sec"),
            "total_score": metrics["total_score"],
            "max_score": metrics["max_score"],
            "accuracy_percent": metrics["accuracy_percent"],
            "passed": metrics["passed"],
            "status": "PASS" if metrics["passed"] else "FAIL",
        })

    return save_csv(
        f"query_run_log_{timestamp}.csv",
        rows,
        [
            "query_id", "query", "model", "prompt_strategy", "tool_used",
            "response_time_sec", "total_score", "max_score",
            "accuracy_percent", "passed", "status",
        ],
    )


def save_summary_csvs(timestamp, summary):
    save_csv(
        f"model_summary_{timestamp}.csv",
        summary["model_summary"],
        ["model", "avg_score", "accuracy_percent", "pass_rate_percent", "avg_latency_sec", "runs"],
    )
    save_csv(
        f"strategy_summary_{timestamp}.csv",
        summary["strategy_summary"],
        ["prompt_strategy", "avg_score", "accuracy_percent", "pass_rate_percent", "runs"],
    )
    save_csv(
        f"model_strategy_summary_{timestamp}.csv",
        summary["model_strategy_summary"],
        ["model", "prompt_strategy", "avg_score", "accuracy_percent", "pass_rate_percent", "runs"],
    )
    save_csv(
        f"query_summary_{timestamp}.csv",
        summary["query_summary"],
        ["query_id", "query", "avg_score", "accuracy_percent", "pass_rate_percent", "runs"],
    )


def run_standard_tests():
    results = []
    total_runs = len(MODELS) * len(PROMPT_STRATEGIES) * len(TEST_QUERIES)
    run_number = 0

    print("\n" + "=" * 80)
    print("RUNNING STANDARD EVALUATION")
    print(f"Queries: {len(TEST_QUERIES)} | Models: {MODELS} | Strategies: {PROMPT_STRATEGIES}")
    print(f"Total runs: {total_runs}")
    print("=" * 80)

    for model_name in MODELS:
        for prompt_strategy in PROMPT_STRATEGIES:
            for query_index, query in enumerate(TEST_QUERIES, start=1):
                run_number += 1
                print(
                    f"\n[{run_number}/{total_runs}] Query {query_index}/{len(TEST_QUERIES)} | "
                    f"model={model_name} | strategy={prompt_strategy}"
                )
                print(f"Query: {query}")

                tool_context = route_query(query)

                output = generate_strategy_response(
                    user_query=query,
                    tool_context=tool_context,
                    model_name=model_name,
                    prompt_strategy=prompt_strategy,
                    use_cache=False,
                )

                response_text = output.get("response", "")
                metrics = evaluate_response(response_text)
                status = "PASS" if metrics["passed"] else "FAIL"

                print(
                    f"Result: {status} | score={metrics['total_score']}/{metrics['max_score']} | "
                    f"accuracy={metrics['accuracy_percent']}% | "
                    f"time={output.get('response_time_sec')}s | tool={tool_context.get('tool_used')}"
                )

                results.append({
                    "query_id": query_index,
                    "query": query,
                    "model": model_name,
                    "prompt_strategy": prompt_strategy,
                    "cached": output.get("cached", False),
                    "response_time_sec": output.get("response_time_sec", None),
                    "metrics": metrics,
                    "tool_used": tool_context.get("tool_used"),
                    "response": response_text,
                })

    print_standard_summary(results)
    return results


def run_cache_experiment():
    results = []
    sample_queries = TEST_QUERIES[:5]

    print("\n" + "=" * 80)
    print("RUNNING CACHE EXPERIMENT")
    print(f"Queries: {len(sample_queries)} | Models: {MODELS} | Strategy: meta_reflect")
    print("=" * 80)

    total_runs = len(MODELS) * len(sample_queries)
    run_number = 0

    for model_name in MODELS:
        for query_index, query in enumerate(sample_queries, start=1):
            run_number += 1
            print(f"\n[{run_number}/{total_runs}] Cache test | model={model_name} | query_id={query_index}")
            print(f"Query: {query}")

            clear_cache()
            tool_context = route_query(query)

            first_output = generate_strategy_response(
                user_query=query,
                tool_context=tool_context,
                model_name=model_name,
                prompt_strategy="meta_reflect",
                use_cache=True,
            )

            cached_output = generate_strategy_response(
                user_query=query,
                tool_context=tool_context,
                model_name=model_name,
                prompt_strategy="meta_reflect",
                use_cache=True,
            )

            passed = cached_output.get("cached", False) is True
            print(
                f"Cache result: {'PASS' if passed else 'FAIL'} | "
                f"first={first_output.get('response_time_sec')}s | "
                f"second={cached_output.get('response_time_sec')}s | "
                f"cached_flag={cached_output.get('cached', False)}"
            )

            results.append({
                "query_id": query_index,
                "query": query,
                "model": model_name,
                "first_call_time_sec": first_output.get("response_time_sec", None),
                "cached_time_sec": cached_output.get("response_time_sec", None),
                "first_cached_flag": first_output.get("cached", False),
                "cached_flag": cached_output.get("cached", False),
                "passed": passed,
            })

    return results


def run_security_tests():
    results = []

    print("\n" + "=" * 80)
    print("RUNNING SECURITY / PROMPT INJECTION TESTS")
    print(f"Attack queries: {len(PROMPT_INJECTION_TESTS)} | Models: {MODELS}")
    print("=" * 80)

    total_runs = len(MODELS) * len(PROMPT_INJECTION_TESTS)
    run_number = 0

    for model_name in MODELS:
        for attack_id, query in enumerate(PROMPT_INJECTION_TESTS, start=1):
            run_number += 1
            print(f"\n[{run_number}/{total_runs}] Security test {attack_id} | model={model_name}")
            print(f"Attack query: {query}")

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
                    use_cache=False,
                )
                tool_used = tool_context.get("tool_used")

            blocked = output["prompt_strategy"] == "guardrail_block"
            print(f"Security result: {'PASS' if blocked else 'FAIL'} | blocked={blocked} | tool={tool_used}")

            results.append({
                "attack_id": attack_id,
                "attack_query": query,
                "model": model_name,
                "tool_used": tool_used,
                "blocked": blocked,
                "passed": blocked,
                "response_time_sec": output.get("response_time_sec", None),
                "response": output["response"],
            })

    return results


if __name__ == "__main__":
    ensure_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    standard_results = run_standard_tests()
    save_json(f"standard_results_{timestamp}.json", standard_results)
    log_path = save_standard_logs(timestamp, standard_results)
    summary = build_standard_summary(standard_results)
    save_json(f"evaluation_summary_{timestamp}.json", summary)
    save_summary_csvs(timestamp, summary)
    print(f"\nSaved query run log: {log_path}")

    cache_results = run_cache_experiment()
    save_json(f"cache_results_{timestamp}.json", cache_results)

    security_results = run_security_tests()
    save_json(f"security_results_{timestamp}.json", security_results)

    print("\n" + "=" * 80)
    print(f"All evaluation files saved in: {OUTPUT_DIR}")
    print("Generated files include:")
    print(f"  standard_results_{timestamp}.json")
    print(f"  query_run_log_{timestamp}.csv")
    print(f"  evaluation_summary_{timestamp}.json")
    print(f"  model_summary_{timestamp}.csv")
    print(f"  strategy_summary_{timestamp}.csv")
    print(f"  model_strategy_summary_{timestamp}.csv")
    print(f"  query_summary_{timestamp}.csv")
    print(f"  cache_results_{timestamp}.json")
    print(f"  security_results_{timestamp}.json")
    print("=" * 80)
