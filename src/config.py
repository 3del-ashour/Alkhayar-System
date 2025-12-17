"""Project configuration for the MLOps Level 2 pipeline."""
from pathlib import Path
from dataclasses import dataclass, field


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
EXAMPLE_DATA_DIR = DATA_DIR / "examples"
MLRUNS_DIR = BASE_DIR / "mlruns"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
MONITORING_DIR = BASE_DIR / "monitoring"
REPORTS_DIR = BASE_DIR / "reports"
CHECKPOINT_DIR = ARTIFACTS_DIR / "checkpoints"


@dataclass
class TrainingConfig:
    horizon_days: int = 7
    experiment_name: str = "stockout_risk"
    mlflow_tracking_uri: str = MLRUNS_DIR.as_posix()
    model_name: str = "stockout_risk_classifier"
    test_size: float = 0.2
    random_state: int = 42
    hash_dims: int = 64
    acceptance_f1: float = 0.65
    imbalance_ratio: float = 0.65  # majority class threshold
    checkpoint_interval: int = 50
    max_rounds: int = 300
    early_stopping_rounds: int = 50
    learning_rate: float = 0.05
    num_leaves: int = 64
    feature_fraction: float = 0.9
    bagging_fraction: float = 0.8
    bagging_freq: int = 5


@dataclass
class MonitoringConfig:
    psi_threshold: float = 0.2
    drift_ks_pvalue: float = 0.05
    performance_drop: float = 0.05
    rolling_window: int = 50
    fallback_metric_floor: float = 0.6
    baseline_report: Path = REPORTS_DIR / "baseline_metrics.json"


@dataclass
class Paths:
    stock_movement: Path = EXAMPLE_DATA_DIR / "stock_movement.csv"
    stock_current: Path = EXAMPLE_DATA_DIR / "stock_current.csv"
    sales: Path = EXAMPLE_DATA_DIR / "sales_transactions.csv"
    item_master: Path = EXAMPLE_DATA_DIR / "item_master.csv"
    employees: Path = EXAMPLE_DATA_DIR / "employees.csv"
    branches: Path = EXAMPLE_DATA_DIR / "branches.csv"


training = TrainingConfig()
monitoring = MonitoringConfig()
paths = Paths()

ARTIFACTS_DIR.mkdir(exist_ok=True, parents=True)
CHECKPOINT_DIR.mkdir(exist_ok=True, parents=True)
REPORTS_DIR.mkdir(exist_ok=True, parents=True)
MONITORING_DIR.mkdir(exist_ok=True, parents=True)
