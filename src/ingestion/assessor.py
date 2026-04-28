"""Cook County Assessor data ingestion (locations, characteristics, sales, values)."""
from __future__ import annotations

import pandas as pd

from .socrata import fetch_socrata

DOMAIN = "datacatalog.cookcountyil.gov"
LOCATIONS_ID = "c49d-89sn"
CHARACTERISTICS_ID = "bcnq-qi2z"
SALES_ID = "wvhk-k5uv"
VALUES_ID = "uzyt-m557"


def fetch_locations(zip_code: str = "60610") -> pd.DataFrame:
    print(f"[Assessor] Fetching locations for ZIP {zip_code}...")
    df = fetch_socrata(
        DOMAIN, LOCATIONS_ID,
        where=f"starts_with(property_zip, '{zip_code}')",
    )
    print(f"  -> {len(df):,} locations")
    return df


def fetch_characteristics(pin_prefix: str = "1704") -> pd.DataFrame:
    print(f"[Assessor] Fetching characteristics for PINs {pin_prefix}*...")
    df = fetch_socrata(
        DOMAIN, CHARACTERISTICS_ID,
        where=f"starts_with(pin, '{pin_prefix}')",
    )
    print(f"  -> {len(df):,} characteristic records")
    return df


def fetch_sales(pin_prefix: str = "1704") -> pd.DataFrame:
    print(f"[Assessor] Fetching sales for PINs {pin_prefix}*...")
    df = fetch_socrata(
        DOMAIN, SALES_ID,
        where=f"starts_with(pin, '{pin_prefix}')",
    )
    print(f"  -> {len(df):,} sale transactions")
    return df


def fetch_assessed_values(pin_prefix: str = "1704") -> pd.DataFrame:
    print(f"[Assessor] Fetching assessed values for PINs {pin_prefix}*...")
    df = fetch_socrata(
        DOMAIN, VALUES_ID,
        where=f"starts_with(pin, '{pin_prefix}') AND year >= '2023'",
    )
    print(f"  -> {len(df):,} assessment records")
    return df


def pivot_sales(raw: pd.DataFrame, pins: set[str]) -> pd.DataFrame:
    """Pivot individual sale transactions into per-PIN columns."""
    if raw.empty:
        return pd.DataFrame(columns=["pin"])

    df = raw[raw["pin"].isin(pins)].copy()
    df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
    df["sale_price"] = pd.to_numeric(df["sale_price"], errors="coerce")
    df = df.dropna(subset=["sale_date"])
    df = df.sort_values(["pin", "sale_date"], ascending=[True, False])
    df["rank"] = df.groupby("pin").cumcount() + 1
    df = df[df["rank"] <= 3]

    parts = []
    for rank in [1, 2, 3]:
        sub = df[df["rank"] == rank][["pin", "sale_date", "sale_price", "deed_type"]].copy()
        sub = sub.rename(columns={
            "sale_date": f"sale_date_{rank}",
            "sale_price": f"sale_price_{rank}",
            "deed_type": f"deed_type_{rank}",
        })
        parts.append(sub)

    result = parts[0]
    for p in parts[1:]:
        result = result.merge(p, on="pin", how="outer")

    print(f"  -> {len(result):,} PINs with sale history")
    return result


def get_latest_assessed_values(raw: pd.DataFrame, pins: set[str]) -> pd.DataFrame:
    """Get the most recent assessed value per PIN."""
    if raw.empty:
        return pd.DataFrame(columns=["pin", "assessed_value"])

    df = raw[raw["pin"].isin(pins)].copy()
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["certified_tot"] = pd.to_numeric(df.get("certified_tot"), errors="coerce")
    df["mailed_tot"] = pd.to_numeric(df.get("mailed_tot"), errors="coerce")
    df["assessed_value"] = df["certified_tot"].fillna(df["mailed_tot"])
    df = df.dropna(subset=["assessed_value"])
    df = df[df["assessed_value"] > 0]
    df = df.sort_values(["pin", "year"], ascending=[True, False])
    df = df.groupby("pin").first().reset_index()

    print(f"  -> {len(df):,} PINs with assessed values")
    return df[["pin", "assessed_value"]]
