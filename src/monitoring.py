"""Continued Model Evaluation and drift monitoring."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import mlflow
import numpy as np
import pandas as pd

from src import config
from src.validation import build_drift_report, write_report
from src.model import evaluate_model


class MonitoringResult(Dict[str, float]):
    pass


def continued_evaluation(model, recent_df: pd.DataFrame, baseline_metrics: Dict[str, float]) -> MonitoringResult:
    metrics = evaluate_model(model, recent_df)
    drops = {
        k: baseline_metrics[k] - metrics.get(k, 0) for k in baseline_metrics if k in metrics
    }
    triggered = any(v > config.monitoring.performance_drop for v in drops.values())
    result: MonitoringResult = MonitoringResult(metrics)
    result["triggered"] = triggered
    result["drops"] = drops
    return result


def monitor_drift(baseline: pd.DataFrame, recent: pd.DataFrame, numeric_cols: List[str]) -> Dict:
    report = build_drift_report(
        baseline,
        recent,
        numeric_cols,
        psi_threshold=config.monitoring.psi_threshold,
        ks_threshold=config.monitoring.drift_ks_pvalue,
    )
    drift_trigger = any(v.get("drifted", False) for v in report.values())
    report_summary = {"drift_trigger": drift_trigger, "details": report}
    return report_summary


def save_monitoring_outputs(performance: Dict, drift: Dict, path: Path) -> None:
    payload = {"performance": performance, "drift": drift}
    write_report(payload, path)


def load_baseline_metrics(path: Path = config.monitoring.baseline_report) -> Dict[str, float]:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("performance", {})
    return {}


def persist_baseline(performance: Dict, drift: Dict) -> None:
    write_report({"performance": performance, "drift": drift}, config.monitoring.baseline_report)


__all__ = [
    "continued_evaluation",
    "monitor_drift",
    "save_monitoring_outputs",
    "load_baseline_metrics",
    "persist_baseline",
]
