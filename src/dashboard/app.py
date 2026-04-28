"""Streamlit dashboard entry point.

Run with:
    streamlit run src/dashboard/app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_root = str(Path(__file__).resolve().parents[2])
if _root not in sys.path:
    sys.path.insert(0, _root)

import streamlit as st

from src.dashboard.data_loader import load_scored_data, _scored_mtime
from src.dashboard.components.zip_selector import render_zip_selector
from src.dashboard.components.filters import render_filters
from src.dashboard.components.map_view import render_map
from src.dashboard.components.table_view import render_table
from src.dashboard.components.detail_panel import render_detail
from src.dashboard.components.export_button import render_export_button

# -- Page config --

st.set_page_config(
    page_title="Listings -- Propensity Scores",
    page_icon="🏠",
    layout="wide",
)

st.title("Listings -- Real Estate Propensity Scores")

# -- Sidebar: ZIP selector, then filters, then export --

with st.sidebar:
    zip_code = render_zip_selector()

    if zip_code is None:
        st.stop()

    st.divider()

    df = load_scored_data(zip_code, _mtime=_scored_mtime(zip_code))
    filtered_df, score_col = render_filters(df)

    st.divider()
    render_export_button(filtered_df)

# -- Main area --

st.subheader("Map")
render_map(filtered_df, score_col)

st.subheader("Ranked Properties")
render_table(filtered_df, score_col)

st.divider()
render_detail(filtered_df)
