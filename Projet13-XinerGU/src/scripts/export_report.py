import os, glob, pandas as pd
import matplotlib.pyplot as plt
from auditor.scoring import aggregate

RUN_DIR = "data/results/runs"
REPORT_DIR = "data/results/reports"

def latest_run():
    files = sorted(glob.glob(os.path.join(RUN_DIR, "run_*.csv")))
    return files[-1] if files else None

def plot_group_metrics(agg_df, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    metrics = ["sentiment","refusal","length","hedge_ratio","negative"]
    for m in metrics:
        plt.figure()
        plt.bar(agg_df["group"], agg_df[m])
        plt.title(f"Group mean - {m}")
        plt.xticks(rotation=15)
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, f"{m}.png"))
        plt.close()

def plot_distributions(df, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    metrics = ["sentiment","length","hedge_ratio"]
    for m in metrics:
        plt.figure()
        plt.hist(df[m].dropna(), bins=20)
        plt.title(f"Distribution of {m}")
        plt.xlabel(m); plt.ylabel("count")
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, f"dist_{m}.png"))
        plt.close()

def main():
    path = latest_run()
    if not path:
        raise SystemExit("No run files found. Please run src/scripts/run_all.py first.")
    df = pd.read_csv(path)
    agg_df = aggregate(df)
    save_dir = os.path.join(REPORT_DIR, os.path.basename(path).replace(".csv",""))
    plot_group_metrics(agg_df, save_dir)
    plot_distributions(df, save_dir)
    print("Report saved to:", save_dir)

if __name__ == "__main__":
    main()
