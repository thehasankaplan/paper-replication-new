#!/usr/bin/env python3
import argparse, os
import pandas as pd

def read_run(run_dir: str) -> pd.DataFrame:
    vs_path = os.path.join(run_dir, "variant_semantic.csv")
    ps_path = os.path.join(run_dir, "per_sample.csv")

    if not os.path.exists(vs_path):
        raise FileNotFoundError(f"Missing {vs_path} (run postprocess_run.sh first)")
    if not os.path.exists(ps_path):
        raise FileNotFoundError(f"Missing {ps_path}")

    vs = pd.read_csv(vs_path)
    ps = pd.read_csv(ps_path)

    model_id = str(ps["model_id"].dropna().iloc[0]) if "model_id" in ps.columns else "UNKNOWN"
    provider = str(ps["provider"].dropna().iloc[0]) if "provider" in ps.columns else "UNKNOWN"

    vs.insert(0, "run_dir", run_dir)
    vs.insert(1, "model_id", model_id)
    vs.insert(2, "provider", provider)
    return vs

def overall_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (model_id, provider), g in df.groupby(["model_id", "provider"]):
        valid = g["valid_pairs"].sum()
        succ  = g["attack_success_pairs"].sum()
        ctrl_ff = g["ctrl_format_fail"].sum()
        poi_ff  = g["poi_format_fail"].sum()
        rows.append({
            "model_id": model_id,
            "provider": provider,
            "valid_pairs_total": int(valid),
            "attack_success_total": int(succ),
            "asr_weighted": (succ/valid) if valid else 0.0,
            "ctrl_format_fail_total": int(ctrl_ff),
            "poi_format_fail_total": int(poi_ff),
        })
    return pd.DataFrame(rows).sort_values(["provider","model_id"])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--out_matrix", default="results/model_variant_matrix.csv")
    ap.add_argument("--out_overall", default="results/model_overall.csv")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out_matrix), exist_ok=True)

    parts = [read_run(r) for r in args.runs]
    df = pd.concat(parts, ignore_index=True)

    df.to_csv(args.out_matrix, index=False)

    ov = overall_summary(df)
    ov.to_csv(args.out_overall, index=False)

    print("[write]", args.out_matrix)
    print("[write]", args.out_overall)
    print("\nOverall:")
    print(ov.to_string(index=False))

if __name__ == "__main__":
    main()
