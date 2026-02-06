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
**Steps:**

