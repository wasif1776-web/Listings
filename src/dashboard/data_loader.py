"""Cached loader for the scored parcel dataset."""
from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
import pandas as pd


def _scored_mtime() -> float:
    """Return modification time of scored_latest.parquet (used as cache key)."""
    p = Path(__file__).resolve().parents[2] / "data" / "outputs" / "scored_latest.parquet"
    if p.exists():
        return os.path.getmtime(p)
    return 0.0


@st.cache_data(ttl=300, show_spinner="Loading scored data…")
def load_scored_data(_mtime: float | None = None) -> pd.DataFrame:
    """Read ``scored_latest.parquet`` with Streamlit caching.

    The *_mtime* parameter is passed solely to bust the cache when the
    file changes on disk — callers should pass ``_scored_mtime()``.
    """
    p = Path(__file__).resolve().parents[2] / "data" / "outputs" / "scored_latest.parquet"
    if not p.exists():
        st.error(f"Scored data not found at `{p}`. Run the pipeline first (`python main.py`).")
        st.stop()
    return pd.read_parquet(p)


__all__ = ["load_scored_data", "_scored_mtime"]
