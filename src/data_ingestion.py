"""Data ingestion utilities with robust date parsing and chunking."""
from __future__ import annotations

import pandas as pd
from typing import Dict, List
from pathlib import Path

from src import config


DATE_COLS = {
    "stock_movement": ["Date"],
    "stock_current": ["LastUpdatedAt"],
    "sales": ["Date"],
    "item_master": [],
    "employees": [],
    "branches": ["OpeningDate"],
}


def _read_csv(path: Path, date_cols: List[str]) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing required data file: {path}")
    return pd.read_csv(
        path,
        parse_dates=date_cols if date_cols else None,
        infer_datetime_format=True,
        dayfirst=True,
        encoding="utf-8",
    )


def load_all(paths: config.Paths = config.paths) -> Dict[str, pd.DataFrame]:
    """Load all required CSV files with date parsing.

    Uses chunked reading when file size exceeds a threshold to keep memory usage
    reasonable.
    """
    data: Dict[str, pd.DataFrame] = {}
    for name, path in paths.__dict__.items():
        date_cols = DATE_COLS.get(name, [])
        stat = path.stat()
        if stat.st_size > 10 * 1024 * 1024:  # >10MB, use chunks
            chunks: List[pd.DataFrame] = []
            for chunk in pd.read_csv(
                path,
                parse_dates=date_cols if date_cols else None,
                infer_datetime_format=True,
                dayfirst=True,
                chunksize=50000,
                encoding="utf-8",
            ):
                chunks.append(chunk)
            data[name] = pd.concat(chunks, ignore_index=True)
        else:
            data[name] = _read_csv(path, date_cols)
    return data


__all__ = ["load_all"]
