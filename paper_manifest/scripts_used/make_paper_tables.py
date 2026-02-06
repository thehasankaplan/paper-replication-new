#!/usr/bin/env python3
import argparse, os, math
import pandas as pd

def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1.0 + (z*z)/n
    center = (p + (z*z)/(2*n)) / denom
    half = (z * math.sqrt((p*(1-p)/n) + (z*z)/(4*n*n))) / denom
    return (max(0.0, center-half), min(1.0, center+half))

def fmt_pct(x):
    return f"{100.0*x:.2f}\\%"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--overall", required=True, help="model_overall.csv")
    ap.add_argument("--matrix", required=True, help="model_variant_matrix.csv")
    ap.add_argument("--out_dir", required=True)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    overall = pd.read_csv(args.overall)
    mat = pd.read_csv(args.matrix)

    # overall with CI
    lows, highs = [], []
    for _, r in overall.iterrows():
        lo, hi = wilson(int(r["attack_success_total"]), int(r["valid_pairs_total"]))
        lows.append(lo); highs.append(hi)
    overall["asr_low"] = lows
    overall["asr_high"] = highs
    overall_out = os.path.join(args.out_dir, "model_overall_with_ci.csv")
    overall.to_csv(overall_out, index=False)

    # per-variant with CI
    v_lows, v_highs = [], []
    for _, r in mat.iterrows():
        lo, hi = wilson(int(r["attack_success_pairs"]), int(r["valid_pairs"]))
        v_lows.append(lo); v_highs.append(hi)
    mat["asr_low"] = v_lows
    mat["asr_high"] = v_highs
    mat_out = os.path.join(args.out_dir, "model_variant_matrix_with_ci.csv")
    mat.to_csv(mat_out, index=False)

    # pivot ASR table
    pivot = mat.pivot_table(index="variant", columns="model_id", values="asr_semantic", aggfunc="first").fillna(0.0)
    pivot_out = os.path.join(args.out_dir, "asr_pivot.csv")
    pivot.to_csv(pivot_out)

    # LaTeX tables
    # Overall table
    lines = []
    lines.append("\\begin{tabular}{lrrr}")
    lines.append("\\toprule")
    lines.append("Model & Valid Pairs & Successes & ASR (95\\% CI) \\\\")
    lines.append("\\midrule")
    for _, r in overall.iterrows():
        model = r["model_id"]
        n = int(r["valid_pairs_total"])
        k = int(r["attack_success_total"])
        asr = float(r["asr_weighted"])
        lo = float(r["asr_low"])
        hi = float(r["asr_high"])
        lines.append(f"{model} & {n} & {k} & {fmt_pct(asr)} [{fmt_pct(lo)}, {fmt_pct(hi)}] \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    with open(os.path.join(args.out_dir, "table_overall.tex"), "w") as f:
        f.write("\n".join(lines) + "\n")

    # Variant table (ASR only)
    vlines = []
    vlines.append("\\begin{tabular}{l" + "r"*len(pivot.columns) + "}")
    vlines.append("\\toprule")
    header = "Variant & " + " & ".join(pivot.columns) + " \\\\"
    vlines.append(header)
    vlines.append("\\midrule")
    for var in pivot.index:
        row = [fmt_pct(float(pivot.loc[var, c])) for c in pivot.columns]
        vlines.append(var + " & " + " & ".join(row) + " \\\\")
    vlines.append("\\bottomrule")
    vlines.append("\\end{tabular}")
    with open(os.path.join(args.out_dir, "table_variants_asr.tex"), "w") as f:
        f.write("\n".join(vlines) + "\n")

    print("[write]", overall_out)
    print("[write]", mat_out)
    print("[write]", pivot_out)
    print("[write]", os.path.join(args.out_dir, "table_overall.tex"))
    print("[write]", os.path.join(args.out_dir, "table_variants_asr.tex"))

if __name__ == "__main__":
    main()
