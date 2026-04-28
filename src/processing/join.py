"""Join all data sources into a master property table."""
from __future__ import annotations

import re

import pandas as pd


def _normalize_address(addr: str) -> str:
    """Normalize address for matching: uppercase, strip suffix, collapse spaces."""
    if not isinstance(addr, str):
        return ""
    addr = addr.upper().strip()
    addr = re.sub(r"\s+", " ", addr)
    return addr


def _strip_street_suffix(addr: str) -> str:
    """Remove common street suffixes for fuzzy joining."""
    suffixes = (
        " ST", " AVE", " BLVD", " DR", " CT", " PL", " TER", " TERR",
        " RD", " WAY", " LN", " CIR", " PKY", " PKWY",
    )
    upper = addr.upper().strip()
    for s in suffixes:
        if upper.endswith(s):
            return upper[: -len(s)]
    return upper


def _add_unit_from_pin(df: pd.DataFrame) -> pd.DataFrame:
    """Append unit identifier from PIN for multi-unit buildings."""
    df = df.copy()
    pin_str = df["pin"].astype(str)
    df["pin_suffix"] = pin_str.str[-4:]
    df["pin_parcel"] = pin_str.str[6:10]
    df["building_address"] = df["address"]

    addr_pin_counts = df.groupby("address")["pin"].transform("count")
    is_multi = addr_pin_counts > 1

    # For condos (suffix != 0000), use block+suffix to handle buildings
    # at the same address in different blocks
    has_unit = is_multi & (df["pin_suffix"] != "0000")
    unit_id = pin_str.str[4:10] + pin_str.str[-4:]
    df.loc[has_unit, "address"] = (
        df.loc[has_unit, "address"] + " #" + df.loc[has_unit, "pin_suffix"]
    )

    # Check if still duplicated after first pass, use full PIN mid-section
    addr_counts2 = df.groupby("address")["pin"].transform("count")
    still_duped_unit = (addr_counts2 > 1) & has_unit
    if still_duped_unit.any():
        df.loc[still_duped_unit, "address"] = (
            df.loc[still_duped_unit, "building_address"]
            + " #" + pin_str.loc[still_duped_unit].str[4:10]
            + "-" + df.loc[still_duped_unit, "pin_suffix"]
        )

    # For remaining duplicates (suffix == 0000), use the parcel portion of PIN
    addr_counts3 = df.groupby("address")["pin"].transform("count")
    still_duped = (addr_counts3 > 1) & (df["pin_suffix"] == "0000")
    if still_duped.any():
        df.loc[still_duped, "address"] = (
            df.loc[still_duped, "address"] + " U" + df.loc[still_duped, "pin_parcel"]
        )

    df = df.drop(columns=["pin_parcel"])
    return df


def build_master(
    locations: pd.DataFrame,
    characteristics: pd.DataFrame,
    sales: pd.DataFrame,
    assessed_values: pd.DataFrame,
    permits: pd.DataFrame,
    violations: pd.DataFrame,
    census: pd.DataFrame,
    zillow: dict,
    hud: dict,
    pin_set: set[str],
) -> pd.DataFrame:
    """Merge all sources into a single property table keyed by PIN."""

    # --- Base: Locations ---
    master = locations.copy()
    master = master.rename(columns={
        "property_address": "address",
        "property_city": "city",
        "property_zip": "zip_code",
        "mailing_address": "owner_mailing_address",
        "mailing_city": "owner_mailing_city",
        "mailing_state": "owner_mailing_state",
        "mailing_zip": "owner_mailing_zip",
        "township_name": "township_name",
        "nbhd": "neighborhood_code",
        "township": "township_code",
    })
    master["latitude"] = pd.to_numeric(master["latitude"], errors="coerce")
    master["longitude"] = pd.to_numeric(master["longitude"], errors="coerce")
    print(f"  Base locations: {len(master):,} rows")

    # --- Characteristics ---
    if not characteristics.empty:
        chars = characteristics[characteristics["pin"].isin(pin_set)].copy()
        # Take the most recent tax_year per PIN
        chars["tax_year"] = pd.to_numeric(chars["tax_year"], errors="coerce")
        chars = chars.sort_values("tax_year", ascending=False).groupby("pin").first().reset_index()

        char_cols = {
            "class": "property_class",
            "beds": "num_bedrooms",
            "fbath": "num_bathrooms",
            "rooms": "num_rooms",
            "bldg_sf": "building_sq_ft",
            "hd_sf": "land_sq_ft",
            "age": "building_age",
            "garage_indicator": "garage_indicator",
            "pri_est_bldg": "assessed_value_building",
            "pri_est_land": "assessed_value_land",
            "total_units": "total_units",
            "tax_year": "tax_year",
            "addr": "char_addr",
        }
        chars = chars.rename(columns=char_cols)
        keep = ["pin"] + [v for v in char_cols.values() if v in chars.columns]
        chars = chars[keep]

        for col in ["num_bedrooms", "num_bathrooms", "num_rooms", "building_sq_ft",
                     "land_sq_ft", "building_age", "assessed_value_building",
                     "assessed_value_land", "total_units"]:
            if col in chars.columns:
                chars[col] = pd.to_numeric(chars[col], errors="coerce")

        master = master.merge(chars, on="pin", how="left")
        print(f"  + Characteristics: {chars['pin'].nunique():,} PINs matched")

    # --- Assessed Values -> estimated_market_value ---
    if not assessed_values.empty:
        master = master.merge(assessed_values, on="pin", how="left")
        # Cook County residential assessment is ~10% of market value
        master["estimated_market_value"] = master["assessed_value"] * 10
        master = master.drop(columns=["assessed_value"], errors="ignore")
        matched = master["estimated_market_value"].notna().sum()
        print(f"  + Assessed values: {matched:,} PINs with market value")

    # --- Sales ---
    if not sales.empty:
        master = master.merge(sales, on="pin", how="left")
        matched = master["sale_date_1"].notna().sum()
        print(f"  + Sales: {matched:,} PINs with sale history")

    # --- Permits (join by building address) ---
    if not permits.empty and "address" in master.columns:
        master["_addr_key"] = master["address"].apply(_strip_street_suffix)
        permits["_addr_key"] = permits["permit_address"].apply(_strip_street_suffix)
        master = master.merge(
            permits[["_addr_key", "permit_count_5yr", "latest_permit_date"]],
            on="_addr_key", how="left",
        )
        master = master.drop(columns=["_addr_key"])
        permits = permits.drop(columns=["_addr_key"])
        matched = master["permit_count_5yr"].notna().sum()
        print(f"  + Permits: {matched:,} PINs with permit data")

    # --- Violations (join by building address) ---
    if not violations.empty and "address" in master.columns:
        master["_addr_key"] = master["address"].apply(_normalize_address)
        violations["_addr_key"] = violations["violation_address"].apply(_normalize_address)
        master = master.merge(
            violations[["_addr_key", "violation_count_open"]],
            on="_addr_key", how="left",
        )
        master = master.drop(columns=["_addr_key"])
        matched = master["violation_count_open"].notna().sum()
        print(f"  + Violations: {matched:,} PINs with violation data")

    # --- Census (join by tract_geoid) ---
    if not census.empty and "tract_geoid" in master.columns:
        census_cols = [c for c in census.columns
                       if c.startswith("tract_") or c == "tract_geoid"]
        master = master.merge(census[census_cols], on="tract_geoid", how="left")
        matched = master["tract_median_household_income"].notna().sum()
        print(f"  + Census: {matched:,} PINs with tract data")

    # --- Zillow (ZIP-level, broadcast) ---
    if zillow:
        for field, val in zillow.items():
            if val is not None:
                master[field] = val
        print(f"  + Zillow: {sum(1 for v in zillow.values() if v is not None)} fields")

    # --- HUD (ZIP-level, broadcast) ---
    if hud:
        for field, val in hud.items():
            if val is not None:
                master[field] = val
        print(f"  + HUD FMR: {sum(1 for v in hud.values() if v is not None)} fields")

    # --- Add unit numbers from PIN suffix ---
    master = _add_unit_from_pin(master)

    # Fill permit/violation NaN with 0
    master["permit_count_5yr"] = master.get("permit_count_5yr", 0)
    if "permit_count_5yr" in master.columns:
        master["permit_count_5yr"] = master["permit_count_5yr"].fillna(0).astype(int)
    master["violation_count_open"] = master.get("violation_count_open", 0)
    if "violation_count_open" in master.columns:
        master["violation_count_open"] = master["violation_count_open"].fillna(0).astype(int)

    return master
