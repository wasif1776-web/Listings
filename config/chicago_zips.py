"""Chicago ZIP codes with neighborhood labels for the dashboard selector."""
from __future__ import annotations

CHICAGO_ZIPS: dict[str, str] = {
    "60601": "Loop / New Eastside",
    "60602": "Loop",
    "60603": "Loop",
    "60604": "Loop / Printer's Row",
    "60605": "South Loop / Museum Campus",
    "60606": "Loop / West Loop Gate",
    "60607": "West Loop / Greektown",
    "60608": "Pilsen / Bridgeport / Chinatown",
    "60609": "Back of the Yards / Bridgeport",
    "60610": "Gold Coast / Old Town / Near North",
    "60611": "Streeterville / Magnificent Mile",
    "60612": "Near West Side / Medical District",
    "60613": "Lakeview / Wrigleyville",
    "60614": "Lincoln Park / DePaul",
    "60615": "Hyde Park / Kenwood",
    "60616": "South Loop / Chinatown / Bronzeville",
    "60617": "South Chicago / Calumet Heights",
    "60618": "North Center / Avondale / Irving Park",
    "60619": "Chatham / Avalon Park",
    "60620": "Auburn Gresham / Washington Heights",
    "60621": "Englewood",
    "60622": "Wicker Park / Ukrainian Village / Bucktown",
    "60623": "Lawndale / Little Village",
    "60624": "West Garfield Park / East Garfield Park",
    "60625": "Lincoln Square / Ravenswood / Bowmanville",
    "60626": "Rogers Park / West Ridge",
    "60628": "Roseland / Pullman / West Pullman",
    "60629": "Chicago Lawn / Marquette Park",
    "60630": "Jefferson Park / Forest Glen",
    "60631": "Edison Park / Norwood Park",
    "60632": "Archer Heights / Brighton Park",
    "60633": "Hegewisch",
    "60634": "Dunning / Portage Park / Belmont Cragin",
    "60636": "West Englewood / Chicago Lawn",
    "60637": "Woodlawn / South Shore / Hyde Park",
    "60638": "Garfield Ridge / Clearing",
    "60639": "Hermosa / Belmont Cragin",
    "60640": "Uptown / Andersonville",
    "60641": "Old Irving Park / Portage Park",
    "60642": "Noble Square / Goose Island",
    "60643": "Beverly / Morgan Park / Mount Greenwood",
    "60644": "Austin",
    "60645": "West Ridge / Peterson Park",
    "60646": "Sauganash / Edgebrook",
    "60647": "Logan Square / Bucktown",
    "60649": "South Shore / Jackson Park Highlands",
    "60651": "Humboldt Park / Austin",
    "60652": "Ashburn / Scottsdale",
    "60653": "Bronzeville / Douglas",
    "60654": "River North",
    "60655": "Mount Greenwood / Beverly",
    "60656": "Norwood Park / O'Hare",
    "60657": "Lakeview / Boystown",
    "60659": "West Ridge / Arcadia Terrace",
    "60660": "Edgewater / Andersonville",
    "60661": "West Loop / Fulton Market",
    "60706": "Harwood Heights / Norridge (partial)",
    "60707": "Elmwood Park / Galewood (partial)",
    "60827": "Riverdale / Altgeld Gardens",
}


def zip_label(zip_code: str) -> str:
    """Return a display label like '60610 - Gold Coast / Old Town / Near North'."""
    desc = CHICAGO_ZIPS.get(zip_code, "")
    if desc:
        return f"{zip_code} - {desc}"
    return zip_code


def all_zip_labels() -> list[tuple[str, str]]:
    """Return sorted list of (zip_code, label) tuples."""
    return [(z, zip_label(z)) for z in sorted(CHICAGO_ZIPS)]
