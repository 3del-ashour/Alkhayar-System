"""End-to-end training pipeline with MLflow logging and registry promotion."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.model_selection import train_test_split

from src import config
from src.data_ingestion import load_all
from src.feature_engineering import build_training_table
from src.model import METRIC_KEYS, evaluate_model, train_model
from src.validation import validate_schema


mlflow.set_tracking_uri(config.training.mlflow_tracking_uri)
mlflow.set_experiment(config.training.experiment_name)


def run_training() -> Dict[str, float]:
    datasets = load_all()
    validate_schema(datasets)

    training_df = build_training_table(
        datasets["sales"], datasets["stock_current"], datasets["stock_movement"], horizon=config.training.horizon_days
    )

    train_df, test_df = train_test_split(
        training_df,
        test_size=config.training.test_size,
        random_state=config.training.random_state,
        stratify=training_df["risk_label"],
    )

    with mlflow.start_run() as run:
        model, train_metrics = train_model(train_df)
        eval_metrics = evaluate_model(model, test_df)

        for k, v in {**train_metrics, **{f"test_{k}": v for k, v in eval_metrics.items()}}.items():
            mlflow.log_metric(k, v)
        mlflow.log_params(
            {
                "horizon_days": config.training.horizon_days,
                "hash_dims": config.training.hash_dims,
                "learning_rate": config.training.learning_rate,
                "num_leaves": config.training.num_leaves,
            }
        )

        mlflow.sklearn.log_model(model, "model")
        mlflow.log_artifact(str(config.CHECKPOINT_DIR / "lgbm_checkpoint.txt"))

        # register and promote if acceptance criteria met
        model_uri = f"runs:/{run.info.run_id}/model"
        result = mlflow.register_model(model_uri, config.training.model_name)
        client = mlflow.tracking.MlflowClient()
        client.transition_model_version_stage(
            name=config.training.model_name,
            version=result.version,
            stage="Staging",
            archive_existing_versions=True,
        )
        if eval_metrics["f1"] >= config.training.acceptance_f1:
            client.transition_model_version_stage(
                name=config.training.model_name,
                version=result.version,
                stage="Production",
                archive_existing_versions=True,
            )

    return eval_metrics


__all__ = ["run_training"]
