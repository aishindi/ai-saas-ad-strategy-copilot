import json
import os
import glob
import matplotlib.pyplot as plt

OUTPUT_DIR = "evaluation_results"
PLOT_DIR = "evaluation_results/plots"


def ensure_plot_dir():
    os.makedirs(PLOT_DIR, exist_ok=True)


def load_latest_file(pattern):
    files = glob.glob(os.path.join(OUTPUT_DIR, pattern))
    if not files:
        print(f"No files found for pattern: {pattern}")
        return None

    latest_file = max(files, key=os.path.getctime)

    with open(latest_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded: {latest_file}")
    return data


def safe_average(values):
    values = [v for v in values if v is not None]
    if not values:
        return 0
    return sum(values) / len(values)


def plot_model_latency(standard_results):
    model_times = {}

    for item in standard_results:
        model = item.get("model")
        response_time = item.get("response_time_sec")

        if model is None or response_time is None:
            continue

        model_times.setdefault(model, []).append(response_time)

    models = list(model_times.keys())
    avg_times = [safe_average(model_times[m]) for m in models]

    plt.figure(figsize=(8, 5))
    plt.bar(models, avg_times)
    plt.title("Average Response Time by Model")
    plt.xlabel("Model")
    plt.ylabel("Average Response Time (sec)")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "model_latency.png"))
    plt.close()


def plot_prompt_strategy_scores(standard_results):
    strategy_scores = {}

    for item in standard_results:
        strategy = item.get("prompt_strategy")
        metrics = item.get("metrics", {})
        total_score = metrics.get("total_score")

        if strategy is None or total_score is None:
            continue

        strategy_scores.setdefault(strategy, []).append(total_score)

    strategies = list(strategy_scores.keys())
    avg_scores = [safe_average(strategy_scores[s]) for s in strategies]

    plt.figure(figsize=(8, 5))
    plt.bar(strategies, avg_scores)
    plt.title("Average Evaluation Score by Prompt Strategy")
    plt.xlabel("Prompt Strategy")
    plt.ylabel("Average Total Score")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "prompt_strategy_scores.png"))
    plt.close()


def plot_cache_comparison(cache_results):
    aggregated = {}

    for item in cache_results:
        model = item.get("model")

        # New field name after fixing cache experiment
        first_call_time = item.get("first_call_time_sec")

        # Backward compatibility with older result files
        if first_call_time is None:
            first_call_time = item.get("uncached_time_sec")

        cached_time = item.get("cached_time_sec")

        if model is None or first_call_time is None or cached_time is None:
            continue

        aggregated.setdefault(model, {"first_call": [], "cached": []})
        aggregated[model]["first_call"].append(first_call_time)
        aggregated[model]["cached"].append(cached_time)

    models = list(aggregated.keys())

    if not models:
        print("No valid cache results found for plotting.")
        return

    first_call_times = [
        safe_average(aggregated[m]["first_call"]) for m in models
    ]

    cached_times = [
        safe_average(aggregated[m]["cached"]) for m in models
    ]

    x = range(len(models))
    width = 0.35

    plt.figure(figsize=(8, 5))
    plt.bar(
        [i - width / 2 for i in x],
        first_call_times,
        width=width,
        label="First Call"
    )
    plt.bar(
        [i + width / 2 for i in x],
        cached_times,
        width=width,
        label="Cached Call"
    )

    plt.xticks(list(x), models)
    plt.title("Cache vs First Call Response Time")
    plt.xlabel("Model")
    plt.ylabel("Average Response Time (sec)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "cache_comparison.png"))
    plt.close()


if __name__ == "__main__":
    ensure_plot_dir()

    standard_results = load_latest_file("standard_results_*.json")
    cache_results = load_latest_file("cache_results_*.json")

    if standard_results:
        plot_model_latency(standard_results)
        plot_prompt_strategy_scores(standard_results)

    if cache_results:
        plot_cache_comparison(cache_results)

    print(f"Plots saved in {PLOT_DIR}")