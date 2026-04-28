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

_PROPERTY_CLASS_DESCRIPTIONS = {
    "200": "Vacant land (residential use)",
    "201": "Vacant residential land",
    "202": "Single-family, one-story",
    "203": "Single-family, two-story",
    "205": "Single-family, partial improvements",
    "206": "Two-family, frame",
    "207": "Two-family, one-story",
    "208": "Two-family, two-story",
    "209": "Two-family with attic/basement apt",
    "210": "Multi-family (3-6 units)",
    "211": "Multi-family (7+ units, 1-2 stories)",
    "212": "Multi-family (7+ units, 3+ stories)",
    "241": "Multi-use (2+ uses on one parcel)",
    "278": "Mixed-use (commercial + residential)",
    "295": "Townhouse / attached row house",
    "299": "Condominium unit",
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
    _markers = [25, 50, 75, 100]
    cols = st.columns(len(_markers))
    for i, val in enumerate(_markers):
        with cols[i]:
            if st.button(str(val), key=f"score_btn_{val}", use_container_width=True):
                st.session_state["min_score_slider"] = val
    min_score = st.slider(
        "Minimum Score", 0, 100,
        value=st.session_state.get("min_score_slider", 0),
        step=1,
        key="min_score_slider",
    )

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
            counts = df["property_class"].value_counts()

            def _on_select_all_change():
                val = st.session_state["pc_select_all"]
                for c in classes:
                    st.session_state[f"pc_{c}"] = val

            with st.container(border=True):
                st.markdown("**Property Classes**")
                st.checkbox("Select All", value=True, key="pc_select_all", on_change=_on_select_all_change)

                class_selected: list[str] = []
                for c in classes:
                    desc = _PROPERTY_CLASS_DESCRIPTIONS.get(c, "Other")
                    cnt = counts.get(c, 0)
                    label = f"{c} - {desc} ({cnt:,})"
                    default = st.session_state.get(f"pc_{c}", True)
                    checked = st.checkbox(
                        label, value=default, key=f"pc_{c}",
                        help=f"Class {c}: {desc} -- {cnt:,} properties",
                    )
                    if checked:
                        class_selected.append(c)

            selected_classes = class_selected if class_selected else None
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
