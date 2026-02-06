# Indirect Prompt Injection in IAM Policy Copilots: A Structured-Output Benchmark for Least-Privilege Violations

This directory is a **self-contained snapshot** of the paper-facing artifacts and the **frozen run summaries**
used to produce the tables/figures reported in the paper.

## What this artifact contains

- `paper/`  
  Camera-ready inputs for the manuscript (LaTeX-ready tables, CSVs, and curated qualitative examples).

- `paper_figures/`  
  PDF figures used in the paper.

- `paper_manifest/`  
  Provenance and reproducibility material:
  - `RUNS_USED.txt`: identifiers of the exact experiment runs used for the paper
  - `frozen_runs/`: **frozen run summaries** (CSV/JSON) for each run used in the paper

## What this artifact intentionally does NOT contain

- Any API keys / credentials.
- A full “rerun from scratch” pipeline that re-queries commercial LLM APIs.
  Re-running model inference requires paid API access and is not required to validate the paper’s measurements.

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
