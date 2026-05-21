import glob
import json
import os
from statistics import mean

OUTPUT_DIR = "evaluation_results"


def latest_file(pattern):
    files = glob.glob(os.path.join(OUTPUT_DIR, pattern))
    if not files:
        raise FileNotFoundError(f"No files found for {pattern}")
    return max(files, key=os.path.getmtime)


def summarize():
    standard_file = latest_file("standard_results_*.json")

    with open(standard_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded: {standard_file}")

    models = sorted(set(item["model"] for item in data))
    strategies = sorted(set(item["prompt_strategy"] for item in data))

    print("\nModel Summary")
    print("model | avg_score | accuracy_percent | pass_rate_percent | avg_latency_sec | runs")
    for model in models:
        rows = [item for item in data if item["model"] == model]
        avg_score = mean(item["metrics"]["total_score"] for item in rows)
        accuracy = mean(item["metrics"]["accuracy_percent"] for item in rows)
        pass_rate = mean(1 if item["metrics"]["passed"] else 0 for item in rows) * 100
        latency_rows = [item["response_time_sec"] for item in rows if item.get("response_time_sec") is not None]
        avg_latency = mean(latency_rows) if latency_rows else 0
        print(f"{model} | {avg_score:.2f} | {accuracy:.2f}% | {pass_rate:.2f}% | {avg_latency:.2f} | {len(rows)}")

    print("\nPrompt Strategy Summary")
    print("strategy | avg_score | accuracy_percent | pass_rate_percent | runs")
    for strategy in strategies:
        rows = [item for item in data if item["prompt_strategy"] == strategy]
        avg_score = mean(item["metrics"]["total_score"] for item in rows)
        accuracy = mean(item["metrics"]["accuracy_percent"] for item in rows)
        pass_rate = mean(1 if item["metrics"]["passed"] else 0 for item in rows) * 100
        print(f"{strategy} | {avg_score:.2f} | {accuracy:.2f}% | {pass_rate:.2f}% | {len(rows)}")

    print("\nModel + Strategy Summary")
    print("model | strategy | avg_score | accuracy_percent | pass_rate_percent | runs")
    for model in models:
        for strategy in strategies:
            rows = [
                item for item in data
                if item["model"] == model and item["prompt_strategy"] == strategy
            ]
            if not rows:
                continue
            avg_score = mean(item["metrics"]["total_score"] for item in rows)
            accuracy = mean(item["metrics"]["accuracy_percent"] for item in rows)
            pass_rate = mean(1 if item["metrics"]["passed"] else 0 for item in rows) * 100
            print(f"{model} | {strategy} | {avg_score:.2f} | {accuracy:.2f}% | {pass_rate:.2f}% | {len(rows)}")


if __name__ == "__main__":
    summarize()
