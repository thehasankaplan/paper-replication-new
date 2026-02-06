#!/usr/bin/env python3
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def plot(csv_path: Path, outpath: Path, title: str):
    df = pd.read_csv(csv_path)
    df = df.sort_values("stealth_rate", ascending=False).reset_index(drop=True)

    x = df["model_id"].astype(str).tolist()
    stealth = df["stealth_rate"].astype(float).to_numpy()
    derail  = df["derail_rate"].astype(float).to_numpy()

    plt.figure(figsize=(9, 3.6))
    plt.bar(x, stealth, label="Stealth (over-permission without full derail)")
    plt.bar(x, derail, bottom=stealth, label="Derailment (hard pivot / wildcard)")

    plt.xticks(rotation=25, ha="right")
    plt.ylabel("Rate (per valid pair)")
    plt.title(title)
    plt.legend(fontsize=8)
    plt.tight_layout()

    outpath.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(outpath)
    plt.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", required=True)
    args = ap.parse_args()

    plot(Path(args.csv), Path(args.out), args.title)

if __name__ == "__main__":
    main()
