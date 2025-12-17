"""Shared utilities for serving predictions."""
from __future__ import annotations

from typing import Dict, Any
import pandas as pd
import mlflow

from src import config
from src.fallback import rule_based_prediction


def load_production_model(model_name: str = config.training.model_name):
    client = mlflow.tracking.MlflowClient()
    prod = client.get_latest_versions(model_name, stages=["Production"])
    if not prod:
        raise RuntimeError("No production model found")
    model_uri = prod[0].source
    return mlflow.pyfunc.load_model(model_uri)


def predict(payload: Dict[str, Any], model=None) -> Dict[str, Any]:
    try:
        model = model or load_production_model()
        df = pd.DataFrame([payload])
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(df)
            probability = float(probs[:, 1][0]) if probs.ndim > 1 else float(probs[0])
        else:
            preds = model.predict(df)
            probability = float(preds[0]) if preds.size else 0.0
        risk = int(probability >= 0.5)
        return {"risk": risk, "probability": probability, "fallback": False}
    except Exception as exc:  # noqa: BLE001
        fallback = rule_based_prediction(payload)
        fallback["error"] = str(exc)
        return fallback


__all__ = ["predict", "load_production_model"]
