import pandas as pd

from src.feature_engineering import build_training_table, build_preprocessing_pipeline
from src import config


def test_feature_crosses_and_label():
    sales = pd.read_csv("data/examples/sales_transactions.csv", parse_dates=["Date"])
    stock = pd.read_csv("data/examples/stock_current.csv")
    moves = pd.read_csv("data/examples/stock_movement.csv", parse_dates=["Date"])
    df = build_training_table(sales, stock, moves, horizon=3)
    assert "item_branch_cross" in df.columns
    assert "item_month_cross" in df.columns
    assert df["risk_label"].isin([0, 1]).all()


def test_hashing_pipeline_dimensions():
    sales = pd.read_csv("data/examples/sales_transactions.csv", parse_dates=["Date"])
    stock = pd.read_csv("data/examples/stock_current.csv")
    moves = pd.read_csv("data/examples/stock_movement.csv", parse_dates=["Date"])
    df = build_training_table(sales, stock, moves, horizon=3)
    prep = build_preprocessing_pipeline(hash_dims=8)
    transformed = prep.fit_transform(df)
    assert transformed.shape[1] == 8 + len([
        "CurrentQuantity",
        "ReservedQuantity",
        "SafetyStockLevel",
        "QuantitySold",
        "sales_7d_avg",
        "movement_7d_net",
        "lag1_sales",
        "day_of_week",
        "month",
    ])
