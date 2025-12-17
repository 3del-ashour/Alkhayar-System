import pandas as pd

from src.pipeline import run_training


def test_training_run_smoke(monkeypatch):
    # shorten training for test
    from src import config
    config.training.max_rounds = 10
    config.training.early_stopping_rounds = 5
    metrics = run_training()
    assert "f1" in metrics
