"""Listings pipeline -- ingest, join, engineer features, score."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd

from config.settings import (
    RAW_DIR, PROCESSED_DIR, OUTPUTS_DIR,
    PARQUET_COMPRESSION, scored_path_for_zip,
)
from src.ingestion.assessor import (
    fetch_locations, fetch_characteristics, fetch_sales,
    fetch_assessed_values, pivot_sales, get_latest_assessed_values,
)
from src.ingestion.permits import fetch_permits
from src.ingestion.violations import fetch_violations
from src.ingestion.census import fetch_census_data
from src.ingestion.zillow import fetch_zillow_data
from src.ingestion.hud import fetch_hud_data
from src.processing.join import build_master
from src.processing.feature_engineer import add_derived_fields
from src.scoring.engine import score_all


def _compute_bounds(locations: pd.DataFrame) -> tuple[float, float, float, float]:
    """Compute lat/lon bounding box from locations data with a small buffer."""
    lat = pd.to_numeric(locations["latitude"], errors="coerce").dropna()
    lon = pd.to_numeric(locations["longitude"], errors="coerce").dropna()
    buffer = 0.005
    return (
        lat.min() - buffer,
        lat.max() + buffer,
        lon.min() - buffer,
        lon.max() + buffer,
    )


def run_pipeline(zip_code: str = "60610", progress_callback=None) -> Path:
    """Run the full pipeline for a single ZIP code.

    Returns the path to the saved parquet file.
    If *progress_callback* is provided, it will be called with (step, message)
    so the dashboard can update a progress bar.
    """
    def _progress(step: int, total: int, msg: str):
        print(msg)
        if progress_callback:
            progress_callback(step, total, msg)

    for d in [RAW_DIR, PROCESSED_DIR, OUTPUTS_DIR]:
        d.mkdir(parents=True, exist_ok=True)

    total_steps = 5

    # -- Step 1: Ingestion ----
    _progress(1, total_steps, f"Step 1/5: Ingesting data for ZIP {zip_code}...")

    locations = fetch_locations(zip_code)
    pin_set = set(locations["pin"].tolist())
    print(f"\nProperty universe: {len(pin_set):,} PINs")

    prefixes = set(p[:4] for p in pin_set)
    main_prefix = max(prefixes, key=lambda p: sum(1 for pin in pin_set if pin.startswith(p)))
    print(f"Primary PIN prefix: {main_prefix}\n")

    characteristics = fetch_characteristics(main_prefix)
    raw_sales = fetch_sales(main_prefix)
    raw_values = fetch_assessed_values(main_prefix)

    sales = pivot_sales(raw_sales, pin_set)
    values = get_latest_assessed_values(raw_values, pin_set)

    lat_min, lat_max, lon_min, lon_max = _compute_bounds(locations)
    print(f"\nBounding box: lat [{lat_min:.4f}, {lat_max:.4f}], lon [{lon_min:.4f}, {lon_max:.4f}]")

    print()
    permits = fetch_permits(lat_min, lat_max, lon_min, lon_max, zip_code)
    print()
    violations = fetch_violations(lat_min, lat_max, lon_min, lon_max, zip_code)

    print()
    tract_geoids = locations["tract_geoid"].dropna().unique().tolist()
    census = fetch_census_data(tract_geoids)

    print()
    zillow = fetch_zillow_data(zip_code)

    print()
    hud = fetch_hud_data(zip_code)

    # -- Step 2: Join ----
    _progress(2, total_steps, "Step 2/5: Joining data sources...")

    master = build_master(
        locations, characteristics, sales, values,
        permits, violations, census, zillow, hud, pin_set,
    )
    print(f"\nMaster table: {len(master):,} rows x {len(master.columns)} columns")

    # -- Step 3: Feature Engineering ----
    _progress(3, total_steps, "Step 3/5: Engineering features...")

    master = add_derived_fields(master)

    # -- Step 4: Scoring ----
    _progress(4, total_steps, "Step 4/5: Scoring properties...")

    master = score_all(master)

    # -- Step 5: Save ----
    _progress(5, total_steps, "Step 5/5: Saving output...")

    out_path = scored_path_for_zip(zip_code)
    master.to_parquet(out_path, compression=PARQUET_COMPRESSION, index=False)
    print(f"Saved {len(master):,} properties -> {out_path}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    key_fields = [
        "property_class", "num_bedrooms", "num_bathrooms", "building_sq_ft",
        "estimated_market_value", "sale_date_1", "years_owned",
        "estimated_equity_pct", "absentee_owner_flag", "owner_occupied_flag",
    ]
    print("\nField coverage:")
    for f in key_fields:
        if f in master.columns:
            pct = master[f].notna().mean() * 100
            non_default = master[f].notna().sum()
            print(f"  {f}: {pct:.1f}% ({non_default:,}/{len(master):,})")

    print("\nScore distributions:")
    for sc in sorted(c for c in master.columns if c.startswith("score_")):
        vals = master[sc].dropna()
        print(
            f"  {sc}: min={vals.min():.0f} max={vals.max():.0f} "
            f"mean={vals.mean():.1f} unique={vals.nunique()}"
        )

    sell_col = "score_likely_to_sell"
    if sell_col in master.columns:
        top = master.nlargest(5, sell_col)
        print(f"\nTop 5 by {sell_col}:")
        show_cols = ["pin", "address", sell_col, "estimated_market_value", "years_owned"]
        show_cols = [c for c in show_cols if c in top.columns]
        print(top[show_cols].to_string(index=False))

    return out_path


def main():
    zip_code = sys.argv[1] if len(sys.argv) > 1 else "60610"
    run_pipeline(zip_code)


if __name__ == "__main__":
    main()
