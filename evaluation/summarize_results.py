import json
import glob
import os
import pandas as pd

OUTPUT_DIR = "evaluation_results"


def latest_file(pattern):
    files = glob.glob(os.path.join(OUTPUT_DIR, pattern))
    if not files:
        raise FileNotFoundError(f"No files found for {pattern}")
    return max(files, key=os.path.getctime)


standard_file = latest_file("standard_results_*.json")

with open(standard_file, "r", encoding="utf-8") as f:
    data = json.load(f)

rows = []

for item in data:
    rows.append({
        "model": item["model"],
        "prompt_strategy": item["prompt_strategy"],
        "response_time_sec": item["response_time_sec"],
        "total_score": item["metrics"]["total_score"],
        "accuracy_percent": round((item["metrics"]["total_score"] / 6) * 100, 2),
    })

df = pd.DataFrame(rows)

model_summary = df.groupby("model").agg(
    avg_score=("total_score", "mean"),
    accuracy_percent=("accuracy_percent", "mean"),
    avg_latency=("response_time_sec", "mean")
).reset_index()

strategy_summary = df.groupby("prompt_strategy").agg(
    avg_score=("total_score", "mean"),
    accuracy_percent=("accuracy_percent", "mean"),
    avg_latency=("response_time_sec", "mean")
).reset_index()

model_strategy_summary = df.groupby(["model", "prompt_strategy"]).agg(
    avg_score=("total_score", "mean"),
    accuracy_percent=("accuracy_percent", "mean"),
    avg_latency=("response_time_sec", "mean")
).reset_index()

print("\nModel Summary")
print(model_summary)

print("\nPrompt Strategy Summary")
print(strategy_summary)

print("\nModel + Strategy Summary")
print(model_strategy_summary)

model_summary.to_csv(os.path.join(OUTPUT_DIR, "model_summary.csv"), index=False)
strategy_summary.to_csv(os.path.join(OUTPUT_DIR, "strategy_summary.csv"), index=False)
model_strategy_summary.to_csv(os.path.join(OUTPUT_DIR, "model_strategy_summary.csv"), index=False)

print("\nSaved CSV summaries in evaluation_results/")