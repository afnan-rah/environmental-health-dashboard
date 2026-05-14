"""Project root and standard data paths."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

ARSENIC_RAW_XLSX = DATA_RAW / "ALL_ArsenicTests_Mapping_071524.xlsx"
MOSQUITO_RAW_XLSX = DATA_RAW / "mosquitoSurveillanceData_2021_Kent (Final).xlsx"

ARSENIC_CLEAN_CSV = DATA_PROCESSED / "arsenic_cleaned.csv"
MOSQUITO_CLEAN_CSV = DATA_PROCESSED / "mosquito_cleaned.csv"
