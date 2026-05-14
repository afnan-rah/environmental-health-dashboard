"""Project root and standard data paths."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_GEO = PROJECT_ROOT / "data" / "geo"

ARSENIC_RAW_XLSX = DATA_RAW / "ALL_ArsenicTests_Mapping_071524.xlsx"
MOSQUITO_RAW_XLSX = DATA_RAW / "mosquitoSurveillanceData_2021_Kent (Final).xlsx"

ARSENIC_CLEAN_CSV = DATA_PROCESSED / "arsenic_cleaned.csv"
MOSQUITO_CLEAN_CSV = DATA_PROCESSED / "mosquito_cleaned.csv"

# Fallback county outlines (Plotly-derived MI subset) if TIGER extract not built yet.
MI_COUNTIES_GEOJSON_FALLBACK = DATA_GEO / "mi_counties.geojson"
# Official TIGER/Line extracts (built locally via scripts/extract_mi_counties_tiger.py).
MI_COUNTIES_TIGER_2025_GEOJSON = DATA_GEO / "mi_counties_tiger2025.geojson"
MI_COUNTIES_TIGER_2024_GEOJSON = DATA_GEO / "mi_counties_tiger2024.geojson"
# Raw national county layers (large; keep out of git — see .gitignore).
TIGER_US_COUNTY_2025_SHP = DATA_RAW / "tl_2025_us_county" / "tl_2025_us_county.shp"
TIGER_US_COUNTY_2024_SHP = DATA_RAW / "tl_2024_us_county" / "tl_2024_us_county.shp"

ZIP_REFERENCE_CSV = DATA_PROCESSED / "mi_zip_reference.csv"
KENT_CITY_CENTROIDS_CSV = DATA_PROCESSED / "kent_area_city_centroids.csv"


def resolve_mi_counties_geojson() -> Path:
    """Prefer Census TIGER-derived MI counties (newer year first), else Plotly fallback."""
    for candidate in (
        MI_COUNTIES_TIGER_2025_GEOJSON,
        MI_COUNTIES_TIGER_2024_GEOJSON,
        MI_COUNTIES_GEOJSON_FALLBACK,
    ):
        if candidate.exists():
            return candidate
    return MI_COUNTIES_GEOJSON_FALLBACK
