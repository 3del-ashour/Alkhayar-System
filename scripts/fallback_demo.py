"""Demonstrate fallback by forcing rollback when metrics fall below threshold."""
from __future__ import annotations

from src import config
from src.fallback import rollback_to_previous_version, rule_based_prediction
from src.monitoring import load_baseline_metrics


if __name__ == "__main__":
    baseline = load_baseline_metrics()
    if not baseline:
        print("No baseline available; showing rule-based fallback example.")
        example = rule_based_prediction(
            {
                "CurrentQuantity": 5,
                "ReservedQuantity": 1,
                "SafetyStockLevel": 10,
                "QuantitySold": 4,
            }
        )
        print(example)
    else:
        print("Attempting rollback to previous model version...")
        uri = rollback_to_previous_version()
        print(f"Rolled back to {uri}")
