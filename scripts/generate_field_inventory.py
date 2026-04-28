"""Generate field inventory spreadsheet for data gap analysis."""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Field Inventory"

# Styles
header_font = Font(bold=True, color="FFFFFF", size=11)
header_fill = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
yes_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
no_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
section_fill = PatternFill(start_color="D6E4F0", end_color="D6E4F0", fill_type="solid")
section_font = Font(bold=True, size=11)
thin_border = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)

headers = ["Field", "Have", "Source", "Source Type", "Use Case"]
col_widths = [35, 8, 45, 12, 65]

for col_idx, (header, width) in enumerate(zip(headers, col_widths), 1):
    cell = ws.cell(row=1, column=col_idx, value=header)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center")
    cell.border = thin_border
    ws.column_dimensions[get_column_letter(col_idx)].width = width

ws.auto_filter.ref = "A1:E1"
ws.freeze_panes = "A2"

rows = [
    # --- PROPERTY CHARACTERISTICS ---
    ("PROPERTY CHARACTERISTICS", "", "", "", ""),
    ("pin", "Yes", "Cook County Assessor (Free API)", "Free", "Join key across all sources"),
    ("address", "Yes", "Cook County Assessor (Free API)", "Free", "Join key, display"),
    ("city", "Yes", "Cook County Assessor (Free API)", "Free", "Filter"),
    ("zip_code", "Yes", "Cook County Assessor (Free API)", "Free", "Filter (60610)"),
    ("property_class", "Yes", "Cook County Assessor (Free API)", "Free", "Property type classification"),
    ("township_code", "Yes", "Cook County Assessor (Free API)", "Free", "Geo context"),
    ("year_built", "Yes", "Cook County Assessor (Free API)", "Free", "Property age, renovation likelihood"),
    ("building_sq_ft", "Yes", "Cook County Assessor (Free API)", "Free", "Upsize/Downsize scoring"),
    ("land_sq_ft", "Yes", "Cook County Assessor (Free API)", "Free", "Lot size, development potential"),
    ("num_bedrooms", "Yes", "Cook County Assessor (Free API)", "Free", "Upsize/Downsize/School District scoring"),
    ("num_bathrooms", "Yes", "Cook County Assessor (Free API)", "Free", "Property size context"),
    ("num_rooms", "Yes", "Cook County Assessor (Free API)", "Free", "Property size context"),
    ("garage_indicator", "Yes", "Cook County Assessor (Free API)", "Free", "Amenity / property quality"),
    ("latitude", "Yes", "Cook County Assessor (Free API)", "Free", "Map display, geo matching"),
    ("longitude", "Yes", "Cook County Assessor (Free API)", "Free", "Map display, geo matching"),

    # --- VALUATION & TAX ---
    ("VALUATION & TAX", "", "", "", ""),
    ("estimated_market_value", "Yes", "Cook County Assessor (Free API)", "Free", "Equity calculation, AVM baseline"),
    ("assessed_value_building", "Yes", "Cook County Assessor (Free API)", "Free", "Tax base, value context"),
    ("assessed_value_land", "Yes", "Cook County Assessor (Free API)", "Free", "Tax base, land value"),
    ("tax_year", "Yes", "Cook County Assessor (Free API)", "Free", "Assessment recency"),
    ("tax_annual_amount", "Yes", "Cook County Recorder (Free API)", "Free", "Carrying cost burden"),
    ("homeowner_exemption", "Yes", "Cook County Assessor (Free API)", "Free", "Owner-occupied proxy"),
    ("senior_exemption", "Yes", "Cook County Assessor (Free API)", "Free", "Age proxy (65+)"),
    ("senior_freeze_exemption", "Yes", "Cook County Assessor (Free API)", "Free", "Fixed-income senior signal"),
    ("propstream_avm", "No", "BatchData API", "Paid", "Real-time property valuation, more accurate equity calc"),
    ("avm_confidence_score", "No", "BatchData API", "Paid", "Data quality — weight AVM-based signals by confidence"),
    ("avm_vs_assessed_pct", "No", "Derived (BatchData AVM vs Assessor)", "Paid", "Identifies undervalued properties, investor opportunity"),

    # --- SALE HISTORY ---
    ("SALE HISTORY", "", "", "", ""),
    ("sale_date_1", "Yes", "Cook County Assessor (Free API)", "Free", "Years owned calc, tenure signal"),
    ("sale_price_1", "Yes", "Cook County Assessor (Free API)", "Free", "Equity calc, appreciation"),
    ("sale_date_2", "Yes", "Cook County Assessor (Free API)", "Free", "Sale frequency, flip detection"),
    ("sale_price_2", "Yes", "Cook County Assessor (Free API)", "Free", "Price trajectory"),
    ("sale_date_3", "Yes", "Cook County Assessor (Free API)", "Free", "Sale frequency"),
    ("sale_price_3", "Yes", "Cook County Assessor (Free API)", "Free", "Price trajectory"),
    ("deed_type", "Yes", "Cook County Assessor (Free API)", "Free", "Transaction type (warranty, quitclaim, etc.)"),

    # --- OWNERSHIP & IDENTITY ---
    ("OWNERSHIP & IDENTITY", "", "", "", ""),
    ("grantor", "Yes", "Cook County Recorder (Free API)", "Free", "Previous owner name"),
    ("grantee", "Yes", "Cook County Recorder (Free API)", "Free", "Current owner name"),
    ("deed_date", "Yes", "Cook County Recorder (Free API)", "Free", "Transfer recency"),
    ("instrument_type", "Yes", "Cook County Recorder (Free API)", "Free", "Trust/LLC detection"),
    ("grantee_mailing_address", "Yes", "Cook County Recorder (Free API)", "Free", "Absentee owner detection"),
    ("grantee_mailing_city", "Yes", "Cook County Recorder (Free API)", "Free", "Out-of-state detection"),
    ("grantee_mailing_state", "Yes", "Cook County Recorder (Free API)", "Free", "Out-of-state detection"),
    ("owner_name", "Yes", "PropWire (Free Tier)", "Free", "Owner identity, entity resolution"),
    ("owner_mailing_address", "Yes", "PropWire (Free Tier)", "Free", "Absentee flag confirmation"),
    ("owner_mailing_city", "Yes", "PropWire (Free Tier)", "Free", "Out-of-state confirmation"),
    ("owner_mailing_state", "Yes", "PropWire (Free Tier)", "Free", "Out-of-state confirmation"),
    ("absentee_owner_flag", "Yes", "PropWire (Free Tier)", "Free", "Absentee signal — Sell, Relocation, Investor"),
    ("corporate_owner_flag", "Yes", "PropWire (Free Tier)", "Free", "Investor/LLC detection"),
    ("portfolio_size", "Yes", "PropWire (Free Tier)", "Free", "Investor scale — Investor, Sell scoring"),
    ("owner_age_range", "No", "BatchData API", "Paid", "Precise age — Downsize, Retirement, Life Transition"),
    ("owner_length_of_residence", "No", "BatchData API", "Paid", "Actual vs deed-based tenure — more accurate years_owned"),
    ("owner_is_trust", "No", "BatchData API", "Paid", "Trust-owned properties — estate planning, succession signal"),

    # --- TAX DELINQUENCY & DISTRESS ---
    ("TAX DELINQUENCY & DISTRESS", "", "", "", ""),
    ("tax_delinquency_flag", "Yes", "Cook County Treasurer (Free API)", "Free", "Distress signal — Sell, Relocation"),
    ("delinquent_tax_amount", "Yes", "Cook County Treasurer (Free API)", "Free", "Distress severity"),
    ("delinquent_tax_years", "Yes", "Cook County Treasurer (Free API)", "Free", "Distress duration"),

    # --- PRE-FORECLOSURE ---
    ("PRE-FORECLOSURE", "", "", "", ""),
    ("nod_flag", "No", "BatchData API", "Paid", "Notice of Default — strongest sell signal"),
    ("lis_pendens_flag", "No", "BatchData API", "Paid", "Lawsuit pending — legal distress, forced sale"),
    ("foreclosure_status", "No", "BatchData API", "Paid", "Stage: pre-foreclosure, auction, REO — Sell, Relocation"),
    ("auction_date", "No", "BatchData API", "Paid", "Foreclosure timeline — urgency signal"),
    ("default_amount", "No", "BatchData API", "Paid", "Default severity — distress magnitude"),

    # --- LIFE EVENT TRIGGERS ---
    ("LIFE EVENT TRIGGERS", "", "", "", ""),
    ("probate_flag", "No", "PropertyRadar API", "Paid", "Inherited property — Sell, Life Transition"),
    ("divorce_flag", "No", "PropertyRadar API", "Paid", "Forced sale — Sell, Relocation Risk"),
    ("inherited_flag", "No", "PropertyRadar API", "Paid", "New owner likely to sell — Sell scoring"),
    ("death_in_household_flag", "No", "PropertyRadar API", "Paid", "Life transition — Downsize, Sell, Retirement"),
    ("bankruptcy_flag", "No", "BatchData API", "Paid", "Financial distress — Sell, Relocation"),
    ("judgment_lien_flag", "No", "BatchData API", "Paid", "Legal/financial distress — forced sale signal"),

    # --- MORTGAGE DATA ---
    ("MORTGAGE DATA", "", "", "", ""),
    ("mortgage_origination_date", "Yes", "PropWire (Free Tier)", "Free", "Loan age"),
    ("mortgage_amount", "Yes", "PropWire (Free Tier)", "Free", "Original loan amount, LTV baseline"),
    ("mortgage_type", "Yes", "PropWire (Free Tier)", "Free", "ARM vs Fixed — rate reset risk"),
    ("lender_name", "Yes", "PropWire (Free Tier)", "Free", "Lender context"),
    ("estimated_loan_balance", "No", "BatchData API", "Paid", "Current balance — accurate equity/LTV calc"),
    ("ltv_ratio", "No", "BatchData API", "Paid", "Current loan-to-value — equity position"),
    ("interest_rate", "No", "BatchData API", "Paid", "Rate sensitivity — refi/sell motivation"),
    ("rate_type", "No", "BatchData API", "Paid", "Fixed vs ARM with reset date — rate reset risk"),
    ("refi_count", "No", "BatchData API", "Paid", "Refinance history — financial activity signal"),
    ("second_mortgage_flag", "No", "BatchData API", "Paid", "HELOC/2nd mortgage — leverage, Investor scoring"),
    ("second_mortgage_amount", "No", "BatchData API", "Paid", "Total debt calc — true LTV"),

    # --- LISTING HISTORY ---
    ("LISTING HISTORY (MLS-DERIVED)", "", "", "", ""),
    ("prev_listed_flag", "No", "BatchData API", "Paid", "Previously listed — re-list signal, Sell scoring"),
    ("expired_listing_flag", "No", "BatchData API", "Paid", "Failed sale — strong re-list signal"),
    ("last_list_date", "No", "BatchData API", "Paid", "Listing recency — intent timing"),
    ("last_list_price", "No", "BatchData API", "Paid", "Pricing context — over/underpriced detection"),
    ("days_since_delisted", "No", "BatchData API", "Paid", "Re-list timing window"),
    ("listing_count", "No", "BatchData API", "Paid", "How many times listed — sale difficulty"),
    ("on_market_flag", "No", "BatchData API", "Paid", "Currently listed — exclude from prospecting or flag"),

    # --- PERMITS & VIOLATIONS ---
    ("PERMITS & VIOLATIONS", "", "", "", ""),
    ("permit_number", "Yes", "Chicago Data Portal (Free API)", "Free", "Permit deduplication"),
    ("permit_type", "Yes", "Chicago Data Portal (Free API)", "Free", "Renovation type — prep-to-sell signal"),
    ("issue_date", "Yes", "Chicago Data Portal (Free API)", "Free", "Permit recency"),
    ("total_fee", "Yes", "Chicago Data Portal (Free API)", "Free", "Renovation scale/investment proxy"),
    ("work_description", "Yes", "Chicago Data Portal (Free API)", "Free", "Renovation type detail"),
    ("latest_permit_date", "Yes", "Chicago Data Portal (Free API)", "Free", "Most recent activity — prep-to-sell"),
    ("permit_count_5yr", "Yes", "Chicago Data Portal (Free API)", "Free", "Renovation activity level"),
    ("violation_date", "Yes", "Chicago Data Portal (Free API)", "Free", "Distress recency"),
    ("violation_code", "Yes", "Chicago Data Portal (Free API)", "Free", "Distress type"),
    ("violation_status", "Yes", "Chicago Data Portal (Free API)", "Free", "Active vs resolved distress"),
    ("violation_count_open", "Yes", "Chicago Data Portal (Free API)", "Free", "Distress severity — Sell, Relocation"),

    # --- CENSUS / DEMOGRAPHICS ---
    ("CENSUS / DEMOGRAPHICS (TRACT-LEVEL)", "", "", "", ""),
    ("block_group_geoid", "Yes", "US Census ACS (Free API)", "Free", "Geographic join key"),
    ("tract_median_age", "Yes", "US Census ACS (Free API)", "Free", "Neighborhood age profile"),
    ("tract_median_household_income", "Yes", "US Census ACS (Free API)", "Free", "Income proxy — Buy, Upsize, Upgrade Renters"),
    ("tract_owner_occupied_units", "Yes", "US Census ACS (Free API)", "Free", "Neighborhood ownership rate"),
    ("tract_renter_occupied_units", "Yes", "US Census ACS (Free API)", "Free", "Renter density — Upgrade Renters, Investor"),
    ("tract_total_occupied_units", "Yes", "US Census ACS (Free API)", "Free", "Occupancy baseline"),
    ("tract_median_year_moved_in", "Yes", "US Census ACS (Free API)", "Free", "Neighborhood tenure signal"),
    ("tract_households_with_children", "Yes", "US Census ACS (Free API)", "Free", "Family presence — School District, Upsize"),
    ("tract_total_households", "Yes", "US Census ACS (Free API)", "Free", "Household baseline"),
    ("tract_total_population", "Yes", "US Census ACS (Free API)", "Free", "Population density"),
    ("tract_median_home_value", "Yes", "US Census ACS (Free API)", "Free", "Neighborhood price context"),
    ("tract_median_gross_rent", "Yes", "US Census ACS (Free API)", "Free", "Rent context — Upgrade Renters, Investor"),
    ("tract_vacant_units", "Yes", "US Census ACS (Free API)", "Free", "Vacancy rate — market health"),
    ("tract_total_housing_units", "Yes", "US Census ACS (Free API)", "Free", "Housing stock baseline"),
    ("tract_pct_65_plus", "Yes", "US Census ACS (Free API)", "Free", "Senior density — Downsize, Retirement"),
    ("tract_pct_35_to_54", "Yes", "US Census ACS (Free API)", "Free", "Move-up buyer density — Buy, Upsize"),
    ("tract_pct_households_with_children", "Yes", "US Census ACS (Free API)", "Free", "Family density — School District, Upsize"),
    ("tract_pct_owner_occupied", "Yes", "US Census ACS (Free API)", "Free", "Ownership rate — neighborhood stability"),
    ("tract_pct_renter_occupied", "Yes", "US Census ACS (Free API)", "Free", "Renter rate — Upgrade Renters scoring"),

    # --- MARKET DATA ---
    ("MARKET DATA (ZIP-LEVEL)", "", "", "", ""),
    ("zip_zhvi", "Yes", "Zillow Research (Free CSV)", "Free", "Home value index — AVM benchmark"),
    ("zip_zori", "Yes", "Zillow Research (Free CSV)", "Free", "Rent index — Investor, Rent Out scoring"),
    ("zip_median_sale_price", "Yes", "Zillow Research (Free CSV)", "Free", "Market pricing context"),
    ("zip_median_days_on_market", "Yes", "Zillow Research (Free CSV)", "Free", "Market heat — Upgrade Renters"),
    ("zip_yoy_price_change_pct", "Yes", "Zillow Research (Free CSV)", "Free", "Appreciation — Buy, School District"),
    ("zip_pct_listings_price_cut", "Yes", "Zillow Research (Free CSV)", "Free", "Market softness signal"),
    ("zip_inventory", "Yes", "Zillow Research (Free CSV)", "Free", "Supply level"),
    ("zip_median_list_price", "Yes", "Zillow Research (Free CSV)", "Free", "Listing price context"),
    ("zip_price_to_rent_ratio", "Yes", "Zillow Research (Free CSV)", "Free", "Investor signal — Investor, Rent Out"),

    # --- HUD RENTS ---
    ("HUD FAIR MARKET RENTS", "", "", "", ""),
    ("fmr_studio", "Yes", "HUD (Free CSV)", "Free", "Rent AVM by bedroom count"),
    ("fmr_1br", "Yes", "HUD (Free CSV)", "Free", "Rent AVM by bedroom count"),
    ("fmr_2br", "Yes", "HUD (Free CSV)", "Free", "Rent AVM by bedroom count"),
    ("fmr_3br", "Yes", "HUD (Free CSV)", "Free", "Rent AVM by bedroom count"),
    ("fmr_4br", "Yes", "HUD (Free CSV)", "Free", "Rent AVM by bedroom count"),

    # --- CONTACT / SKIP TRACE ---
    ("CONTACT / SKIP TRACE", "", "", "", ""),
    ("skip_trace_phone", "No", "PropWire ($0.10/record) or BatchData API", "Paid", "Owner phone — outreach"),
    ("skip_trace_email", "No", "PropWire ($0.10/record) or BatchData API", "Paid", "Owner email — outreach"),

    # --- DERIVED FIELDS ---
    ("DERIVED / ENGINEERED FIELDS", "", "", "", ""),
    ("years_owned", "Yes", "Derived (sale_date_1)", "Free", "Long tenure — Sell, Downsize, Retirement"),
    ("estimated_equity_pct", "Yes", "Derived (market value - mortgage)", "Free", "Equity position — all equity-based models"),
    ("estimated_equity_dollar", "Yes", "Derived (market value - mortgage)", "Free", "Equity dollar amount"),
    ("out_of_state_flag", "Yes", "Derived (mailing state != IL)", "Free", "Absentee severity — Relocation Risk"),
    ("owner_occupied_flag", "Yes", "Derived (homeowner exemption)", "Free", "Occupancy — Buy, Upsize, School District"),
    ("investor_flag", "Yes", "Derived (corporate OR portfolio > 1)", "Free", "Investor detection — Investor, Rent Out"),
    ("senior_flag", "Yes", "Derived (senior exemptions)", "Free", "Age proxy — Downsize, Retirement"),
    ("recent_permit_flag", "Yes", "Derived (permit date < 2yr)", "Free", "Prep-to-sell — Sell, Downsize"),
    ("open_violation_flag", "Yes", "Derived (open violations > 0)", "Free", "Distress — Sell, Relocation"),
    ("price_to_rent_ratio", "Yes", "Derived (value / rent x 12)", "Free", "Investor calc — Investor, Rent Out"),
    ("appreciation_vs_zip", "Yes", "Derived (property vs ZIP appreciation)", "Free", "Relative gain — sell motivation"),
    ("sale_count", "Yes", "Derived (count of sale dates)", "Free", "Transaction frequency"),
    ("life_event_flag", "No", "Derived (probate OR divorce OR inherited OR death)", "Paid", "Any life event — Sell, Retirement"),
    ("distress_flag", "No", "Derived (NOD OR lis pendens OR foreclosure)", "Paid", "Any pre-foreclosure — Sell, Relocation"),
    ("total_debt", "No", "Derived (loan balance + 2nd mortgage)", "Paid", "True leverage position"),
    ("true_ltv", "No", "Derived (total debt / real-time AVM)", "Paid", "Accurate equity — all equity models"),
    ("negative_equity_flag", "No", "Derived (true LTV > 1.0)", "Paid", "Underwater — distress signal"),
    ("rate_reset_risk_flag", "No", "Derived (ARM + origination < 5yr)", "Paid", "ARM reset window — Sell scoring"),
    ("failed_listing_flag", "No", "Derived (expired + delisted < 1yr)", "Paid", "Recent failed sale — strong Sell signal"),
]

section_rows = set()
row_num = 2
for row_data in rows:
    field, have, source, source_type, use_case = row_data

    # Section header
    if have == "" and source == "":
        for col_idx in range(1, 6):
            cell = ws.cell(row=row_num, column=col_idx)
            cell.fill = section_fill
            cell.font = section_font
            cell.border = thin_border
        ws.cell(row=row_num, column=1, value=field)
        ws.merge_cells(start_row=row_num, start_column=1, end_row=row_num, end_column=5)
        section_rows.add(row_num)
    else:
        ws.cell(row=row_num, column=1, value=field).border = thin_border
        have_cell = ws.cell(row=row_num, column=2, value=have)
        have_cell.alignment = Alignment(horizontal="center")
        have_cell.border = thin_border
        if have == "Yes":
            have_cell.fill = yes_fill
        else:
            have_cell.fill = no_fill
        ws.cell(row=row_num, column=3, value=source).border = thin_border
        type_cell = ws.cell(row=row_num, column=4, value=source_type)
        type_cell.alignment = Alignment(horizontal="center")
        type_cell.border = thin_border
        ws.cell(row=row_num, column=5, value=use_case).border = thin_border

    row_num += 1

# Summary counts at the bottom
row_num += 1
ws.cell(row=row_num, column=1, value="SUMMARY").font = Font(bold=True, size=12)
row_num += 1

yes_count = sum(1 for r in rows if r[1] == "Yes")
no_count = sum(1 for r in rows if r[1] == "No")
free_count = sum(1 for r in rows if r[3] == "Free")
paid_count = sum(1 for r in rows if r[3] == "Paid")

for label, value in [
    ("Total Fields", yes_count + no_count),
    ("Fields We Have (Yes)", yes_count),
    ("Fields Missing (No)", no_count),
    ("Free Fields", free_count),
    ("Paid Fields", paid_count),
]:
    ws.cell(row=row_num, column=1, value=label).font = Font(bold=True)
    ws.cell(row=row_num, column=2, value=value).alignment = Alignment(horizontal="center")
    row_num += 1

output_path = "docs/field_inventory.xlsx"
wb.save(output_path)
print(f"Saved to {output_path}")
print(f"Total fields: {yes_count + no_count} | Have: {yes_count} | Missing: {no_count} | Free: {free_count} | Paid: {paid_count}")
