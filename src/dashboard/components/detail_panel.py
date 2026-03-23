"""Property detail panel — lookup by PIN and display all fields + score chart."""
from __future__ import annotations

import streamlit as st
import pandas as pd

from .filters import SCORE_COLUMNS

# Field groups for organized display
_FIELD_GROUPS: dict[str, list[str]] = {
    "Assessor": [
        "pin", "address", "property_class", "num_bedrooms", "num_bathrooms",
        "building_sq_ft", "land_sq_ft", "year_built", "assessed_value",
        "estimated_market_value", "tax_amount",
    ],
    "Recorder": [
        "sale_date_1", "sale_price_1", "sale_date_2", "sale_price_2",
        "sale_date_3", "sale_price_3", "deed_type", "mortgage_amount",
        "mortgage_type", "tax_delinquency_flag",
    ],
    "Permits": [
        "permit_count_5yr", "latest_permit_date",
    ],
    "Violations": [
        "violation_count_open",
    ],
    "Census": [
        "block_group_geoid", "tract_median_household_income",
        "tract_pct_renter_occupied", "tract_pct_65_plus",
        "tract_pct_35_to_54", "tract_pct_households_with_children",
        "tract_median_gross_rent",
    ],
    "Zillow": [
        "zip_zhvi", "zip_zori", "zip_yoy_price_change_pct",
        "zip_median_days_on_market", "zip_price_to_rent_ratio",
    ],
    "HUD": [
        "fmr_0br", "fmr_1br", "fmr_2br", "fmr_3br", "fmr_4br",
    ],
    "PropWire": [
        "propwire_equity_pct", "portfolio_size", "corporate_owner_flag",
        "absentee_owner_flag", "owner_occupied_flag",
        "skip_trace_phone", "skip_trace_email",
    ],
    "Derived": [
        "years_owned", "sale_count", "estimated_equity_pct",
        "estimated_equity_dollar", "investor_flag", "senior_flag",
        "recent_permit_flag", "open_violation_flag", "price_to_rent_ratio",
        "appreciation_vs_zip", "out_of_state_flag",
    ],
}


def render_detail(df: pd.DataFrame) -> None:
    """Render the property detail panel with PIN lookup."""
    st.subheader("Property Detail")

    pin_input = st.text_input("Look up by PIN", placeholder="e.g. 17093020010000")

    if not pin_input:
        st.caption("Enter a PIN above to view full property details.")
        return

    pin_input = pin_input.strip()
    matches = df[df["pin"].astype(str).str.strip() == pin_input] if "pin" in df.columns else pd.DataFrame()

    if matches.empty:
        st.warning(f"No property found with PIN `{pin_input}`.")
        return

    row = matches.iloc[0]

    # Score bar chart
    score_data = {}
    for col in SCORE_COLUMNS:
        if col in row.index:
            val = pd.to_numeric(row[col], errors="coerce")
            label = col.replace("score_", "").replace("_", " ").title()
            score_data[label] = val if pd.notna(val) else 0.0

    if score_data:
        chart_df = pd.DataFrame({"Score": score_data})
        st.bar_chart(chart_df)

    # Field groups
    for group_name, fields in _FIELD_GROUPS.items():
        present = [f for f in fields if f in row.index]
        if not present:
            continue
        with st.expander(group_name, expanded=True):
            for field in present:
                val = row[field]
                st.text(f"{field}: {val}")


__all__ = ["render_detail"]
