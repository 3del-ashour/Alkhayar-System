# Implementation Plan for MLOps Level 2 Project

## Scope Choices
- **Learning task:** Classification for stockout risk: predict whether an item at a branch will fall below `SafetyStockLevel` in the next 7 days.
- **Feature strategy:**
  - High-cardinality handling via **feature hashing** for `ItemCode`, `BranchID`, and feature crosses.
  - Feature cross: `ItemCode × BranchID` and `ItemCode × Month` hashed into fixed dimensions.
- **Model:** LightGBM classifier (boosting ensemble) with class imbalance detection and optional resampling (SMOTE or RandomUnderSampler).
- **Checkpointing:** Save LightGBM boosters at intervals during training to allow resume.
- **Orchestrator:** Prefect 2 flow covering ingest → validate → feature build → train → evaluate → register/promote → build/deploy serving image.
- **Experiment tracking:** MLflow tracking server and Model Registry (local file backend) with stage transitions.
- **Serving:** FastAPI REST `POST /predict`; model loaded from MLflow; fallback rule and registry rollback support.
- **CI/CD:** GitLab CI with stages: commit, quality (lint), tests (unit + component), build (docker), and acceptance (pipeline run excerpt). Uses pytest and ruff.
- **Monitoring:** Continued Model Evaluation with rolling datasets, drift checks (PSI + KS), schema validation, and alert-based fallback.

## Target Repository Layout (new/updated files)
- `README.md` – runbook and rationale.
- `roles.md` – team roles mapping.
- `docs/` – this plan and business presentation outline.
- `data/` – ignored real data; `data/examples/*.csv` sample slices.
- `src/`
  - `config.py` – configuration (paths, seeds, thresholds).
  - `data_ingestion.py` – CSV loading with chunking and date parsing.
  - `validation.py` – schema checks, drift calculators.
  - `feature_engineering.py` – feature builders, hashing, crosses.
  - `model.py` – model training, imbalance handling, checkpoints, evaluation.
  - `pipeline.py` – MLflow logging helpers and orchestration glue.
  - `monitoring.py` – continued evaluation, drift detection, fallback triggers.
  - `fallback.py` – rule-based fallback and registry rollback utilities.
  - `serve_utils.py` – prediction logic shared with API.
- `orchestration/prefect_flow.py` – Prefect DAG.
- `serving/app.py` – FastAPI app for `/predict` with MLflow loading and fallback logic.
- `docker/Dockerfile` – API container image.
- `docker/docker-compose.yml` – local stack (API + MLflow server).
- `ci/.gitlab-ci.yml` – CI/CD pipeline.
- `tests/` – unit/component tests for features, validation, pipeline.
- `scripts/`
  - `run_pipeline.py` – CLI to run Prefect flow end-to-end.
  - `cme_job.py` – scheduled monitoring job.
  - `fallback_demo.py` – demonstrate rollback/fallback.

## Key Decisions
- Prefect chosen for lightweight local orchestration and simple configuration.
- Feature hashing chosen over embeddings to keep footprint small while handling high-cardinality identifiers.
- Boosting ensemble (LightGBM) selected for tabular performance and native categorical handling via hashes.
- MLflow used for tracking and registry to enable promotion/rollback; local backend for simplicity.
- Drift detection via PSI and KS tests; schema validation via pandera-like checks coded in `validation.py`.
- Serving remains stateless; batch serving discussed in README but not implemented.
