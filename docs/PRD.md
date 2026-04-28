# Product Requirements Document
## Listings — Real Estate Propensity Scoring System
**Version:** 2.0
**Date:** 2026-03-26
**Target ZIP:** 60610 (Near North Side / Gold Coast, Chicago IL)
**Status:** Active

---

## 1. Problem Statement

Real estate agents working a specific Chicago market need to identify which homeowners are most likely to sell, buy, upsize, downsize, or relocate — before those homeowners list on MLS. Manual prospecting is time-consuming and low-signal. The goal is to build a data-driven propensity scoring system that ranks every property in ZIP 60610 by likelihood of a near-term real estate event, using free public data sources supplemented by paid property intelligence platforms for maximum accuracy.

---

## 2. Goals & Non-Goals

**Goals**
- Ingest property, ownership, tax, permit, and demographic data for all residential parcels in ZIP 60610
- Join all sources at the parcel (PIN / address) level into a single enriched property record
- Compute propensity scores for 10 distinct use cases
- Produce two outputs: (1) a ranked, exportable CSV/spreadsheet for agent review and (2) a dashboard for interactive exploration
- Leverage PropStream ($99/mo) for high-signal property intelligence (pre-foreclosure, life events, mortgage details, listing history) alongside free public data sources

**Non-Goals**
- Automated outreach / CRM sync
- Nationwide or multi-ZIP coverage in v1
- Real-time data (batch/monthly refresh is acceptable)

---

## 3. Users

| User | Need |
|---|---|
| Real estate agent (primary) | Ranked list of warm leads by use case; exportable for outreach |
| Agent / analyst (secondary) | Dashboard to filter, explore, and understand the data behind scores |

---

## 4. Data Sources

### 4.1 Cook County Assessor Open Data
**URL:** https://www.cookcountyassessor.com/opendata
**Cost:** Free — REST API + bulk CSV export
**Refresh:** Annual (assessments) / Quarterly (sales)
**Join Key:** PIN (Parcel Identification Number), Address

| Field | Description | Use Cases |
|---|---|---|
| `pin` | 14-digit Parcel ID | Join key |
| `address` | Property street address | Join key |
| `city` | City | Filter |
| `zip_code` | ZIP code | Filter (60610) |
| `property_class` | Property class code (e.g., 202 = SFR condo) | Property type |
| `township_code` | Township identifier | Geo context |
| `year_built` | Year structure was built | Age of property |
| `building_sq_ft` | Living area square footage | Size |
| `land_sq_ft` | Lot size in sq ft | Lot size |
| `num_bedrooms` | Bedroom count | Size / family fit |
| `num_bathrooms` | Bathroom count | Size / family fit |
| `num_rooms` | Total room count | Size |
| `garage_indicator` | Garage present (Y/N) | Amenity |
| `estimated_market_value` | Assessor AVM | Equity calculation |
| `assessed_value_building` | Assessed value (structure) | Tax base |
| `assessed_value_land` | Assessed value (land) | Tax base |
| `tax_year` | Tax year of assessment | Recency |
| `homeowner_exemption` | Homeowner exemption claimed (Y/N → owner-occupied proxy) | Owner-occupied flag |
| `senior_exemption` | Senior exemption claimed (Y/N → age proxy) | Age signal |
| `senior_freeze_exemption` | Senior freeze exemption (Y/N) | Fixed-income signal |
| `sale_date_1` | Most recent sale date | Years owned |
| `sale_price_1` | Most recent sale price | Equity calculation |
| `sale_date_2` | Prior sale date | Sale history |
| `sale_price_2` | Prior sale price | Sale history |
| `sale_date_3` | Third most recent sale date | Sale frequency |
| `sale_price_3` | Third most recent sale price | Sale frequency |
| `deed_type` | Deed type at last sale (warranty, quitclaim, etc.) | Transaction type |

### 4.2 Cook County Open Data Portal (Recorder / Treasurer)
**URL:** https://datacatalog.cookcountyil.gov
**Cost:** Free — Socrata API
**Refresh:** Weekly (deed recordings) / Monthly (tax delinquency)
**Join Key:** PIN, Address

| Field | Description | Use Cases |
|---|---|---|
| `pin` | Parcel ID | Join key |
| `grantor` | Seller name at last deed transfer | Owner history |
| `grantee` | Buyer / current owner name | Owner name |
| `deed_date` | Date of deed recording | Transfer recency |
| `instrument_type` | Deed type (Warranty, Quitclaim, Trustee, etc.) | Trust / LLC flag |
| `grantee_mailing_address` | Owner mailing address | Absentee flag |
| `grantee_mailing_city` | Owner mailing city | Out-of-state flag |
| `grantee_mailing_state` | Owner mailing state | Out-of-state flag |
| `tax_delinquency_flag` | Property has delinquent taxes (Y/N) | Distress signal |
| `delinquent_tax_amount` | Dollar amount of delinquent taxes | Distress severity |
| `delinquent_tax_years` | Number of years with delinquent taxes | Distress duration |
| `tax_annual_amount` | Annual property tax bill | Carrying cost |

### 4.3 Chicago Data Portal — Building Permits
**URL:** https://data.cityofchicago.org/Buildings/Building-Permits
**Cost:** Free — Socrata API
**Refresh:** Daily
**Join Key:** Address (fuzzy match to PIN)

| Field | Description | Use Cases |
|---|---|---|
| `permit_number` | Permit ID | Deduplication |
| `permit_type` | Type (PERMIT - RENOVATION, NEW CONSTRUCTION, etc.) | Renovation signal |
| `issue_date` | Permit issue date | Recency of activity |
| `total_fee` | Permit fee (proxy for scope/value of work) | Renovation scale |
| `work_description` | Free-text description of permitted work | Renovation type |
| `address` | Property address | Join key |
| `latest_permit_date` | Most recent permit date (derived) | Prep-to-sell signal |
| `permit_count_5yr` | Number of permits in last 5 years (derived) | Renovation activity |

### 4.4 Chicago Data Portal — Building Violations
**URL:** https://data.cityofchicago.org/Buildings/Building-Violations
**Cost:** Free — Socrata API
**Refresh:** Daily
**Join Key:** Address

| Field | Description | Use Cases |
|---|---|---|
| `violation_date` | Date of violation | Distress recency |
| `violation_code` | Code violation type | Distress type |
| `violation_status` | Status (open, complied, dismissed) | Active distress |
| `violation_count_open` | Number of open violations (derived) | Distress severity |
| `address` | Property address | Join key |

### 4.5 US Census American Community Survey (ACS)
**URL:** https://api.census.gov/data (5-Year ACS, table B-series)
**Cost:** Free — REST API (key required, free to obtain)
**Refresh:** Annual
**Join Key:** Census Tract / Block Group → mapped to address via TIGER shapefiles

| Field | Description | Use Cases |
|---|---|---|
| `tract_median_age` | Median age of residents in census tract | Age / life stage |
| `tract_median_household_income` | Median HH income | Income proxy |
| `tract_pct_owner_occupied` | % owner-occupied housing units | Neighborhood type |
| `tract_pct_renter_occupied` | % renter-occupied housing units | Investor signal |
| `tract_median_length_of_residence` | Median years at same address | Tenure signal |
| `tract_pct_households_with_children` | % HH with children under 18 | Life stage |
| `tract_pct_65_plus` | % population 65+ | Senior signal |
| `tract_pct_35_to_54` | % population 35–54 | Move-up buyer signal |
| `tract_median_home_value` | Median home value in tract | Price context |
| `tract_median_gross_rent` | Median gross rent in tract | Rent AVM proxy |
| `tract_vacancy_rate` | % vacant housing units | Market health |
| `block_group_geoid` | Block group identifier | Join key |

### 4.6 Zillow Research Data
**URL:** https://www.zillow.com/research/data/
**Cost:** Free — CSV download (no API)
**Refresh:** Monthly
**Join Key:** ZIP code

| Field | Description | Use Cases |
|---|---|---|
| `zip_median_sale_price` | Median sale price in ZIP | Market context |
| `zip_median_days_on_market` | Median DOM in ZIP | Market heat |
| `zip_pct_listings_price_cut` | % of active listings with price cut | Market softness |
| `zip_inventory` | Active listing count | Supply signal |
| `zip_yoy_price_change_pct` | Year-over-year median price change | Appreciation rate |
| `zip_median_list_price` | Median list price | Pricing context |
| `zip_zhvi` | Zillow Home Value Index | Benchmark AVM |
| `zip_zori` | Zillow Observed Rent Index | Rent AVM |
| `zip_price_to_rent_ratio` | Price-to-rent ratio (derived: ZHVI / ZORI×12) | Investor signal |

### 4.7 HUD Fair Market Rents
**URL:** https://www.huduser.gov/portal/datasets/fmr.html
**Cost:** Free — annual CSV
**Refresh:** Annual (federal fiscal year)
**Join Key:** ZIP / Metro Area

| Field | Description | Use Cases |
|---|---|---|
| `fmr_studio` | Fair market rent, studio | Rent AVM |
| `fmr_1br` | Fair market rent, 1 bedroom | Rent AVM |
| `fmr_2br` | Fair market rent, 2 bedroom | Rent AVM |
| `fmr_3br` | Fair market rent, 3 bedroom | Rent AVM |
| `fmr_4br` | Fair market rent, 4 bedroom | Rent AVM |

### 4.8 PropWire (Free Tier)
**URL:** https://www.propwire.com
**Cost:** Free — up to 10,000 records/month
**Refresh:** On demand
**Join Key:** Address / PIN

| Field | Description | Use Cases |
|---|---|---|
| `owner_name` | Owner full name | Identity |
| `owner_mailing_address` | Owner mailing address | Absentee flag |
| `owner_mailing_city` | Owner mailing city | Out-of-state flag |
| `owner_mailing_state` | Owner mailing state | Out-of-state flag |
| `absentee_owner_flag` | Owner does not live at property | Absentee signal |
| `corporate_owner_flag` | Owner is LLC, trust, or corporation | Investor flag |
| `portfolio_size` | Number of properties owned by same owner | Investor flag |
| `estimated_equity_pct` | Estimated equity % (PropWire calculated) | Equity signal |
| `estimated_equity_dollar` | Estimated equity $ amount | Equity signal |
| `open_lien_count` | Number of open liens | Financial distress |
| `mortgage_origination_date` | Date of most recent mortgage | Loan age |
| `mortgage_amount` | Original mortgage amount | LTV calc |
| `mortgage_type` | Fixed, ARM, etc. | Rate reset risk |
| `lender_name` | Lender at origination | Context |
| `skip_trace_phone` | Owner phone (if skip traced, $0.10/record) | Outreach |
| `skip_trace_email` | Owner email (if skip traced) | Outreach |

### 4.9 PropStream (Paid — $99/mo)
**URL:** https://www.propstream.com
**Cost:** $99/month — unlimited searches, bulk export, API access
**Refresh:** Daily (foreclosure/listing data) / Monthly (mortgage/ownership)
**Join Key:** Address / APN (PIN equivalent)

#### 4.9.1 Pre-Foreclosure & Distress

| Field | Description | Use Cases |
|---|---|---|
| `nod_flag` | Notice of Default filed (Y/N) | Strongest sell signal |
| `lis_pendens_flag` | Lis pendens (lawsuit pending) filed (Y/N) | Legal distress |
| `foreclosure_status` | Status: pre-foreclosure, auction, REO, none | Distress stage |
| `auction_date` | Scheduled foreclosure auction date | Urgency / timeline |
| `default_amount` | Dollar amount in default | Distress severity |

#### 4.9.2 Life Event Triggers

| Field | Description | Use Cases |
|---|---|---|
| `probate_flag` | Property in probate (Y/N) | Inherited property — likely to sell |
| `divorce_flag` | Owner involved in divorce filing (Y/N) | Forced sale signal |
| `inherited_flag` | Property recently inherited (Y/N) | New owner may sell |
| `death_in_household_flag` | Death recorded at property address (Y/N) | Life transition |

#### 4.9.3 Enhanced Mortgage Data

| Field | Description | Use Cases |
|---|---|---|
| `estimated_loan_balance` | Current estimated mortgage balance | LTV / equity calc |
| `ltv_ratio` | Loan-to-value ratio (current) | Equity signal |
| `interest_rate` | Mortgage interest rate | Rate sensitivity |
| `rate_type` | Fixed vs. ARM (with reset date if ARM) | Rate reset risk |
| `refi_count` | Number of refinances on record | Financial activity |
| `second_mortgage_flag` | Second mortgage / HELOC present (Y/N) | Leverage signal |
| `second_mortgage_amount` | Second mortgage balance | Total debt calc |

#### 4.9.4 Listing History (MLS-Derived)

| Field | Description | Use Cases |
|---|---|---|
| `prev_listed_flag` | Property was previously listed (Y/N) | Re-list signal |
| `expired_listing_flag` | Most recent listing expired or was withdrawn (Y/N) | Failed sale — likely to re-list |
| `last_list_date` | Date of most recent listing | Recency of intent |
| `last_list_price` | Most recent list price | Pricing context |
| `days_since_delisted` | Days since listing expired/withdrawn | Re-list timing |
| `listing_count` | Total number of times property has been listed | Sale difficulty |

#### 4.9.5 Property-Level AVM

| Field | Description | Use Cases |
|---|---|---|
| `propstream_avm` | PropStream automated valuation | Real-time equity calc |
| `avm_confidence_score` | Confidence level of the AVM estimate | Data quality |
| `avm_vs_assessed_pct` | `(propstream_avm - assessed_value) / assessed_value` | Value gap signal |

---

## 5. Derived / Engineered Fields

These fields are computed during the processing step from the raw source data above.

| Field | Formula / Logic | Use Cases |
|---|---|---|
| `years_owned` | `today - sale_date_1` in years | Long tenure signal |
| `estimated_equity_pct` | `(estimated_market_value - mortgage_amount) / estimated_market_value` | Equity signal |
| `estimated_equity_dollar` | `estimated_market_value - mortgage_amount` | Equity signal |
| `absentee_owner_flag` | `grantee_mailing_address != property_address` | Absentee signal |
| `out_of_state_flag` | `grantee_mailing_state != 'IL'` | Absentee severity |
| `owner_occupied_flag` | `homeowner_exemption == True` | Occupancy |
| `investor_flag` | `corporate_owner_flag OR portfolio_size > 1` | Investor signal |
| `senior_flag` | `senior_exemption == True OR senior_freeze_exemption == True` | Age proxy |
| `tax_delinquency_flag` | From Cook County Treasurer | Distress signal |
| `recent_permit_flag` | `latest_permit_date > today - 2yr` | Prep-to-sell signal |
| `open_violation_flag` | `violation_count_open > 0` | Distress signal |
| `price_to_rent_ratio` | `estimated_market_value / (fmr_Nbr * 12)` using bedroom count | Investor calc |
| `appreciation_vs_zip` | `(estimated_market_value - sale_price_1) / sale_price_1 - zip_yoy_price_change_pct` | Relative gain |
| `sale_count` | Count of non-null sale_date fields | Transaction frequency |
| `life_event_flag` | `probate_flag OR divorce_flag OR inherited_flag OR death_in_household_flag` | Any life event trigger |
| `distress_flag` | `nod_flag OR lis_pendens_flag OR foreclosure_status != 'none'` | Any pre-foreclosure distress |
| `total_debt` | `estimated_loan_balance + second_mortgage_amount` | True leverage |
| `true_ltv` | `total_debt / propstream_avm` (uses real-time AVM) | Accurate equity position |
| `negative_equity_flag` | `true_ltv > 1.0` | Underwater signal |
| `rate_reset_risk_flag` | `rate_type == 'ARM' AND mortgage_origination_date > today - 5yr` | ARM reset window |
| `failed_listing_flag` | `expired_listing_flag == True AND days_since_delisted <= 365` | Recent failed sale |

---

## 6. Use Case Scoring Model

Each property receives a score (0–100) per use case. Scores are computed by summing weighted signals and normalizing to 0–100.

### 6.1 Likely to Sell

| Signal | Points | Source |
|---|---|---|
| `nod_flag == True` | +25 | PropStream |
| `life_event_flag == True` | +20 | PropStream (derived) |
| `failed_listing_flag == True` | +20 | PropStream (derived) |
| `tax_delinquency_flag == True` | +15 | Cook County |
| `years_owned >= 7` | +10 | Assessor |
| `years_owned >= 15` | +5 (additive) | Assessor |
| `estimated_equity_pct >= 0.40` | +10 | Derived |
| `absentee_owner_flag == True` | +10 | Recorder / PropWire |
| `open_violation_flag == True` | +5 | Chicago Data Portal |
| `rate_reset_risk_flag == True` | +10 | PropStream (derived) |
| `recent_permit_flag == True` | +5 | Chicago Data Portal |
| `senior_flag == True` | +5 | Assessor |
| `portfolio_size > 3` | +5 | PropWire |

### 6.2 Likely to Buy (Move-Up)

| Signal | Points | Source |
|---|---|---|
| `tract_pct_35_to_54 high` | +15 | Census |
| `num_bedrooms <= 2` | +15 | Assessor |
| `tract_pct_households_with_children high` | +15 | Census |
| `tract_median_household_income high` | +10 | Census |
| `years_owned 3–7` | +10 | Assessor |
| `estimated_equity_pct >= 0.30` | +10 | Derived |
| `zip_yoy_price_change_pct > 0` | +10 | Zillow |
| `owner_occupied_flag == True` | +5 | Assessor |

### 6.3 Likely to Downsize

| Signal | Points | Source |
|---|---|---|
| `senior_flag == True` | +20 | Assessor |
| `death_in_household_flag == True` | +15 | PropStream |
| `tract_pct_65_plus high` | +10 | Census |
| `years_owned >= 15` | +10 | Assessor |
| `num_bedrooms >= 3` | +10 | Assessor |
| `building_sq_ft >= 1500` | +10 | Assessor |
| `estimated_equity_pct >= 0.60` | +10 | Derived |
| `tract_pct_households_with_children low` | +10 | Census |
| `owner_occupied_flag == True` | +5 | Assessor |
| `recent_permit_flag == True` | +5 | Chicago Data Portal |

### 6.4 Likely to Upsize

| Signal | Points | Source |
|---|---|---|
| `tract_pct_households_with_children high` | +20 | Census |
| `num_bedrooms <= 2` | +20 | Assessor |
| `tract_median_household_income high` | +15 | Census |
| `years_owned 2–5` | +15 | Assessor |
| `tract_pct_35_to_54 high` | +10 | Census |
| `building_sq_ft < 1000` | +10 | Assessor |
| `owner_occupied_flag == True` | +5 | Assessor |
| `estimated_equity_pct >= 0.20` | +5 | Derived |

### 6.5 Near Retirement / Life Transition

| Signal | Points | Source |
|---|---|---|
| `senior_flag == True` | +20 | Assessor |
| `life_event_flag == True` | +20 | PropStream (derived) |
| `death_in_household_flag == True` | +15 | PropStream |
| `tract_pct_65_plus high` | +10 | Census |
| `years_owned >= 10` | +10 | Assessor |
| `estimated_equity_pct >= 0.50` | +10 | Derived |
| `num_bedrooms >= 3` | +10 | Assessor |
| `tract_pct_households_with_children low` | +5 | Census |
| `absentee_owner_flag == True` | +5 | Recorder |
| `open_lien_count == 0` | +5 | PropWire |

### 6.6 Relocation Risk (Out-of-State / Absentee)

| Signal | Points | Source |
|---|---|---|
| `out_of_state_flag == True` | +25 | Recorder |
| `absentee_owner_flag == True` | +15 | Recorder / PropWire |
| `divorce_flag == True` | +15 | PropStream |
| `corporate_owner_flag == True` | +10 | PropWire |
| `tax_delinquency_flag == True` | +10 | Cook County |
| `nod_flag == True` | +10 | PropStream |
| `open_violation_flag == True` | +5 | Chicago Data Portal |
| `years_owned >= 7` | +10 | Assessor |

### 6.7 School District Movers

| Signal | Points | Source |
|---|---|---|
| `tract_pct_households_with_children high` | +30 | Census |
| `num_bedrooms <= 2` | +20 | Assessor |
| `years_owned 2–6` | +20 | Assessor |
| `tract_median_household_income high` | +15 | Census |
| `owner_occupied_flag == True` | +10 | Assessor |
| `zip_yoy_price_change_pct > 0` | +5 | Zillow |

### 6.8 Investor / Landlord

| Signal | Points | Source |
|---|---|---|
| `investor_flag == True` | +20 | PropWire |
| `absentee_owner_flag == True` | +15 | Recorder / PropWire |
| `portfolio_size > 1` | +15 | PropWire |
| `second_mortgage_flag == True` | +10 | PropStream |
| `price_to_rent_ratio <= 20` | +10 | Derived |
| `corporate_owner_flag == True` | +10 | PropWire |
| `refi_count >= 2` | +10 | PropStream |
| `zip_zori high` | +10 | Zillow |

### 6.9 Likely to Rent Out

| Signal | Points | Source |
|---|---|---|
| `investor_flag == True` | +20 | PropWire |
| `absentee_owner_flag == True` | +15 | Recorder |
| `price_to_rent_ratio <= 18` | +15 | Derived |
| `zip_zori high` | +15 | Zillow |
| `second_mortgage_flag == False` | +10 | PropStream |
| `open_lien_count == 0` | +10 | PropWire |
| `estimated_equity_pct >= 0.40` | +10 | Derived |
| `corporate_owner_flag == True` | +5 | PropWire |

### 6.10 Upgrade Renters (Renter → Buyer Conversion)

| Signal | Points | Source |
|---|---|---|
| `tract_pct_renter_occupied high` | +25 | Census |
| `tract_median_gross_rent high` | +20 | Census |
| `tract_median_household_income high` | +20 | Census |
| `zip_price_to_rent_ratio high` | +15 | Derived |
| `tract_pct_35_to_54 high` | +10 | Census |
| `zip_median_days_on_market low` | +10 | Zillow |

---

## 7. Outputs

### 7.1 Scored Property Export (CSV / Excel)
- One row per property
- All source fields + derived fields + 10 propensity scores
- Sortable by any score for agent use
- Refreshed monthly

### 7.2 Dashboard (Streamlit)
- Filter by use case score threshold
- Map view of properties (color-coded by score)
- Property detail panel (all fields including PropStream data)
- Life event & distress alert badges on flagged properties
- Export filtered results to CSV
- Deployed on Streamlit Cloud for remote access (iPad demo-ready)

---

## 8. Tech Stack (Proposed)

| Layer | Tool |
|---|---|
| Language | Python 3.11+ |
| Data ingestion | `requests`, `sodapy` (Socrata), `census`, PropStream API/export |
| Data processing | `pandas`, `geopandas` |
| Storage | Parquet files (local, v1) → PostgreSQL (v2) |
| Scoring | Custom Python scoring engine |
| Dashboard | Streamlit (v1) |
| Orchestration | Manual / cron (v1) → Airflow (v2) |
| Version control | GitHub (this repo) |

---

## 9. Constraints & Assumptions

- **ZIP 60610 only** for v1 POC
- **No PII storage** beyond what is in the public record and PropStream data
- **No automated outreach** — agent manually uses the export
- Monthly data refresh is acceptable; real-time is not required
- Free data sources may have rate limits; ingestion scripts must handle throttling
- PropStream subscription ($99/mo) required for pre-foreclosure, life event, mortgage, and listing history data
- Address matching across sources will require fuzzy matching (PIN is not always available)

---

## 10. Open Questions

| # | Question | Owner | Status |
|---|---|---|---|
| 1 | Which dashboard tool? | User | **Resolved** — Streamlit, deployed on Streamlit Cloud |
| 2 | Should skip-trace phone/email be included in v1 or only v2? | User | Open |
| 3 | What is the refresh cadence for agent use? (weekly vs. monthly) | User | Open |
| 4 | Will PropStream ($99/mo) be added? | User | **Resolved** — Yes, adding PropStream for pre-foreclosure, life events, mortgage, and listing history |
| 5 | PropStream ingestion method: API vs. bulk CSV export? | Dev | Open |
| 6 | How to handle PropStream data for properties with no match (coverage gaps)? | Dev | Open |

---

*Next: [Architecture Document](ARCHITECTURE.md)*
