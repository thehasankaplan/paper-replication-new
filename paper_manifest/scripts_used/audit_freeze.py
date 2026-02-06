
import os, glob, csv, sys, json
from typing import List, Dict

try:
    import yaml  # PyYAML
except Exception:
    yaml = None

FREEZE_DIR = os.environ.get("FREEZE_DIR")
if not FREEZE_DIR or not os.path.isdir(FREEZE_DIR):
    print("[audit] ERROR: FREEZE_DIR is not set or does not exist.", file=sys.stderr)
    sys.exit(2)

reports_dir = os.path.join(FREEZE_DIR, "reports")
os.makedirs(reports_dir, exist_ok=True)

summary_path = os.path.join(FREEZE_DIR, "audit_summary.csv")
invalid_path = os.path.join(FREEZE_DIR, "invalid_runs.txt")
empty_report = os.path.join(reports_dir, "_empty_raw_report.csv")
error_report = os.path.join(reports_dir, "_error_stub_report.csv")

def read_yaml(path: str) -> Dict:
    if not yaml:
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

def read_poisoned_expected_count(per_sample_csv: str) -> int:
    if not os.path.exists(per_sample_csv):
        return -1
    n = 0
    try:
        with open(per_sample_csv, "r", encoding="utf-8", newline="") as f:
            r = csv.DictReader(f)
            for row in r:
                v = str(row.get("is_poisoned", "")).strip().lower()
                if v in ("true", "1", "yes"):
                    n += 1
    except Exception:
        return -1
    return n

def file_contains_error_stub(path: str) -> bool:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            chunk = f.read(200_000)  # scan first 200 KB
        return "[ERROR]" in chunk
    except Exception:
        return True  # if unreadable, treat as error
       
runs = sorted(glob.glob(os.path.join(FREEZE_DIR, "frozen_*")))
invalid_runs = []
rows: List[Dict[str, str]] = []

empty_items: List[Dict[str, str]] = []
error_items: List[Dict[str, str]] = []

for run in runs:
    run_name = os.path.basename(run)
    cfg_path = os.path.join(run, "config_used.yaml")
    per_sample = os.path.join(run, "per_sample.csv")
    raw_glob = os.path.join(run, "raw", "*__poisoned__*.txt")
    poisoned_txts = sorted(glob.glob(raw_glob))

    # metadata
    meta = read_yaml(cfg_path)
    model_id = ""
    dataset_path = ""
    try:
        model_id = (meta.get("model", {}) or {}).get("model_id", "")
        dataset_path = (meta.get("dataset", {}) or {}).get("path", "")
    except Exception:
        pass
    poisoned_expected = read_poisoned_expected_count(per_sample)

    # counts
    empty_count = 0
    error_count = 0
    for p in poisoned_txts:
        try:
            if os.path.getsize(p) == 0:
                empty_count += 1
                empty_items.append({"run": run_name, "file": p})
        except Exception:
            empty_count += 1
            empty_items.append({"run": run_name, "file": p})
        if file_contains_error_stub(p):
            error_count += 1
            error_items.append({"run": run_name, "file": p})

    status = "OK"
    reason = ""
    if empty_count > 0 or error_count > 0:
        status = "INVALID"
        reason = f"empty={empty_count}, error_stubs={error_count}"
        invalid_runs.append(run)

    rows.append({
        "run": run_name,
        "model_id": model_id,
        "dataset_path": dataset_path,
        "poisoned_raw_txts": str(len(poisoned_txts)),
        "poisoned_expected": str(poisoned_expected),
        "empty_poisoned_txts": str(empty_count),
        "error_stub_files": str(error_count),
        "status": status,
        "reason": reason,
    })

# write summary
with open(summary_path, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [
        "run","model_id","dataset_path","poisoned_raw_txts","poisoned_expected",
        "empty_poisoned_txts","error_stub_files","status","reason"
    ])
    w.writeheader()
    for r in rows:
        w.writerow(r)

# write invalid list
with open(invalid_path, "w", encoding="utf-8") as f:
    for r in invalid_runs:
        f.write(r + "\n")

# write detailed per-file reports
with open(empty_report, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["run","file"])
    w.writeheader()
    for it in empty_items:
        w.writerow(it)

with open(error_report, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["run","file"])
    w.writeheader()
    for it in error_items:
        w.writerow(it)

# console summary
print("[audit] Summary:")
for r in rows:
    tag = "OK" if r["status"] == "OK" else "INVALID"
    print(f" - {tag:7s} {r['run']}  (empty={r['empty_poisoned_txts']}, error_stubs={r['error_stub_files']}, model={r['model_id']})")

if invalid_runs:
    print(f"\n[audit] Found INVALID runs: {len(invalid_runs)}")
    print(f"[audit] See: {invalid_path}")
    sys.exit(1)
else:
    print("\n[audit] All frozen runs passed (no empties or error stubs).")
    sys.exit(0)
