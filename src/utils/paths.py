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

MI_COUNTIES_GEOJSON = DATA_GEO / "mi_counties.geojson"
ZIP_REFERENCE_CSV = DATA_PROCESSED / "mi_zip_reference.csv"
KENT_CITY_CENTROIDS_CSV = DATA_PROCESSED / "kent_area_city_centroids.csv"
