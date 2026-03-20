# Listings

A real estate propensity scoring system for Chicago zip code 60610, built on free and low-cost public data sources.

## Overview

This project ingests property, ownership, tax, permit, and demographic data from free public sources, joins them at the parcel level, and produces ranked propensity scores for homeowners likely to sell, buy, upsize, downsize, or relocate.

## Repository Structure

```
listings/
├── docs/               # Requirements, architecture, data dictionary
├── data/
│   ├── raw/            # Downloaded source files (never modify)
│   ├── processed/      # Cleaned and joined datasets
│   └── outputs/        # Scored property lists and dashboard exports
├── src/
│   ├── ingestion/      # Per-source data fetch scripts
│   ├── processing/     # Cleaning, joining, feature engineering
│   ├── scoring/        # Propensity model logic
│   └── dashboard/      # Dashboard app
├── notebooks/          # Exploratory analysis
├── tests/              # Unit and integration tests
└── config/             # Settings, field mappings (no secrets)
```

## Data Sources

| Source | Cost | Key Data |
|---|---|---|
| Cook County Assessor Open Data | Free | Property characteristics, AVM, sale history, tax exemptions |
| Cook County Open Data Portal | Free | Deed transfers, zoning, violations |
| Chicago Data Portal | Free | Building permits, code violations |
| US Census ACS | Free | Block-level demographics, income, household size |
| Zillow Research CSVs | Free | ZIP-level median price, days on market, inventory |
| HUD Fair Market Rents | Free | Rent estimates by bedroom count |
| PropWire | Free tier | Owner details, skip tracing |

## Target

ZIP code: **60610** (Near North Side / Gold Coast, Chicago IL)

## Docs

- [Product Requirements (PRD)](docs/PRD.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Data Dictionary](docs/DATA_DICTIONARY.md)
