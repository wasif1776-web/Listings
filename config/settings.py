"""
Central configuration for the Listings pipeline.
All paths, constants, and API endpoints are defined here.
API keys are read from environment variables — never hardcoded.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

_ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(_ENV_PATH)

# ── Geography ────────────────────────────────────────────────────────────────

TARGET_ZIP = "60610"  # default; overridden at runtime by dashboard

# ── Paths ────────────────────────────────────────────────────────────────────

ROOT_DIR       = Path(__file__).parent.parent
DATA_DIR       = ROOT_DIR / "data"
RAW_DIR        = DATA_DIR / "raw"
PROCESSED_DIR  = DATA_DIR / "processed"
CANONICAL_DIR  = PROCESSED_DIR / "canonical"
OUTPUTS_DIR    = DATA_DIR / "outputs"
REFERENCE_DIR  = DATA_DIR / "reference"
CONFIG_DIR     = ROOT_DIR / "config"

TIGER_PATH           = REFERENCE_DIR / "tiger_60610.parquet"
ADDRESS_INDEX_PATH   = PROCESSED_DIR / "address_index.parquet"
MASTER_PARCELS_PATH  = PROCESSED_DIR / "master_parcels.parquet"
FEATURES_PATH        = PROCESSED_DIR / "features.parquet"
SCORED_LATEST_PATH   = OUTPUTS_DIR / "scored_latest.parquet"
LAST_RUN_META_PATH   = DATA_DIR / "last_run_metadata.json"

FIELD_MAPPINGS_PATH   = CONFIG_DIR / "field_mappings.yaml"
SOURCE_SCHEMAS_PATH   = CONFIG_DIR / "source_schemas.yaml"
SCORING_WEIGHTS_PATH  = CONFIG_DIR / "scoring_weights.yaml"

# ── API Keys (from environment) ───────────────────────────────────────────────

CENSUS_API_KEY   = os.environ.get("CENSUS_API_KEY", "")
PROPWIRE_API_KEY = os.environ.get("PROPWIRE_API_KEY", "")

# ── API Endpoints ─────────────────────────────────────────────────────────────

ASSESSOR_API_URL   = "https://datacatalog.cookcountyil.gov/resource/uzyt-m557.json"
ASSESSOR_CSV_URL   = "https://datacatalog.cookcountyil.gov/api/views/uzyt-m557/rows.csv?accessType=DOWNLOAD"
RECORDER_DOMAIN    = "datacatalog.cookcountyil.gov"
RECORDER_DEEDS_ID  = "v923-b6by"
TREASURER_TAX_ID   = "s7th-mxhp"
PERMITS_DOMAIN     = "data.cityofchicago.org"
PERMITS_DATASET_ID = "ydr8-5enu"
VIOLATIONS_DOMAIN  = "data.cityofchicago.org"
VIOLATIONS_DATASET_ID = "22u3-xenr"
CENSUS_GEOCODER_URL = "https://geocoding.geo.census.gov/geocoder/geographies/addressbatch"
PROPWIRE_API_URL   = "https://api.propwire.com/v1/properties"

ZILLOW_ZHVI_URL = (
    "https://files.zillowstatic.com/research/public_csvs/zhvi/"
    "Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
)
ZILLOW_ZORI_URL = (
    "https://files.zillowstatic.com/research/public_csvs/zori/"
    "Zip_zori_uc_sfrcondomfr_sm_month.csv"
)
ZILLOW_SALES_URL = (
    "https://files.zillowstatic.com/research/public_csvs/median_sale_price/"
    "Zip_median_sale_price_uc_sfrcondo_sm_month.csv"
)
ZILLOW_DOM_URL = (
    "https://files.zillowstatic.com/research/public_csvs/days_to_pending/"
    "Zip_days_to_pending_uc_sfrcondo_sm_month.csv"
)
HUD_FMR_URL = (
    "https://www.huduser.gov/portal/datasets/fmr/fmr2025/FY25_FMRs.xlsx"
)

# ── Scoring ───────────────────────────────────────────────────────────────────

CHANGE_FLAG_THRESHOLD = 5      # Minimum point change to set change_flag = "score_changed"
FUZZY_MATCH_THRESHOLD = 88     # Minimum rapidfuzz token_sort_ratio to accept an address match

# ── Source Refresh Thresholds (days) ─────────────────────────────────────────

ASSESSOR_MAX_AGE_DAYS   = 90
CENSUS_MAX_AGE_DAYS     = 180
HUD_MAX_AGE_DAYS        = 180
PROPWIRE_MAX_AGE_DAYS   = 28

# ── Socrata Rate Limiting ─────────────────────────────────────────────────────

SOCRATA_REQUEST_LIMIT   = 50_000   # Max rows per Socrata API call
SOCRATA_TIMEOUT_SECONDS = 60

# ── PropWire ──────────────────────────────────────────────────────────────────

PROPWIRE_MONTHLY_LIMIT  = 10_000   # Free tier monthly record cap

# ── Parquet Storage ───────────────────────────────────────────────────────────

PARQUET_COMPRESSION = "snappy"

# ── Dashboard ─────────────────────────────────────────────────────────────────

DASHBOARD_MAP_CENTER = {"lat": 41.8981, "lon": -87.6298}   # ZIP 60610 centroid
DASHBOARD_MAP_ZOOM   = 13

# ── Per-ZIP Helpers ──────────────────────────────────────────────────────────

DATA_STALENESS_DAYS = 30


def scored_path_for_zip(zip_code: str) -> Path:
    """Return the parquet path for a given ZIP code."""
    return OUTPUTS_DIR / f"{zip_code}.parquet"
