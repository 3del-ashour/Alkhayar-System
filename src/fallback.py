"""Fallback strategies for degraded performance or drift."""
from __future__ import annotations

import mlflow
from typing import Dict

from src import config


def rule_based_prediction(payload: Dict) -> Dict:
    """Simple baseline: flag risk if current quantity is within 10% of safety stock after demand."""
    current_qty = float(payload.get("CurrentQuantity", 0))
    reserved = float(payload.get("ReservedQuantity", 0))
    safety = float(payload.get("SafetyStockLevel", 0))
    expected_sales = float(payload.get("ExpectedSales", payload.get("QuantitySold", 0)))
    projected = current_qty - reserved - expected_sales
    risk = projected <= safety * 1.1
    return {"risk": int(risk), "probability": 0.5 if risk else 0.1, "fallback": True}


def rollback_to_previous_version(model_name: str = config.training.model_name) -> str:
    """Return latest Production or previous Staging model URI for rollback."""
    client = mlflow.tracking.MlflowClient()
    versions = client.search_model_versions(f"name='{model_name}'")
    # prefer last Production then Staging
    prod_versions = [v for v in versions if v.current_stage == "Production"]
    staging_versions = [v for v in versions if v.current_stage == "Staging"]
    chosen = None
    if len(prod_versions) > 1:
        chosen = sorted(prod_versions, key=lambda v: int(v.version))[-2]
    elif staging_versions:
        chosen = sorted(staging_versions, key=lambda v: int(v.version))[-1]
    if chosen:
        client.transition_model_version_stage(model_name, chosen.version, "Production", archive_existing_versions=True)
        return chosen.source
    raise RuntimeError("No previous model version available for rollback")


__all__ = ["rule_based_prediction", "rollback_to_previous_version"]
