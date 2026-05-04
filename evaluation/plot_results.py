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
        return None
    latest_file = max(files, key=os.path.getctime)
    with open(latest_file, "r", encoding="utf-8") as f:
        return json.load(f)


def plot_model_latency(standard_results):
    model_times = {}

    for item in standard_results:
        model = item["model"]
        model_times.setdefault(model, []).append(item["response_time_sec"])

    models = list(model_times.keys())
    avg_times = [sum(times) / len(times) for times in model_times.values()]

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
        strategy = item["prompt_strategy"]
        score = item["metrics"]["total_score"]
        strategy_scores.setdefault(strategy, []).append(score)

    strategies = list(strategy_scores.keys())
    avg_scores = [sum(scores) / len(scores) for scores in strategy_scores.values()]

    plt.figure(figsize=(8, 5))
    plt.bar(strategies, avg_scores)
    plt.title("Average Evaluation Score by Prompt Strategy")
    plt.xlabel("Prompt Strategy")
    plt.ylabel("Average Total Score")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "prompt_strategy_scores.png"))
    plt.close()


def plot_cache_comparison(cache_results):
    models = []
    uncached = []
    cached = []

    aggregated = {}

    for item in cache_results:
        model = item["model"]
        aggregated.setdefault(model, {"uncached": [], "cached": []})
        aggregated[model]["uncached"].append(item["uncached_time_sec"])
        aggregated[model]["cached"].append(item["cached_time_sec"])

    for model, vals in aggregated.items():
        models.append(model)
        uncached.append(sum(vals["uncached"]) / len(vals["uncached"]))
        cached.append(sum(vals["cached"]) / len(vals["cached"]))

    x = range(len(models))
    width = 0.35

    plt.figure(figsize=(8, 5))
    plt.bar([i - width / 2 for i in x], uncached, width=width, label="Uncached")
    plt.bar([i + width / 2 for i in x], cached, width=width, label="Cached")
    plt.xticks(list(x), models)
    plt.title("Cache vs No Cache Response Time")
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