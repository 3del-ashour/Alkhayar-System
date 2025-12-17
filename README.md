# Alkhayar Stockout Risk MLOps (Level 2)

End-to-end CI/CD MLOps project using the provided CSV datasets to predict whether an item at a branch will fall below the safety stock level within the next 7 days. The pipeline automates ingestion, validation, feature engineering (hashing + feature crosses), ensemble modeling, MLflow tracking/registry, Prefect orchestration, GitLab CI, Dockerized FastAPI serving, monitoring, and fallback/rollback.

## Learning Task & Problem Reframing
- **Primary task:** Binary classification `risk_label` = will stock drop below `SafetyStockLevel` in the next **7 days**.
- **Reframing:** Instead of regressing future demand, the task directly classifies the risk, aligning with business need for actionable alerts and enabling class balancing/thresholding.

## Key Design Choices
- **High-cardinality** handled via **feature hashing** for `ItemCode`, `BranchID`, and crosses.
- **Feature cross**: `ItemCode×BranchID` and `ItemCode×Month` hashed into fixed vectors.
- **Model:** LightGBM boosting ensemble with imbalance-aware resampling when detected.
- **Checkpointing:** LightGBM boosters saved periodically to `artifacts/checkpoints` to resume training.
- **Orchestration:** Prefect flow covering ingest → validate → feature build → train → evaluate → MLflow register/promote → container build.
- **Experiment tracking:** MLflow tracking + Model Registry with automatic Staging → Production promotion when `f1 >= 0.65`.
- **Serving:** FastAPI `POST /predict` returns risk + probability; falls back to rule-based heuristic on errors and supports registry rollback.
- **CI/CD:** GitLab CI with lint, unit/component tests, docker build, and acceptance (pipeline) stage.
- **Monitoring:** Continued Model Evaluation + drift checks (PSI + KS) with persisted reports and rollback demo.

## Repository Layout
```
./src                # pipeline code (config, ingestion, validation, features, model, monitoring, serving utils)
./orchestration      # Prefect flow
./serving            # FastAPI app
./scripts            # CLI helpers (run pipeline, monitoring, fallback demo)
./docker             # Dockerfile + docker-compose
./data/examples      # sample CSV slices (real data goes in data/ and is gitignored)
./tests              # unit/component tests
./docs               # plan + business outline
```

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Running the Pipeline
- **Local end-to-end:** `python scripts/run_pipeline.py` (executes Prefect flow).
- **Direct training:** `python -c "from src.pipeline import run_training; print(run_training())"`
- MLflow artifacts stored in `./mlruns` by default.

## Serving API
- Local: `uvicorn serving.app:app --host 0.0.0.0 --port 8000`
- Docker Compose (MLflow + API):
  ```bash
  cd docker
  docker-compose up --build
  ```
- Request example:
  ```bash
  curl -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"Date":"2024-01-08","BranchID":1,"BranchName":"Main","ItemCode":"A1","ItemName":"Widget","CurrentQuantity":80,"ReservedQuantity":5,"SafetyStockLevel":30,"QuantitySold":12}'
  ```

## Monitoring & Drift
- Run CME + drift job: `python scripts/cme_job.py`
- Reports written to `./reports`. Baseline metrics saved to `reports/baseline_metrics.json` on first successful run.
- Drift uses PSI + KS; performance drop threshold 0.05.

## Fallback & Rollback
- Rule-based fallback inside serving returns risk when model unavailable.
- Registry rollback demo: `python scripts/fallback_demo.py` (uses prior MLflow versions when available).

## CI/CD
- GitLab CI stages: commit → quality (ruff) → test (pytest unit+component) → build (docker) → acceptance (pipeline smoke).

## Governance & Roles
- See `roles.md` for RACI-style mapping (Data Engineer, ML Engineer, DevOps, Monitoring/Observability).

## Batch Serving Note
Batch predictions can be added by feeding a DataFrame to `src.serve_utils.predict` in batch mode or using Prefect tasks; current implementation focuses on stateless real-time REST per requirements.

## Reproducibility
- Fixed seeds, deterministic LightGBM config, and versioned artifacts in `mlruns`.
- Sample CSVs provided; place full datasets in `data/` with matching schema.
