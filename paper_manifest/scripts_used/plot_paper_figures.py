#!/usr/bin/env python3
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def plot_overall_with_ci(overall_csv: Path, outpath: Path, title: str):
    df = pd.read_csv(overall_csv)

    # Required
    if "model_id" not in df.columns:
        raise ValueError(f"{overall_csv} missing model_id column")
    if "asr_weighted" not in df.columns:
        raise ValueError(f"{overall_csv} missing asr_weighted column")

    # Optional CI
    has_ci = ("asr_low" in df.columns) and ("asr_high" in df.columns)

    df = df.sort_values("asr_weighted", ascending=False).reset_index(drop=True)

    x = df["model_id"].astype(str).tolist()
    y = df["asr_weighted"].astype(float).to_numpy()

    plt.figure(figsize=(9, 3.6))

    if has_ci:
        low = df["asr_low"].astype(float).to_numpy()
        high = df["asr_high"].astype(float).to_numpy()
        yerr = np.vstack([y - low, high - y])
        plt.bar(x, y, yerr=yerr, capsize=3)
    else:
        plt.bar(x, y)

    plt.xticks(rotation=20, ha="right")
    plt.ylabel("ASR (semantic)")
    plt.title(title)
    plt.tight_layout()
    outpath.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(outpath)
    plt.close()


def plot_variant_heatmap(matrix_csv: Path, outpath: Path, title: str):
    df = pd.read_csv(matrix_csv)

    required = {"model_id", "variant", "asr_semantic"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{matrix_csv} missing columns: {sorted(missing)}")

    order = [
        "baseline",
        "broad_star",
        "json_seed_above",
        "precedence_takeover",
        "resource_star",
        "role_override",
        "service_wildcard",
    ]

    piv = (
        df.pivot_table(index="model_id", columns="variant", values="asr_semantic", aggfunc="mean")
        .fillna(0.0)
    )

    # Keep stable column order if present
    cols = [c for c in order if c in piv.columns]
    piv = piv[cols]

    plt.figure(figsize=(10, 3.6))
    im = plt.imshow(piv.values, aspect="auto")

    plt.yticks(range(len(piv.index)), [str(m) for m in piv.index])
    plt.xticks(range(len(piv.columns)), [str(v) for v in piv.columns], rotation=20, ha="right")

    plt.colorbar(im)
    plt.title(title)
    plt.tight_layout()
    outpath.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(outpath)
    plt.close()


def plot_stealth_derailment(stealth_csv: Path, outpath: Path, title: str):
    df = pd.read_csv(stealth_csv)

    required = {"model_id", "poi_stealth_rate", "poi_derailment_rate"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{stealth_csv} missing columns: {sorted(missing)}")

    df = df.sort_values("poi_stealth_rate", ascending=False).reset_index(drop=True)

    x = df["model_id"].astype(str).tolist()
    stealth = df["poi_stealth_rate"].astype(float).to_numpy()
    derail = df["poi_derailment_rate"].astype(float).to_numpy()

    plt.figure(figsize=(9, 3.6))
    plt.bar(x, stealth, label="stealth")
    plt.bar(x, derail, bottom=stealth, label="derailment")

    plt.xticks(rotation=20, ha="right")
    plt.ylabel("Rate")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    outpath.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(outpath)
    plt.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--overall_with_ci", type=Path, required=True)
    ap.add_argument("--variant_matrix", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--title_prefix", type=str, required=True)
    ap.add_argument("--stealth_csv", type=Path, default=None)
    args = ap.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)

    plot_overall_with_ci(
        args.overall_with_ci,
        args.outdir / "overall_asr_with_ci.pdf",
        f"{args.title_prefix} — Overall ASR (with CI)",
    )

    plot_variant_heatmap(
        args.variant_matrix,
        args.outdir / "variant_asr_heatmap.pdf",
        f"{args.title_prefix} — ASR by Variant",
    )

    if args.stealth_csv is not None:
        plot_stealth_derailment(
            args.stealth_csv,
            args.outdir / "stealth_vs_derailment.pdf",
            f"{args.title_prefix} — Stealth vs Derailment",
        )


if __name__ == "__main__":
    main()
