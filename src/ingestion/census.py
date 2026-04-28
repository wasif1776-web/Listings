"""US Census ACS 5-year data ingestion."""
from __future__ import annotations

import os
import requests
import pandas as pd

ACS_VARIABLES = {
    "B01002_001E": "tract_median_age",
    "B19013_001E": "tract_median_household_income",
    "B25003_001E": "tract_total_occupied_units",
    "B25003_002E": "tract_owner_occupied_units",
    "B25003_003E": "tract_renter_occupied_units",
    "B25035_001E": "tract_median_year_moved_in",
    "B11005_001E": "tract_total_households",
    "B11005_002E": "tract_households_with_children",
    "B01001_001E": "tract_total_population",
    "B25077_001E": "tract_median_home_value",
    "B25064_001E": "tract_median_gross_rent",
    "B25002_001E": "tract_total_housing_units",
    "B25002_003E": "tract_vacant_units",
    # Male 65+ age bands
    "B01001_020E": "tract_pop_m65_to_66",
    "B01001_021E": "tract_pop_m67_to_69",
    "B01001_022E": "tract_pop_m70_to_74",
    "B01001_023E": "tract_pop_m75_to_79",
    "B01001_024E": "tract_pop_m80_to_84",
    "B01001_025E": "tract_pop_m85_plus",
    # Female 65+ age bands
    "B01001_044E": "tract_pop_f65_to_66",
    "B01001_045E": "tract_pop_f67_to_69",
    "B01001_046E": "tract_pop_f70_to_74",
    "B01001_047E": "tract_pop_f75_to_79",
    "B01001_048E": "tract_pop_f80_to_84",
    "B01001_049E": "tract_pop_f85_plus",
    # Male 35-54
    "B01001_013E": "tract_pop_m35_to_39",
    "B01001_014E": "tract_pop_m40_to_44",
    "B01001_015E": "tract_pop_m45_to_49",
    "B01001_016E": "tract_pop_m50_to_54",
    # Female 35-54
    "B01001_037E": "tract_pop_f35_to_39",
    "B01001_038E": "tract_pop_f40_to_44",
    "B01001_039E": "tract_pop_f45_to_49",
    "B01001_040E": "tract_pop_f50_to_54",
}

STATE_FIPS = "17"
COUNTY_FIPS = "031"


def fetch_census_data(tract_geoids: list[str]) -> pd.DataFrame:
    """Fetch ACS 5-year estimates for the given tract GEOIDs."""
    print(f"[Census] Fetching ACS data for {len(tract_geoids)} tracts...")

    tracts = set()
    for geoid in tract_geoids:
        g = str(geoid)
        if len(g) >= 11:
            tracts.add(g[5:11])

    if not tracts:
        print("  -> No valid tract codes")
        return pd.DataFrame()

    api_key = os.environ.get("CENSUS_API_KEY", "")
    var_list = ",".join(ACS_VARIABLES.keys())
    tract_list = ",".join(sorted(tracts))

    for year in [2023, 2022, 2021]:
        url = f"https://api.census.gov/data/{year}/acs/acs5"
        params = {
            "get": f"NAME,{var_list}",
            "for": f"tract:{tract_list}",
            "in": f"state:{STATE_FIPS} county:{COUNTY_FIPS}",
        }
        if api_key:
            params["key"] = api_key

        try:
            resp = requests.get(url, params=params, timeout=60)
            if resp.ok:
                data = resp.json()
                if len(data) > 1:
                    print(f"  -> Using ACS {year} 5-year estimates")
                    break
        except Exception as e:
            print(f"  ACS {year} failed: {e}")
            continue
    else:
        print("  -> Census API unavailable")
        return pd.DataFrame()

    header = data[0]
    rows = data[1:]
    df = pd.DataFrame(rows, columns=header)

    df["tract_geoid"] = STATE_FIPS + COUNTY_FIPS + df["tract"]

    rename = {raw: canon for raw, canon in ACS_VARIABLES.items()}
    df = df.rename(columns=rename)

    numeric_cols = list(ACS_VARIABLES.values())
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Compute percentage fields
    pop = df["tract_total_population"].replace(0, float("nan"))
    m65_cols = [c for c in df.columns if c.startswith("tract_pop_m6") or c.startswith("tract_pop_m7") or c.startswith("tract_pop_m8")]
    f65_cols = [c for c in df.columns if c.startswith("tract_pop_f6") or c.startswith("tract_pop_f7") or c.startswith("tract_pop_f8")]
    df["tract_pct_65_plus"] = df[m65_cols + f65_cols].sum(axis=1) / pop

    m35_cols = [c for c in df.columns if c.startswith("tract_pop_m3") or c.startswith("tract_pop_m4") or c.startswith("tract_pop_m5")]
    f35_cols = [c for c in df.columns if c.startswith("tract_pop_f3") or c.startswith("tract_pop_f4") or c.startswith("tract_pop_f5")]
    df["tract_pct_35_to_54"] = df[m35_cols + f35_cols].sum(axis=1) / pop

    occ = df["tract_total_occupied_units"].replace(0, float("nan"))
    df["tract_pct_owner_occupied"] = df["tract_owner_occupied_units"] / occ
    df["tract_pct_renter_occupied"] = df["tract_renter_occupied_units"] / occ

    hh = df["tract_total_households"].replace(0, float("nan"))
    df["tract_pct_households_with_children"] = df["tract_households_with_children"] / hh

    hu = df["tract_total_housing_units"].replace(0, float("nan"))
    df["tract_vacancy_rate"] = df["tract_vacant_units"] / hu

    print(f"  -> {len(df)} tracts with census data")
    return df
