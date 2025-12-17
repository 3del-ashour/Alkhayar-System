"""Prefect flow orchestrating the MLOps pipeline."""
from __future__ import annotations

import subprocess
from pathlib import Path

from prefect import flow, task

from src import config
from src.data_ingestion import load_all
from src.feature_engineering import build_training_table
from src.model import train_model, evaluate_model
from src.monitoring import save_monitoring_outputs, persist_baseline
from src.validation import validate_schema
from src.pipeline import run_training


@task
def ingest_task():
    datasets = load_all()
    validate_schema(datasets)
    return datasets


@task
def feature_task(datasets):
    return build_training_table(
        datasets["sales"], datasets["stock_current"], datasets["stock_movement"], horizon=config.training.horizon_days
    )


@task
def train_task(training_df):
    model, metrics = train_model(training_df)
    return model, metrics


@task
def evaluate_task(model, training_df):
    return evaluate_model(model, training_df)


@task
def register_and_promote(metrics):
    # reuse run_training to leverage MLflow registry logic
    return run_training()


@task
def build_and_deploy_container():
    dockerfile = Path(__file__).resolve().parent.parent / "docker" / "Dockerfile"
    if not dockerfile.exists():
        raise FileNotFoundError("Dockerfile not found")
    try:
        subprocess.run(["docker", "build", "-t", "stockout-api", "-f", str(dockerfile), ".."], check=True)
    except Exception as exc:  # noqa: BLE001
        print(f"[orchestration] Docker build failed or unavailable: {exc}")
    return True


@flow(name="stockout_risk_flow")
def stockout_flow():
    datasets = ingest_task()
    training_df = feature_task(datasets)
    model, train_metrics = train_task(training_df)
    eval_metrics = evaluate_task(model, training_df)
    registry_metrics = register_and_promote(eval_metrics)
    save_monitoring_outputs(eval_metrics, {"drift_trigger": False}, config.REPORTS_DIR / "latest_flow_report.json")
    persist_baseline(eval_metrics, {"drift_trigger": False})
    build_and_deploy_container()
    return {"train": train_metrics, "eval": eval_metrics, "registry": registry_metrics}


if __name__ == "__main__":
    stockout_flow()
