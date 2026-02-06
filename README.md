# Indirect Prompt Injection in IAM Policy Copilots: A Structured-Output Benchmark for Least-Privilege Violations

This directory is a **self-contained snapshot** of the paper-facing artifacts and the **frozen run summaries**
used to produce the tables/figures reported in the paper.
# Indirect Prompt Injection in IAM Policy Copilots: A Structured-Output Benchmark for Least-Privilege Violations

This repository is the **replication package** for the paper:

**Indirect Prompt Injection in IAM Policy Copilots: A Structured-Output Benchmark for Least-Privilege Violations**

It is designed to be **reproducible without calling any model APIs** by providing **frozen run summaries** (CSV/JSON) for the runs reported in the paper, along with scripts to regenerate the paper tables and figures.

## What this package contains

### 1) Paper-facing outputs
- `paper/`  
  Paper-facing artifacts such as LaTeX tables (`.tex`), CSVs used in tables, and curated qualitative examples.
- `paper_figures/`  
  PDF figures used in the paper (both `full/` and `mixed_ns/`).

### 2) Provenance + frozen runs (the core of reproducibility)
- `paper_manifest/`
  - `RUNS_USED.txt`  
    The **exact run IDs** used for the paper.
  - `frozen_runs/`  
    Per-run frozen summaries (e.g., `per_sample.csv`, `variant_semantic.csv`, `pairwise_semantic.csv`, etc.).
    These are the “source of truth” used to regenerate the aggregate results.
  - `configs_used/`  
    YAML configs used to produce each run (model ID, decoding, prompt template choices, suite, etc.).
  - `scripts_used/`  
    Scripts used to aggregate frozen runs, generate tables/figures, and export examples.
  - `PYTHON_VERSION.txt`, `PIP_FREEZE.txt`, `GIT_COMMIT.txt`  
    Environment + provenance metadata for traceability.

### 3) Aggregate paper results (derived from frozen runs)
- `full/` and `mixed_ns/`  
  Pre-aggregated CSVs and LaTeX tables derived from `paper_manifest/frozen_runs/`, plus example markdown files.

## What this artifact intentionally does NOT contain
- Any API keys / credentials.
- Any requirement that the evaluator must rerun paid model inference to validate results.
- Guaranteed “rerun from scratch” inference for commercial models without the reviewer’s own credentials.
  (Rerunning inference is optional and may incur cost.)
  
We include **optional** rerun instructions for authors/curious readers with credentials, but the paper can be verified from frozen summaries alone.


## Quick start (no re-running)

1. Unzip the bundle.
2. Open:
   - `paper/table_main_results.tex` (Table 1)
   - `paper_figures/overall_asr_with_ci.pdf`
   - `paper_figures/variant_asr_heatmap.pdf`

## Reproducing the paper tables/figures from frozen runs (one command)

This artifact includes **frozen run summaries** under `paper_manifest/frozen_runs/`.
From those summaries, you can regenerate the main results table and the core figures **without calling any model API**.

**Steps:**

```bash
# from the directory that contains paper_bundle/
cd paper_bundle

# create a virtualenv (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# install minimal dependencies (pandas/numpy/matplotlib/scipy)
pip install -U pip
pip install pandas numpy matplotlib scipy

# one command: regenerate Table 1 + key figures from frozen runs
python3 paper_manifest/reproduce_from_frozen_runs.py


## Rerunning Inference (Optional) If you have your own AWS Bedrock credentials, you can run new evaluations using the provided configurations:
## Regenerate CSV outputs + figures from frozen runs

The run IDs used in the paper are listed in:

paper_manifest/RUNS_USED.txt

FULL suite: regenerate matrices + stealth/abandon + figures
# Example: set these to the FULL run directories (see RUNS_USED.txt)
RUNS_FULL=(
  paper_manifest/frozen_runs/20260124_173448_us_anthropic_claude_sonnet_4_5_20250929_v1_0
  paper_manifest/frozen_runs/20260124_194245_amazon_nova_lite_v1_0
  paper_manifest/frozen_runs/20260125_064456_amazon_nova_pro_v1_0
)

python3 paper_manifest/scripts_used/collect_results_matrix.py \
  --runs "${RUNS_FULL[@]}" \
  --out_dir full

python3 paper_manifest/scripts_used/stealth_vs_derailment.py \
  --runs "${RUNS_FULL[@]}" \
  --out full/stealth_vs_derailment_full.csv

python3 paper_manifest/scripts_used/plot_paper_figures.py \
  --overall_with_ci full/model_overall_with_ci.csv \
  --variant_matrix full/model_variant_matrix.csv \
  --outdir paper_figures/full \
  --title_prefix "FULL"

python3 paper_manifest/scripts_used/plot_stealth_derailment.py \
  --csv full/stealth_vs_derailment_full.csv \
  --out paper_figures/full/stealth_vs_derailment.pdf \
  --title_suffix "FULL"

MIXED_NS suite: regenerate matrices + stealth/abandon + figures
RUNS_MIXED=(
  paper_manifest/frozen_runs/20260125_113755_us_anthropic_claude_sonnet_4_5_20250929_v1_0
  paper_manifest/frozen_runs/20260125_134104_amazon_nova_lite_v1_0
  paper_manifest/frozen_runs/20260125_130011_amazon_nova_pro_v1_0
)

python3 paper_manifest/scripts_used/collect_results_matrix.py \
  --runs "${RUNS_MIXED[@]}" \
  --out_dir mixed_ns

python3 paper_manifest/scripts_used/stealth_vs_derailment.py \
  --runs "${RUNS_MIXED[@]}" \
  --out mixed_ns/stealth_vs_derailment_mixed_ns.csv

python3 paper_manifest/scripts_used/plot_paper_figures.py \
  --overall_with_ci mixed_ns/model_overall_with_ci.csv \
  --variant_matrix mixed_ns/model_variant_matrix.csv \
  --outdir paper_figures/mixed_ns \
  --title_prefix "MIXED_NS"

python3 paper_manifest/scripts_used/plot_stealth_derailment.py \
  --csv mixed_ns/stealth_vs_derailment_mixed_ns.csv \
  --out paper_figures/mixed_ns/stealth_vs_derailment.pdf \
  --title_suffix "MIXED_NS"

3) Regenerate LaTeX tables (optional)
python3 paper_manifest/scripts_used/make_paper_tables.py \
  --overall full/model_overall.csv \
  --matrix full/model_variant_matrix.csv \
  --out_dir full

python3 paper_manifest/scripts_used/make_paper_tables.py \
  --overall mixed_ns/model_overall.csv \
  --matrix mixed_ns/model_variant_matrix.csv \
  --out_dir mixed_ns

Defense gate evaluation (from frozen runs)

The package  includes scripts and outputs for the post-generation format gate / effective ASR computations.

# Example for one run directory (repeat for each run if desired)
python3 paper_manifest/scripts_used/defense_gate_eval.py \
  --run paper_manifest/frozen_runs/20260124_173448_us_anthropic_claude_sonnet_4_5_20250929_v1_0 \
  --out full/defense_gate_claude.csv

python3 paper_manifest/scripts_used/compute_effective_asr_after_gate.py \
  --gate_csv full/defense_gate_claude.csv \
  --out_csv full/defense_gate_claude_effective.csv

Rerunning Inference (Optional)

If you have your own AWS Bedrock credentials and model access, you can rerun inference using the provided configs.

Prerequisites

AWS credentials configured (e.g., via aws configure).

Bedrock access to the required models in your region.

Python environment created and dependencies installed:

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

## Datasets needed

To rerun the exact experiments, you must have the benchmark JSONLs a:
datasets/policy_bench_v3_strict_s55.jsonl
datasets/policy_bench_v3_attack_aug.jsonl
datasets/policy_bench_v3_mixed_attack_aug_NS.jsonl

(These are synthetic benchmark files used by the evaluation harness.)

Steps

Pick a config from:

paper_manifest/configs_used/

Run inference (example command; adjust to your harness’ CLI):

python3 paper_manifest/scripts_used/run_eval.py \
  --config paper_manifest/configs_used/attack_aug_claude_full.yaml \
  --out runs/new_run_claude_full


Postprocess the run to compute per-sample + pairwise semantic summaries.

Freeze/audit the run (optional but recommended for reproducibility):
python3 paper_manifest/scripts_used/audit_freeze.py runs/new_run_claude_full


Regenerate tables/figures using the same “frozen runs” commands above, pointing at your new run directory.

Notes
Rerunning inference may incur cost depending on models and scale.
This artifact’s primary validation path is reproducing results from the included frozen runs (no API calls).


