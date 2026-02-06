# Indirect Prompt Injection in IAM Policy Copilots: Replication Package

This repository is the replication package for the paper:

**Indirect Prompt Injection in IAM Policy Copilots: A Structured-Output Benchmark for Least-Privilege Violations**

It is designed to be **reproducible without calling any model APIs** by providing **frozen run summaries** (CSV/JSON)
for all runs reported in the paper, plus scripts to regenerate the paper tables and figures from those frozen summaries.

## Repository layout

### Paper-facing artifacts
- `paper/`  
  LaTeX tables (`.tex`), CSVs used in tables, and curated qualitative examples used in the manuscript.
- `paper_figures/`  
  PDF figures used in the paper:
  - `paper_figures/full/`
  - `paper_figures/mixed_ns/`

### Core reproducibility: frozen runs + provenance
- `paper_manifest/`
  - `RUNS_USED.txt`  
    The **exact run IDs** used in the paper.
  - `frozen_runs/`  
    Frozen run summaries for each paper run (per-run directories).
  - `configs_used/`  
    YAML configs used to define the evaluation parameters for each run (model IDs, suite selection, decoding, etc.).
  - `scripts_used/`  
    Scripts used to aggregate frozen runs, compute metrics, and generate figures/tables.
  - `datasets_used/`  
    Benchmark JSONL files used by the evaluation harness (needed **only** for optional inference reruns).
  - `PYTHON_VERSION.txt`, `PIP_FREEZE.txt`, `GIT_COMMIT.txt`  
    Environment + provenance metadata for traceability.

### Convenience outputs (already included)
- `full/` and `mixed_ns/`  
  Pre-aggregated CSVs/LaTeX tables/examples derived from the frozen runs.


## What this package intentionally does NOT contain

- Any API keys / credentials.
- Any requirement that a reviewer must rerun paid/commercial model inference to validate the paper results.

Re-running model inference is **optional** and requires the reviewer’s own credentials/model access.


## Quick start (no API calls)

You can validate the paper immediately by opening the included outputs:

- Main result tables:
  - `full/table_overall.tex`
  - `mixed_ns/table_overall.tex`
- Figures:
  - `paper_figures/full/overall_asr_with_ci.pdf`
  - `paper_figures/full/variant_asr_heatmap.pdf`
  - `paper_figures/full/stealth_vs_derailment.pdf`
  - (and the same under `paper_figures/mixed_ns/`)

---

## Reproducing the paper results from frozen runs (no API calls)

## FULL suite (from frozen runs)

### 1) Aggregate CSVs (overall + per-variant matrix)

```bash
mkdir -p full

python3 paper_manifest/scripts_used/collect_results_matrix.py \
  --runs \
    paper_manifest/frozen_runs/20260124_173448_us_anthropic_claude_sonnet_4_5_20250929_v1_0 \
    paper_manifest/frozen_runs/20260124_194245_amazon_nova_lite_v1_0 \
    paper_manifest/frozen_runs/20260125_064456_amazon_nova_pro_v1_0 \
  --out_overall full/model_overall.csv \
  --out_matrix full/model_variant_matrix.csv
```

### 2) Compute confidence intervals + emit LaTeX tables

This step also writes the `*_with_ci.csv` files used by plotting.

```bash
python3 paper_manifest/scripts_used/make_paper_tables.py \
  --overall full/model_overall.csv \
  --matrix full/model_variant_matrix.csv \
  --out_dir full
```

Expected outputs include:
- `full/model_overall_with_ci.csv`
- `full/model_variant_matrix_with_ci.csv`
- `full/table_overall.tex`
- `full/table_variants_asr.tex`

### 3) Stealth vs derailment CSV

```bash
python3 paper_manifest/scripts_used/stealth_vs_derailment.py \
  --run "Claude Sonnet 4.5=paper_manifest/frozen_runs/20260124_173448_us_anthropic_claude_sonnet_4_5_20250929_v1_0" \
  --run "Nova Lite=paper_manifest/frozen_runs/20260124_194245_amazon_nova_lite_v1_0" \
  --run "Nova Pro=paper_manifest/frozen_runs/20260125_064456_amazon_nova_pro_v1_0" \
  --out full/stealth_vs_derailment_full.csv
```

### 4) Generate figures

```bash
mkdir -p paper_figures/full

python3 paper_manifest/scripts_used/plot_paper_figures.py \
  --overall_with_ci full/model_overall_with_ci.csv \
  --variant_matrix full/model_variant_matrix_with_ci.csv \
  --outdir paper_figures/full \
  --title_prefix "FULL"

python3 paper_manifest/scripts_used/plot_stealth_derailment.py \
  --csv full/stealth_vs_derailment_full.csv \
  --out paper_figures/full/stealth_vs_derailment.pdf \
  --title "Stealth vs. Derailment (FULL)"
```

---

## MIXED_NS suite (from frozen runs)

### 1) Aggregate CSVs (overall + per-variant matrix)

```bash
mkdir -p mixed_ns

python3 paper_manifest/scripts_used/collect_results_matrix.py \
  --runs \
    paper_manifest/frozen_runs/20260125_113755_us_anthropic_claude_sonnet_4_5_20250929_v1_0 \
    paper_manifest/frozen_runs/20260125_134104_amazon_nova_lite_v1_0 \
    paper_manifest/frozen_runs/20260125_130011_amazon_nova_pro_v1_0 \
  --out_overall mixed_ns/model_overall.csv \
  --out_matrix mixed_ns/model_variant_matrix.csv
```

### 2) Compute confidence intervals + emit LaTeX tables

```bash
python3 paper_manifest/scripts_used/make_paper_tables.py \
  --overall mixed_ns/model_overall.csv \
  --matrix mixed_ns/model_variant_matrix.csv \
  --out_dir mixed_ns
```

### 3) Stealth vs derailment CSV

```bash
python3 paper_manifest/scripts_used/stealth_vs_derailment.py \
  --run "Claude Sonnet 4.5=paper_manifest/frozen_runs/20260125_113755_us_anthropic_claude_sonnet_4_5_20250929_v1_0" \
  --run "Nova Lite=paper_manifest/frozen_runs/20260125_134104_amazon_nova_lite_v1_0" \
  --run "Nova Pro=paper_manifest/frozen_runs/20260125_130011_amazon_nova_pro_v1_0" \
  --out mixed_ns/stealth_vs_derailment_mixed_ns.csv
```

### 4) Generate figures

```bash
mkdir -p paper_figures/mixed_ns

python3 paper_manifest/scripts_used/plot_paper_figures.py \
  --overall_with_ci mixed_ns/model_overall_with_ci.csv \
  --variant_matrix mixed_ns/model_variant_matrix_with_ci.csv \
  --outdir paper_figures/mixed_ns \
  --title_prefix "MIXED_NS"

python3 paper_manifest/scripts_used/plot_stealth_derailment.py \
  --csv mixed_ns/stealth_vs_derailment_mixed_ns.csv \
  --out paper_figures/mixed_ns/stealth_vs_derailment.pdf \
  --title "Stealth vs. Derailment (MIXED_NS)"
```

---

## Defense-gate evaluation (optional; from frozen runs)

This recomputes the post-generation **format/schema gate** outputs and effective-ASR calculations.

```bash
python3 paper_manifest/scripts_used/defense_gate_eval.py \
  --run paper_manifest/frozen_runs/20260124_173448_us_anthropic_claude_sonnet_4_5_20250929_v1_0 \
  --out full/defense_gate_claude.csv

python3 paper_manifest/scripts_used/compute_effective_asr_after_gate.py \
  --gate_csv full/defense_gate_claude.csv \
  --out_csv full/defense_gate_claude_effective.csv
```

(Repeat for the Nova Lite/Pro run directories if desired.)

---

## Rerunning inference (optional; requires your own AWS Bedrock credentials)
**Cost note:** rerunning inference may incur cost depending on model and scale.
**This section is optional.** The primary validation path is reproducing from frozen summaries (above).

### Prerequisites
- AWS credentials configured (e.g., `aws configure`) and AWS Bedrock access.
- Bedrock model access enabled in your AWS account/region for the models referenced in the configs.
- Python environment + dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Datasets

This repo includes the benchmark JSONLs under:

- `paper_manifest/datasets_used/`
  - `policy_bench_v3_strict_s55.jsonl`
  - `policy_bench_v3_attack_aug.jsonl`
  - `policy_bench_v3_mixed_attack_aug_NS.jsonl`
  - `smoke.jsonl`
  - `adversarial_test_data.jsonl`

**Important:** YAML configs may refer to dataset paths relative to the config location.
If a config expects `paper_manifest/datasets/...` but the repo uses `paper_manifest/datasets_used/...`, you can either:

- (A) create a symlink so the paths match:
  ```bash
  ln -s datasets_used paper_manifest/datasets
  ```
  (Run from the repo root.)

**OR**

- (B) edit the YAML config(s) under `paper_manifest/configs_used/` to point to `../datasets_used/...`.

### Run inference

The inference harness is:

- `paper_manifest/scripts_used/run_eval.py`

Because CLI flags can vary by harness version, first inspect the supported arguments:

```bash
python3 paper_manifest/scripts_used/run_eval.py --help
```

Then run one of the provided configs. Example configs:
- `paper_manifest/configs_used/attack_aug_claude_full.yaml`
- `paper_manifest/configs_used/attack_aug_nova_lite_full.yaml`
- `paper_manifest/configs_used/attack_aug_nova_pro_full.yaml`

Example command (adjust `--out_dir` / `--out` according to `--help`):

```bash
mkdir -p runs

python3 paper_manifest/scripts_used/run_eval.py \
  --config paper_manifest/configs_used/attack_aug_claude_full.yaml \
  --out_dir runs/new_run_claude_full
```

### Freeze/audit (recommended for reproducibility)

After inference completes, convert raw outputs into the frozen-summary format:

```bash
python3 paper_manifest/scripts_used/audit_freeze.py --help
```

Then run with the flags shown by `--help`. Example (adjust flag names if needed):

```bash
python3 paper_manifest/scripts_used/audit_freeze.py \
  --run_dir runs/new_run_claude_full \
  --out_dir runs/new_run_claude_full_frozen
```

### Regenerate tables/figures from your new run

Once you have a frozen output directory for your new run, reuse the commands in
“Reproducing the paper results from frozen runs” but replace the
`paper_manifest/frozen_runs/...` paths with your `runs/..._frozen` directory.

**Cost note:** rerunning inference may incur cost depending on model and scale.

---

## Troubleshooting

- If you see “No such file or directory” for output paths, create them first:
  ```bash
  mkdir -p full mixed_ns paper_figures/full paper_figures/mixed_ns
  ```
- If a script’s CLI differs from what is shown above, run:
  ```bash
  python3 <script.py> --help
  ```
  and follow the usage printed by the script.

**Cost note:** rerunning inference may incur cost depending on model and scale.


