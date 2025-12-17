"""Model training, evaluation, and checkpointing."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple

import joblib
import mlflow
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.under_sampling import RandomUnderSampler
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from lightgbm import LGBMClassifier

from src import config
from src.feature_engineering import build_preprocessing_pipeline


METRIC_KEYS = ["f1", "precision", "recall", "roc_auc", "accuracy"]


def _checkpoint_callback(path: Path, interval: int):
    def callback(env):
        if env.iteration % interval == 0:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            env.model.booster_.save_model(str(path))
    return callback


def train_model(train_df: pd.DataFrame, cfg: config.TrainingConfig = config.training) -> Tuple[ImbPipeline, Dict[str, float]]:
    X = train_df.drop(columns=["risk_label"])
    y = train_df["risk_label"]

    preprocessing = build_preprocessing_pipeline(cfg.hash_dims)

    # imbalance detection
    positive_ratio = y.mean()
    sampler = None
    if positive_ratio < 1 - cfg.imbalance_ratio or positive_ratio > cfg.imbalance_ratio:
        sampler = SMOTE(random_state=cfg.random_state) if positive_ratio < 0.5 else RandomUnderSampler(random_state=cfg.random_state)

    model = LGBMClassifier(
        objective="binary",
        n_estimators=cfg.max_rounds,
        learning_rate=cfg.learning_rate,
        num_leaves=cfg.num_leaves,
        subsample=cfg.bagging_fraction,
        subsample_freq=cfg.bagging_freq,
        feature_fraction=cfg.feature_fraction,
        random_state=cfg.random_state,
        n_jobs=-1,
    )

    steps = [("preprocess", preprocessing)]
    if sampler:
        steps.append(("sampler", sampler))
    steps.append(("model", model))

    pipeline = ImbPipeline(steps)

    model_callbacks = [_checkpoint_callback(config.CHECKPOINT_DIR / "lgbm_checkpoint.txt", cfg.checkpoint_interval)]

    pipeline.fit(X, y, model__callbacks=model_callbacks, model__eval_metric="auc")

    preds = pipeline.predict(X)
    prob = pipeline.predict_proba(X)[:, 1]
    metrics = {
        "f1": f1_score(y, preds),
        "precision": precision_score(y, preds),
        "recall": recall_score(y, preds),
        "roc_auc": roc_auc_score(y, prob),
        "accuracy": accuracy_score(y, preds),
        "class_ratio": float(positive_ratio),
    }

    return pipeline, metrics


def evaluate_model(model: ImbPipeline, df: pd.DataFrame) -> Dict[str, float]:
    X = df.drop(columns=["risk_label"])
    y = df["risk_label"]
    preds = model.predict(X)
    prob = model.predict_proba(X)[:, 1]
    return {
        "f1": f1_score(y, preds),
        "precision": precision_score(y, preds),
        "recall": recall_score(y, preds),
        "roc_auc": roc_auc_score(y, prob),
        "accuracy": accuracy_score(y, preds),
    }


__all__ = ["train_model", "evaluate_model", "METRIC_KEYS"]
