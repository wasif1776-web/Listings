"""Chicago building violations ingestion."""
from __future__ import annotations

import pandas as pd

from .socrata import fetch_socrata

DOMAIN = "data.cityofchicago.org"
DATASET_ID = "22u3-xenr"


def fetch_violations(
    lat_min: float = 41.870,
    lat_max: float = 41.912,
    lon_min: float = -87.656,
    lon_max: float = -87.620,
    zip_code: str = "60610",
) -> pd.DataFrame:
    """Fetch open building violations for the given bounding box."""
    print(f"[Violations] Fetching violations for ZIP {zip_code} area...")

    df = fetch_socrata(
        DOMAIN, DATASET_ID,
        where=(
            f"latitude >= '{lat_min}' AND latitude <= '{lat_max}' "
            f"AND longitude >= '{lon_min}' AND longitude <= '{lon_max}' "
            f"AND violation_status = 'OPEN'"
        ),
        select="address,violation_date,violation_code,violation_status,latitude,longitude",
    )
    if df.empty:
        print("  -> 0 violations")
        return pd.DataFrame(columns=["violation_address", "violation_count_open"])

    df["violation_address"] = df["address"].str.strip().str.upper()

    agg = df.groupby("violation_address").agg(
        violation_count_open=("violation_date", "count"),
    ).reset_index()

    print(f"  -> {len(agg):,} addresses with open violations")
    return agg
