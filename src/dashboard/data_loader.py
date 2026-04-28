"""Cached loader for the scored parcel dataset."""
from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
import pandas as pd

from config.settings import scored_path_for_zip


def _scored_mtime(zip_code: str = "60610") -> float:
    """Return modification time of the scored parquet for a ZIP (used as cache key)."""
    p = scored_path_for_zip(zip_code)
    if p.exists():
        return os.path.getmtime(p)
    return 0.0


@st.cache_data(ttl=300, show_spinner="Loading scored data...")
def load_scored_data(zip_code: str, _mtime: float | None = None) -> pd.DataFrame:
    """Read the scored parquet for *zip_code* with Streamlit caching."""
    p = scored_path_for_zip(zip_code)
    if not p.exists():
        st.error(f"Scored data not found at `{p}`. Click 'Get Data' to run the pipeline.")
        st.stop()
    return pd.read_parquet(p)


__all__ = ["load_scored_data", "_scored_mtime"]
