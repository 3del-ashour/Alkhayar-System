"""Feature engineering utilities for stockout risk classification."""
from __future__ import annotations

import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction import FeatureHasher
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from typing import Tuple

from src import config


class HashingTransformer(BaseEstimator, TransformerMixin):
    """Hash categorical columns using scikit-learn's FeatureHasher."""

    def __init__(self, n_features: int = 64):
        self.n_features = n_features
        self.hasher = FeatureHasher(n_features=n_features, input_type="string")

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        # Expect X as DataFrame; combine values per row as tokens
        token_lists = X.astype(str).apply(lambda row: list(row.values), axis=1).tolist()
        hashed = self.hasher.transform(token_lists)
        return hashed.astype(np.float32)


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["day_of_week"] = df["Date"].dt.dayofweek
    df["month"] = df["Date"].dt.month
    return df


def build_training_table(
    sales: pd.DataFrame,
    stock_current: pd.DataFrame,
    stock_movement: pd.DataFrame,
    horizon: int,
) -> pd.DataFrame:
    """Build supervised training table with derived label."""
    sales = sales.copy()
    stock_current = stock_current.copy()
    stock_movement = stock_movement.copy()

    sales["Date"] = pd.to_datetime(sales["Date"], errors="coerce")
    stock_current["LastUpdatedAt"] = pd.to_datetime(stock_current["LastUpdatedAt"], errors="coerce")
    stock_movement["Date"] = pd.to_datetime(stock_movement["Date"], errors="coerce")

    sales_daily = (
        sales.groupby(["Date", "BranchID", "ItemCode", "ItemName", "BranchName"], as_index=False)["QuantitySold"].sum()
    )

    # Lagged sales for trend
    sales_daily = sales_daily.sort_values("Date")
    sales_daily["lag1_sales"] = sales_daily.groupby(["BranchID", "ItemCode"])['QuantitySold'].shift(1).fillna(0)
    sales_daily["sales_7d_avg"] = (
        sales_daily.groupby(["BranchID", "ItemCode"])["QuantitySold"].transform(lambda s: s.rolling(window=7, min_periods=1).mean())
    )

    # Future sales for label
    sales_daily["future_sales"] = (
        sales_daily.groupby(["BranchID", "ItemCode"])["QuantitySold"].transform(
            lambda s: s.shift(-1).rolling(window=horizon, min_periods=1).sum()
        )
    )

    # Stock movements: incoming and outgoing
    stock_movement["net_movement"] = stock_movement.apply(
        lambda r: -r["QuantityMoved"] if pd.notnull(r["FromBranchID"]) and r["FromBranchID"] == r["ToBranchID"] else r["QuantityMoved"],
        axis=1,
    )
    move_daily = (
        stock_movement.groupby(["Date", "ToBranchID", "ItemCode"], as_index=False)["net_movement"].sum()
    ).rename(columns={"ToBranchID": "BranchID"})
    move_daily["movement_7d_net"] = move_daily.groupby(["BranchID", "ItemCode"])["net_movement"].transform(
        lambda s: s.rolling(window=7, min_periods=1).sum()
    )

    df = sales_daily.merge(move_daily[["Date", "BranchID", "ItemCode", "movement_7d_net"]],
                           on=["Date", "BranchID", "ItemCode"], how="left")

    df = df.merge(
        stock_current[
            [
                "BranchID",
                "BranchName",
                "ItemCode",
                "ItemName",
                "CurrentQuantity",
                "ReservedQuantity",
                "SafetyStockLevel",
            ]
        ],
        on=["BranchID", "ItemCode"],
        how="left",
    )

    df["movement_7d_net"] = df["movement_7d_net"].fillna(0)
    df["CurrentQuantity"] = df["CurrentQuantity"].fillna(df["QuantitySold"])  # fallback assumption
    df["ReservedQuantity"] = df["ReservedQuantity"].fillna(0)
    df["SafetyStockLevel"] = df["SafetyStockLevel"].fillna(df["QuantitySold"].median())

    df = add_time_features(df)
    df["item_branch_cross"] = df["ItemCode"].astype(str) + "_" + df["BranchID"].astype(str)
    df["item_month_cross"] = df["ItemCode"].astype(str) + "_" + df["month"].astype(str)

    df["risk_label"] = (
        (df["CurrentQuantity"] - df["future_sales"].fillna(0)) <= df["SafetyStockLevel"]
    ).astype(int)

    return df.dropna(subset=["risk_label"])


def build_preprocessing_pipeline(hash_dims: int) -> ColumnTransformer:
    categorical_cols = ["ItemCode", "BranchID", "item_branch_cross", "item_month_cross"]
    numeric_cols = [
        "CurrentQuantity",
        "ReservedQuantity",
        "SafetyStockLevel",
        "QuantitySold",
        "sales_7d_avg",
        "movement_7d_net",
        "lag1_sales",
        "day_of_week",
        "month",
    ]

    preprocessing = ColumnTransformer(
        transformers=[
            (
                "cat_hash",
                HashingTransformer(n_features=hash_dims),
                categorical_cols,
            ),
            (
                "num",
                Pipeline([
                    ("scaler", StandardScaler()),
                ]),
                numeric_cols,
            ),
        ],
        remainder="drop",
    )
    return preprocessing


__all__ = ["build_training_table", "build_preprocessing_pipeline"]
