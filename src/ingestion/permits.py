"""Chicago building permits ingestion."""
from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd

from .socrata import fetch_socrata

DOMAIN = "data.cityofchicago.org"
DATASET_ID = "ydr8-5enu"


def _build_address(row: pd.Series) -> str:
    parts = []
    for col in ("street_number", "street_direction", "street_name"):
        val = str(row.get(col, "") or "").strip()
        if val:
            parts.append(val)
    return " ".join(parts).upper()


def fetch_permits(
    lat_min: float = 41.870,
    lat_max: float = 41.912,
    lon_min: float = -87.656,
    lon_max: float = -87.620,
    zip_code: str = "60610",
) -> pd.DataFrame:
    """Fetch building permits for the given bounding box and aggregate per address."""
    print(f"[Permits] Fetching permits for ZIP {zip_code} area...")

    five_years_ago = (datetime.now() - timedelta(days=5 * 365)).strftime("%Y-%m-%dT00:00:00")

    df = fetch_socrata(
        DOMAIN, DATASET_ID,
        where=(
            f"latitude >= '{lat_min}' AND latitude <= '{lat_max}' "
            f"AND longitude >= '{lon_min}' AND longitude <= '{lon_max}' "
            f"AND issue_date >= '{five_years_ago}'"
        ),
    )
    if df.empty:
        print("  -> 0 permits")
        return pd.DataFrame(columns=["permit_address", "permit_count_5yr", "latest_permit_date"])

    df["permit_address"] = df.apply(_build_address, axis=1)
    df["issue_date"] = pd.to_datetime(df["issue_date"], errors="coerce")

    agg = df.groupby("permit_address").agg(
        permit_count_5yr=("issue_date", "count"),
        latest_permit_date=("issue_date", "max"),
    ).reset_index()

    print(f"  -> {len(agg):,} addresses with permits")
    return agg
