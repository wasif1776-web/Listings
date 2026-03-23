"""Ranked table view of scored parcels."""
from __future__ import annotations

import streamlit as st
import pandas as pd

from .filters import SCORE_COLUMNS


def render_table(df: pd.DataFrame, score_col: str) -> None:
    """Render a sortable table with conditional row highlighting."""
    if df.empty:
        st.info("No properties match the current filters.")
        return

    # Columns to display
    display_cols = ["address", "pin", score_col]
    display_cols += [c for c in SCORE_COLUMNS if c in df.columns and c != score_col]
    display_cols += [
        c for c in ("change_flag", "years_owned", "absentee_owner_flag", "investor_flag")
        if c in df.columns
    ]
    # Keep only columns that actually exist
    display_cols = [c for c in display_cols if c in df.columns]

    view = df[display_cols].copy()

    # Sort descending by selected score
    if score_col in view.columns:
        view = view.sort_values(score_col, ascending=False, na_position="last")

    st.dataframe(
        view,
        use_container_width=True,
        height=500,
        column_config={
            "change_flag": st.column_config.TextColumn(
                "Change",
                help="new = first appearance, score_changed = score shifted",
            ),
        },
    )


__all__ = ["render_table"]
