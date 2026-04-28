"""Zillow Research data ingestion."""
from __future__ import annotations

import requests
import pandas as pd
from io import StringIO

from config.settings import (
    ZILLOW_ZHVI_URL, ZILLOW_ZORI_URL, ZILLOW_SALES_URL, ZILLOW_DOM_URL,
)


def _download_zillow_csv(url: str, value_col: str, zip_code: str) -> float | None:
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        df = pd.read_csv(StringIO(resp.text))
    except Exception as e:
        print(f"  Warning: failed to download {value_col}: {e}")
        return None

    name_col = "RegionName"
    if name_col not in df.columns:
        return None

    row = df[df[name_col].astype(str) == zip_code]
    if row.empty:
        return None

    date_cols = [c for c in df.columns if c[:4].isdigit()]
    if not date_cols:
        return None

    latest = date_cols[-1]
    val = pd.to_numeric(row.iloc[0][latest], errors="coerce")
    return val if pd.notna(val) else None


def fetch_zillow_data(zip_code: str = "60610") -> dict:
    """Download Zillow research CSVs and extract latest values for the ZIP."""
    print(f"[Zillow] Fetching research data for ZIP {zip_code}...")

    result = {}

    sources = [
        (ZILLOW_ZHVI_URL, "zip_zhvi"),
        (ZILLOW_ZORI_URL, "zip_zori"),
        (ZILLOW_SALES_URL, "zip_median_sale_price"),
        (ZILLOW_DOM_URL, "zip_median_days_on_market"),
    ]

    for url, field in sources:
        val = _download_zillow_csv(url, field, zip_code)
        result[field] = val
        status = f"{val:,.0f}" if val is not None else "N/A"
        print(f"  {field}: {status}")

    # Derived
    zhvi = result.get("zip_zhvi")
    zori = result.get("zip_zori")
    if zhvi and zori and zori > 0:
        result["zip_price_to_rent_ratio"] = zhvi / (zori * 12)
    else:
        result["zip_price_to_rent_ratio"] = None

    # YoY price change: download ZHVI again and compute
    try:
        resp = requests.get(ZILLOW_ZHVI_URL, timeout=60)
        resp.raise_for_status()
        df = pd.read_csv(StringIO(resp.text))
        row = df[df["RegionName"].astype(str) == zip_code]
        if not row.empty:
            date_cols = [c for c in df.columns if c[:4].isdigit()]
            if len(date_cols) >= 13:
                current = pd.to_numeric(row.iloc[0][date_cols[-1]], errors="coerce")
                year_ago = pd.to_numeric(row.iloc[0][date_cols[-13]], errors="coerce")
                if pd.notna(current) and pd.notna(year_ago) and year_ago > 0:
                    result["zip_yoy_price_change_pct"] = (current - year_ago) / year_ago
    except Exception:
        pass

    if "zip_yoy_price_change_pct" not in result:
        result["zip_yoy_price_change_pct"] = None

    print(f"  -> {sum(1 for v in result.values() if v is not None)}/{len(result)} fields populated")
    return result
