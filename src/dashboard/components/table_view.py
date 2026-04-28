"""Ranked table view of scored parcels."""
from __future__ import annotations

import streamlit as st
import pandas as pd

from .filters import SCORE_COLUMNS


_PAGE_SIZES = [50, 100, 250, 500, 1000]


def render_table(df: pd.DataFrame, score_col: str) -> None:
    """Render a paginated, sortable table."""
    if df.empty:
        st.info("No properties match the current filters.")
        return

    # Columns to display
    display_cols = ["address", "pin", score_col]
    display_cols += [c for c in SCORE_COLUMNS if c in df.columns and c != score_col]
    display_cols += [
        c for c in (
            "property_class", "estimated_market_value", "years_owned",
            "estimated_equity_pct", "absentee_owner_flag", "investor_flag",
        )
        if c in df.columns
    ]
    display_cols = [c for c in display_cols if c in df.columns]

    view = df[display_cols].copy()
    if score_col in view.columns:
        view = view.sort_values(score_col, ascending=False, na_position="last")
    view = view.reset_index(drop=True)

    total_rows = len(view)

    # Pagination controls
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        page_size = st.selectbox("Rows per page", _PAGE_SIZES, index=1, key="page_size")
    total_pages = max(1, (total_rows + page_size - 1) // page_size)
    with col3:
        page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1, key="page_num")
    with col2:
        st.markdown(f"**{total_rows:,} results** | Page {page} of {total_pages}")

    start = (page - 1) * page_size
    end = min(start + page_size, total_rows)
    page_df = view.iloc[start:end]

    st.dataframe(
        page_df,
        use_container_width=True,
        height=min(700, 35 * len(page_df) + 38),
        column_config={
            "estimated_market_value": st.column_config.NumberColumn(
                "Est. Market Value", format="$%,.0f",
            ),
            "estimated_equity_pct": st.column_config.NumberColumn(
                "Equity %", format="%.0f%%",
            ),
            "years_owned": st.column_config.NumberColumn(
                "Yrs Owned", format="%.1f",
            ),
        },
    )


__all__ = ["render_table"]
