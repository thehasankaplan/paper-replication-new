
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 RUN_DIR"
  echo "Example: $0 runs/20251119_180530"
  exit 2
fi

RUN_DIR="$1"
RAW_DIR="${RUN_DIR}/raw"

if [[ ! -d "$RAW_DIR" ]]; then
  echo "ERROR: No raw/ directory at: $RAW_DIR"
  exit 2
fi

echo "[inspect] Run: $RUN_DIR"

# 0) check
REPAIR_PY="scripts/repair_raw_json.py"
if [[ ! -f "$REPAIR_PY" ]]; then
  echo "ERROR: $REPAIR_PY not found. Please create it (see the Python block I gave you)."
  exit 2
fi

# 1) Zero-byte raw files
echo
echo "[inspect] Zero-byte raw files:"
find "$RAW_DIR" -type f -name 'req_*__*.txt' -size 0 -print | sed -n '1,200p' || true
ZB_COUNT=$(find "$RAW_DIR" -type f -name 'req_*__*.txt' -size 0 | wc -l | tr -d ' ')
echo "[inspect] Zero-byte count: $ZB_COUNT"

# 2) Provider error stubs
echo
echo "[inspect] [ERROR] stubs in raw text:"
grep -nR '^\[ERROR\]' "$RAW_DIR" || true
ERR_COUNT=$(grep -R '^\[ERROR\]' "$RAW_DIR" | wc -l | tr -d ' ')
echo "[inspect] [ERROR] lines: $ERR_COUNT"

# 3) Count how many REPAIRED.json we have and list missing
echo
echo "[inspect] REPAIRED present / missing:"
TOTAL_CAND=$(ls "$RAW_DIR"/req_*__*.txt 2>/dev/null | wc -l | tr -d ' ')
HAVE_REP=$(ls "$RAW_DIR"/req_*__*__REPAIRED.json 2>/dev/null | wc -l | tr -d ' ' || true)
echo "  - raw text candidates: $TOTAL_CAND"
echo "  - repaired json files: $HAVE_REP"

# Build list of raw text files that *should* have a repaired companion
MISSING_LIST="$(python3 - "$RAW_DIR" <<'PY'
import os, sys, glob
raw_dir = sys.argv[1]
missing = []
for p in sorted(glob.glob(os.path.join(raw_dir, "req_*_*.txt"))):
    base = os.path.basename(p)
    repaired = os.path.join(raw_dir, base.replace(".txt", "__REPAIRED.json"))
    if not os.path.exists(repaired):
        print(p)
PY
)"
if [[ -n "$MISSING_LIST" ]]; then
  echo "[inspect] Missing repaired JSON for:"
  echo "$MISSING_LIST" | sed -n '1,200p'
else
  echo "[inspect] No missing repaired JSON."
fi

# 4) Try to auto-repair any missing REPAIRED.json
if [[ -n "$MISSING_LIST" ]]; then
  echo
  echo "[repair] Attempting to repair missing files..."
  echo "$MISSING_LIST" | while read -r RAW_TXT; do
    [[ -n "$RAW_TXT" ]] || continue
    python3 "$REPAIR_PY" "$RAW_TXT" || true
  done
fi

# 5) Show final counts again
echo
echo "[inspect] FINAL counts after repair:"
HAVE_REP2=$(ls "$RAW_DIR"/req_*__*__REPAIRED.json 2>/dev/null | wc -l | tr -d ' ' || true)
ZB_COUNT2=$(find "$RAW_DIR" -type f -name 'req_*__*.txt' -size 0 | wc -l | tr -d ' ')
ERR_COUNT2=$(grep -R '^\[ERROR\]' "$RAW_DIR" | wc -l | tr -d ' ' || true)
echo "  - repaired json files: $HAVE_REP2"
echo "  - zero-byte raw files: $ZB_COUNT2"
echo "  - [ERROR] raw lines:   $ERR_COUNT2"

echo
echo "[inspect] Done."
