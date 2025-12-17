"""Scheduled job to perform continued model evaluation and drift checks."""
from __future__ import annotations

import pandas as pd

from src import config
from src.data_ingestion import load_all
from src.feature_engineering import build_training_table
from src.monitoring import continued_evaluation, monitor_drift, load_baseline_metrics, save_monitoring_outputs
from src.serve_utils import load_production_model


if __name__ == "__main__":
    datasets = load_all()
    dataset = build_training_table(
        datasets["sales"], datasets["stock_current"], datasets["stock_movement"], horizon=config.training.horizon_days
    )
    # use most recent window as monitoring slice
    recent = dataset.tail(config.monitoring.rolling_window)
    baseline_metrics = load_baseline_metrics()
    model = load_production_model()

    performance = continued_evaluation(model, recent, baseline_metrics)
    drift_report = monitor_drift(
        dataset.head(config.monitoring.rolling_window),
        recent,
        numeric_cols=["QuantitySold", "CurrentQuantity", "SafetyStockLevel", "sales_7d_avg"],
    )
    save_monitoring_outputs(performance, drift_report, config.REPORTS_DIR / "monitoring_latest.json")
    print("Monitoring completed", performance, drift_report)
