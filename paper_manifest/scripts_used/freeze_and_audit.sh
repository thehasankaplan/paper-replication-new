
# - If run without args: create a new FREEZE_DIR and copy latest runs/* into it.
# - If --audit-only --freeze-dir <dir>: just audit that directory.

set -euo pipefail

FREEZE_DIR=""
AUDIT_ONLY="false"

print_usage() {
  cat <<EOF
Usage:
  $0                         # create new FREEZE_DIR and copy latest runs/*
  $0 --audit-only --freeze-dir <dir>   # only audit an existing freeze dir
EOF
}

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --audit-only)
      AUDIT_ONLY="true"; shift ;;
    --freeze-dir)
      FREEZE_DIR="${2:-}"; shift 2 ;;
    -h|--help)
      print_usage; exit 0 ;;
    *)
      echo "ERROR: unknown arg: $1" >&2; print_usage; exit 2 ;;
  esac
done

ts_utc() { date -u +%Y%m%d_%H%M%S; }

# If not audit-only, create new freeze dir & copy latest runs
if [[ "$AUDIT_ONLY" != "true" ]]; then
  FREEZE_DIR="${FREEZE_DIR:-freeze_$(ts_utc)_xmodels}"
  mkdir -p "$FREEZE_DIR"
  echo "[freeze] Using FREEZE_DIR=$FREEZE_DIR"

  # Copy all runs/* 
  mapfile -t LATEST < <(ls -dt runs/2025* 2>/dev/null | head -3 || true)
  if [[ ${#LATEST[@]} -eq 0 ]]; then
    echo "[freeze] No runs/ found." >&2
    exit 0
  fi
  for r in "${LATEST[@]}"; do
    cp -r "$r" "$FREEZE_DIR"/
  done
else
  if [[ -z "$FREEZE_DIR" ]]; then
    echo "ERROR: --audit-only requires --freeze-dir <dir>" >&2; exit 2
  fi
  echo "[freeze] Using FREEZE_DIR=$FREEZE_DIR"
fi

# --- Audit ---
INVALID_FILE="$FREEZE_DIR/invalid_runs.txt"
: > "$INVALID_FILE"

invalid_count=0
for rd in "$FREEZE_DIR"/*; do
  [[ -d "$rd" ]] || continue
  raw="$rd/raw"
  [[ -d "$raw" ]] || continue

  empty_count=$(find "$raw" -type f -name 'req_*.txt' -size 0 | wc -l | tr -d ' ')
  error_stub=$(grep -R --line-number '^[[]ERROR[]]' "$raw" || true)
  if [[ "$empty_count" != "0" ]] || [[ -n "$error_stub" ]]; then
    echo "$rd" >> "$INVALID_FILE"
    ((invalid_count+=1))
  fi
done

echo
echo "[audit] Found INVALID runs: $invalid_count"
echo "[audit] See: $INVALID_FILE"
