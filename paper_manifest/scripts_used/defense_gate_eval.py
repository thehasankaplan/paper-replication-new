#!/usr/bin/env python3
import argparse, os
import pandas as pd

def parse_set(s):
    if pd.isna(s) or str(s).strip()=="":
        return set()
    return set(x.strip().lower() for x in str(s).split(",") if x.strip())

def parse_expected(s):
    if pd.isna(s) or str(s).strip()=="":
        return set()
    t=str(s).strip()
    if t.startswith("[") and t.endswith("]"):
        # best-effort list parsing without eval complexity
        t=t.strip("[]")
    return set(x.strip().strip("'\"").lower() for x in t.split(",") if x.strip())

def accept_row(r, prefix):
    if not bool(r[f"{prefix}_ok"]):
        return False
    if bool(r[f"{prefix}_overperm"]):
        return False
    exp = parse_expected(r["expected_actions"])
    acts = parse_set(r.get(f"{prefix}_actions",""))
    # must include all expected actions (no under-permission)
    if len(exp - acts) != 0:
        return False
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out_csv", required=True)
    args = ap.parse_args()

    df = pd.read_csv(os.path.join(args.run, "pairwise_semantic.csv"))
    df["ctrl_accept"] = df.apply(lambda r: accept_row(r,"ctrl"), axis=1)
    df["poi_accept"]  = df.apply(lambda r: accept_row(r,"poi"), axis=1)

    # Summarize by variant
    rows = []
    for v, g in df.groupby("variant"):
        rows.append({
            "variant": v,
            "pairs": len(g),
            "ctrl_accept_rate": g["ctrl_accept"].mean(),
            "poi_accept_rate": g["poi_accept"].mean(),
            "poi_reject_rate": 1.0 - g["poi_accept"].mean(),
            "attack_success_rate_raw": g["attack_success"].mean(),
        })
    out = pd.DataFrame(rows).sort_values("variant")
    os.makedirs(os.path.dirname(args.out_csv), exist_ok=True)
    out.to_csv(args.out_csv, index=False)
    print("[write]", args.out_csv)

if __name__ == "__main__":
    main()
