"""Data validation and drift detection utilities."""
from __future__ import annotations

import json
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats


REQUIRED_COLUMNS = {
    "sales": ["Date", "BranchID", "BranchName", "InvoiceNumber", "ItemCode", "ItemName", "QuantitySold"],
    "stock_current": [
        "BranchID",
        "BranchName",
        "ItemCode",
        "ItemName",
        "CurrentQuantity",
        "ReservedQuantity",
        "SafetyStockLevel",
        "LastUpdatedAt",
    ],
    "stock_movement": [
        "MovementID",
        "Date",
        "FromBranchID",
        "FromBranchName",
        "ToBranchID",
        "ToBranchName",
        "ItemCode",
        "ItemName",
        "QuantityMoved",
    ],
}


class ValidationError(Exception):
    """Raised when required validations fail."""


def validate_columns(df: pd.DataFrame, name: str) -> None:
    missing = set(REQUIRED_COLUMNS.get(name, [])) - set(df.columns)
    if missing:
        raise ValidationError(f"{name} missing required columns: {missing}")


def validate_schema(datasets: Dict[str, pd.DataFrame]) -> None:
    for name, df in datasets.items():
        validate_columns(df, name)
        if df.isnull().sum().sum() > 0:
            # allow sparsity but log
            nulls = df.isnull().sum()
            print(f"[validation] Warning: nulls detected in {name}: {nulls[nulls>0].to_dict()}")


def psi(expected: np.ndarray, actual: np.ndarray, buckets: int = 10) -> float:
    """Population Stability Index for drift detection."""
    eps = 1e-6
    expected_perc, _ = np.histogram(expected, bins=buckets)
    actual_perc, _ = np.histogram(actual, bins=buckets)
    expected_perc = expected_perc / (len(expected) + eps)
    actual_perc = actual_perc / (len(actual) + eps)
    diff = actual_perc - expected_perc
    ln_ratio = np.log((actual_perc + eps) / (expected_perc + eps))
    return float(np.sum(diff * ln_ratio))


def ks_test(expected: np.ndarray, actual: np.ndarray) -> float:
    return float(stats.ks_2samp(expected, actual).pvalue)


def build_drift_report(
    baseline: pd.DataFrame,
    recent: pd.DataFrame,
    numeric_cols: List[str],
    psi_threshold: float,
    ks_threshold: float,
) -> Dict[str, Dict[str, float]]:
    report: Dict[str, Dict[str, float]] = {}
    for col in numeric_cols:
        base_series = baseline[col].dropna()
        recent_series = recent[col].dropna()
        report[col] = {
            "psi": psi(base_series.values, recent_series.values),
            "ks_pvalue": ks_test(base_series.values, recent_series.values),
            "drifted": psi(base_series.values, recent_series.values) > psi_threshold
            or ks_test(base_series.values, recent_series.values) < ks_threshold,
        }
    return report


def write_report(report: Dict, path) -> None:
    path.parent.mkdir(exist_ok=True, parents=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)


__all__ = ["validate_schema", "build_drift_report", "write_report", "ValidationError"]
