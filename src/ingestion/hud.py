"""HUD Fair Market Rent data ingestion."""
from __future__ import annotations

import requests
import pandas as pd
from io import BytesIO


HUD_FMR_URL = (
    "https://www.huduser.gov/portal/datasets/fmr/fmr2025/FY25_FMRs.xlsx"
)


def fetch_hud_data(zip_code: str = "60610") -> dict:
    """Download HUD FMR data and extract values for the ZIP."""
    print(f"[HUD] Fetching Fair Market Rents for ZIP {zip_code}...")

    try:
        resp = requests.get(HUD_FMR_URL, timeout=120)
        resp.raise_for_status()
        df = pd.read_excel(BytesIO(resp.content), engine="openpyxl")
    except Exception as e:
        print(f"  Warning: HUD download failed: {e}")
        print("  Using Chicago-metro FY2025 fallback values")
        return {
            "fmr_studio": 1159,
            "fmr_1br": 1260,
            "fmr_2br": 1444,
            "fmr_3br": 1844,
            "fmr_4br": 2068,
        }

    zip_col = None
    for c in df.columns:
        if "zip" in str(c).lower():
            zip_col = c
            break

    if zip_col is None:
        print("  Warning: no ZIP column found, using fallback")
        return {
            "fmr_studio": 1159,
            "fmr_1br": 1260,
            "fmr_2br": 1444,
            "fmr_3br": 1844,
            "fmr_4br": 2068,
        }

    row = df[df[zip_col].astype(str).str.startswith(zip_code)]
    if row.empty:
        print(f"  Warning: ZIP {zip_code} not found, using fallback")
        return {
            "fmr_studio": 1159,
            "fmr_1br": 1260,
            "fmr_2br": 1444,
            "fmr_3br": 1844,
            "fmr_4br": 2068,
        }

    r = row.iloc[0]
    fmr_cols = sorted([c for c in df.columns if "fmr" in str(c).lower() or "br" in str(c).lower()])

    result = {}
    for i, key in enumerate(["fmr_studio", "fmr_1br", "fmr_2br", "fmr_3br", "fmr_4br"]):
        if i < len(fmr_cols):
            result[key] = pd.to_numeric(r[fmr_cols[i]], errors="coerce")
        else:
            result[key] = None

    for k, v in result.items():
        print(f"  {k}: ${v:,.0f}" if pd.notna(v) else f"  {k}: N/A")

    return result
