"""Sidebar filter components for the Listings dashboard."""
from __future__ import annotations

import streamlit as st
import pandas as pd

SCORE_COLUMNS = [
    "score_likely_to_sell",
    "score_likely_to_buy",
    "score_downsize",
    "score_upsize",
    "score_near_retirement",
    "score_relocation_risk",
    "score_school_district_movers",
    "score_investor",
    "score_likely_to_rent_out",
    "score_upgrade_renters",
]

_USE_CASE_LABELS = {
    "score_likely_to_sell": "Likely to Sell",
    "score_likely_to_buy": "Likely to Buy",
    "score_downsize": "Downsize",
    "score_upsize": "Upsize",
    "score_near_retirement": "Near Retirement",
    "score_relocation_risk": "Relocation Risk",
    "score_school_district_movers": "School District Movers",
    "score_investor": "Investor",
    "score_likely_to_rent_out": "Likely to Rent Out",
    "score_upgrade_renters": "Upgrade Renters",
}


def render_filters(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Render sidebar filters and return (filtered_df, selected_score_column).

    All widgets are placed inside the caller's ``st.sidebar`` context.
    """
    st.header("Filters")

    # 1. Use case selector
    available = [c for c in SCORE_COLUMNS if c in df.columns]
    labels = [_USE_CASE_LABELS.get(c, c) for c in available]
    selected_label = st.selectbox("Use Case", labels, index=0)
    score_col = available[labels.index(selected_label)]

    # 2. Score threshold
    min_score = st.slider("Minimum Score", 0, 100, 0)

    # 3. Change flag filter
    change_options = ["All", "New", "Score Changed"]
    change_choice = st.radio("Change Status", change_options, index=0)

    # 4. Owner type filter
    owner_options = ["All", "Owner-Occupied", "Absentee", "Investor"]
    owner_choice = st.radio("Owner Type", owner_options, index=0)

    # 5. Property class filter
    if "property_class" in df.columns:
        classes = sorted(df["property_class"].dropna().unique().tolist())
        if classes:
            selected_classes = st.multiselect("Property Class", classes, default=classes)
        else:
            selected_classes = None
    else:
        selected_classes = None

    # ── Apply filters ────────────────────────────────────────────────────────
    filtered = df.copy()

    # Score threshold
    if score_col in filtered.columns:
        filtered = filtered[pd.to_numeric(filtered[score_col], errors="coerce").fillna(0) >= min_score]

    # Change flag
    if change_choice == "New" and "change_flag" in filtered.columns:
        filtered = filtered[filtered["change_flag"] == "new"]
    elif change_choice == "Score Changed" and "change_flag" in filtered.columns:
        filtered = filtered[filtered["change_flag"] == "score_changed"]

    # Owner type
    if owner_choice == "Owner-Occupied" and "owner_occupied_flag" in filtered.columns:
        filtered = filtered[filtered["owner_occupied_flag"] == True]  # noqa: E712
    elif owner_choice == "Absentee" and "absentee_owner_flag" in filtered.columns:
        filtered = filtered[filtered["absentee_owner_flag"] == True]  # noqa: E712
    elif owner_choice == "Investor" and "investor_flag" in filtered.columns:
        filtered = filtered[filtered["investor_flag"] == True]  # noqa: E712

    # Property class
    if selected_classes is not None and "property_class" in filtered.columns:
        filtered = filtered[filtered["property_class"].isin(selected_classes)]

    return filtered, score_col


__all__ = ["render_filters", "SCORE_COLUMNS"]
