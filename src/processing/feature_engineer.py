"""Compute derived / engineered fields from joined property data."""
from __future__ import annotations

from datetime import datetime

import pandas as pd


def add_derived_fields(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    today = pd.Timestamp(datetime.now())

    # --- years_owned ---
    if "sale_date_1" in df.columns:
        sd1 = pd.to_datetime(df["sale_date_1"], errors="coerce")
        df["years_owned"] = (today - sd1).dt.days / 365.25

    # --- sale_count ---
    sale_date_cols = [c for c in df.columns if c.startswith("sale_date_")]
    if sale_date_cols:
        df["sale_count"] = df[sale_date_cols].notna().sum(axis=1)

    # --- estimated_equity ---
    if "estimated_market_value" in df.columns:
        emv = df["estimated_market_value"].copy()
        # Estimate remaining mortgage balance from sale price + years owned
        # Assume 80% LTV at purchase, amortized ~2% per year
        sp1 = pd.to_numeric(df.get("sale_price_1", pd.Series(0.0, index=df.index)), errors="coerce").fillna(0)
        yo = pd.to_numeric(df.get("years_owned", pd.Series(0.0, index=df.index)), errors="coerce").fillna(0)
        amort_factor = (0.80 - yo * 0.02).clip(lower=0)
        est_remaining = sp1 * amort_factor
        df["estimated_equity_dollar"] = emv - est_remaining
        df["estimated_equity_pct"] = df["estimated_equity_dollar"] / emv.replace(0, float("nan"))

    # --- owner flags ---
    if "owner_mailing_state" in df.columns:
        state = df["owner_mailing_state"].str.strip().str.upper()
        df["out_of_state_flag"] = state.notna() & (state != "") & (state != "IL")
    else:
        df["out_of_state_flag"] = False

    if "owner_mailing_address" in df.columns and "address" in df.columns:
        mail = df["owner_mailing_address"].fillna("").str.upper().str.strip()
        prop = df["building_address"].fillna("").str.upper().str.strip() if "building_address" in df.columns else df["address"].fillna("").str.upper().str.strip()
        same_start = pd.Series(
            [m[:10] == p[:10] if m and p else True for m, p in zip(mail, prop)],
            index=df.index,
        )
        df["absentee_owner_flag"] = (mail != "") & (mail != prop) & ~same_start
    if "absentee_owner_flag" not in df.columns:
        df["absentee_owner_flag"] = False

    # homeowner exemption is not available from the Assessor API
    # use absentee_owner_flag as proxy: owner-occupied = not absentee
    if "owner_occupied_flag" not in df.columns:
        df["owner_occupied_flag"] = ~df["absentee_owner_flag"]

    # --- investor_flag ---
    corp = df.get("corporate_owner_flag", pd.Series(False, index=df.index))
    port = pd.to_numeric(df.get("portfolio_size", pd.Series(dtype="float64")), errors="coerce")
    df["investor_flag"] = (corp == True) | (port > 1)  # noqa: E712

    # --- senior_flag (from property class or building age as proxy) ---
    # No exemption data available from API; set to False
    df["senior_flag"] = False

    # --- permit flags ---
    if "latest_permit_date" in df.columns:
        lpd = pd.to_datetime(df["latest_permit_date"], errors="coerce")
        two_years_ago = today - pd.Timedelta(days=730)
        df["recent_permit_flag"] = lpd >= two_years_ago
    else:
        df["recent_permit_flag"] = False

    # --- violation flag ---
    vco = pd.to_numeric(df.get("violation_count_open", 0), errors="coerce").fillna(0)
    df["open_violation_flag"] = vco > 0

    # --- price_to_rent_ratio ---
    emv = pd.to_numeric(df.get("estimated_market_value", pd.Series(dtype="float64")), errors="coerce")
    beds = pd.to_numeric(df.get("num_bedrooms", pd.Series(dtype="float64")), errors="coerce").fillna(1)
    fmr_map = {}
    for br, key in [(0, "fmr_studio"), (1, "fmr_1br"), (2, "fmr_2br"), (3, "fmr_3br")]:
        if key in df.columns:
            fmr_map[br] = df[key].iloc[0] if not df[key].isna().all() else None
    if 4 <= 4 and "fmr_4br" in df.columns:
        fmr_map[4] = df["fmr_4br"].iloc[0] if not df["fmr_4br"].isna().all() else None

    if fmr_map:
        annual_rent = beds.clip(0, 4).map(lambda b: fmr_map.get(int(b), fmr_map.get(2))) * 12
        annual_rent = annual_rent.replace(0, float("nan"))
        df["price_to_rent_ratio"] = emv / annual_rent
    else:
        df["price_to_rent_ratio"] = float("nan")

    # --- appreciation_vs_zip ---
    sp1 = pd.to_numeric(df.get("sale_price_1", pd.Series(dtype="float64")), errors="coerce")
    if "estimated_market_value" in df.columns:
        prop_appr = (emv - sp1) / sp1.replace(0, float("nan"))
        zip_appr = pd.to_numeric(df.get("zip_yoy_price_change_pct", 0), errors="coerce")
        df["appreciation_vs_zip"] = prop_appr - zip_appr
    else:
        df["appreciation_vs_zip"] = float("nan")

    # --- year_built from building_age ---
    if "building_age" in df.columns and "year_built" not in df.columns:
        age = pd.to_numeric(df["building_age"], errors="coerce")
        tax_yr = pd.to_numeric(df.get("tax_year", 2024), errors="coerce").fillna(2024)
        df["year_built"] = tax_yr - age

    # --- change_flag placeholder ---
    df["change_flag"] = ""

    # Ensure boolean columns are actual bools
    for col in ["absentee_owner_flag", "out_of_state_flag", "owner_occupied_flag",
                 "investor_flag", "senior_flag", "recent_permit_flag", "open_violation_flag"]:
        if col in df.columns:
            df[col] = df[col].fillna(False).astype(bool)

    print(f"  Derived fields added: {len(df.columns)} total columns")
    return df
