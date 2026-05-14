"""
Reusable pandas pipeline for mosquito surveillance trap rows (Kent County template).
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from src.utils.paths import MOSQUITO_CLEAN_CSV, MOSQUITO_RAW_XLSX

logger = logging.getLogger(__name__)

COLUMN_RENAME = {
    "Collection Method/Trap Type": "collection_method",
    "Attractant Used": "attractant_used",
    "Collection Location ID": "collection_location_id",
    "UID if submitting for arbovirus testing": "uid_arbovirus_submission",
    "Nearest Street Address": "nearest_street_address",
    "City": "city",
    "State": "state",
    "County": "county",
    "Type of Collection Site": "collection_site_type",
    "Trap Set Date": "trap_set_date",
    "Trap Set Time of Day": "trap_set_time_of_day",
    "Trap Pickup Date": "trap_pickup_date",
    "Trap Pickup Time of Day": "trap_pickup_time_of_day",
    "Genus": "genus",
    "Species": "species",
    "# Females Collected": "females_collected",
    "# Males Collected": "males_collected",
    "# Adults of Unknown Sex Collected": "adults_unknown_sex_collected",
    "Staff Person": "staff_person",
    "Notes": "notes",
    "Detected": "detected_raw",
}


def _month_to_season(month: int | None) -> str | None:
    if month is None or pd.isna(month):
        return None
    m = int(month)
    if m in (12, 1, 2):
        return "winter"
    if m in (3, 4, 5):
        return "spring"
    if m in (6, 7, 8):
        return "summer"
    if m in (9, 10, 11):
        return "fall"
    return None


def _clean_text(val: object) -> str | None:
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return None
    s = str(val).strip()
    return s if s and s.lower() != "nan" else None


def _species_binomial(genus: object, species: object) -> str | None:
    g = _clean_text(genus)
    sp = _clean_text(species)
    if not g and not sp:
        return None
    if g and not sp:
        return f"{g} sp."
    if g and sp:
        if sp.lower() in ("sp.", "sp"):
            return f"{g} sp."
        return f"{g} {sp}"
    return sp


def _normalize_detected(val: object) -> str | None:
    s = _clean_text(val)
    if s is None:
        return None
    up = s.upper()
    if up in ("ND", "N/D", "NOT DETECTED"):
        return "not_detected"
    if up in ("POSITIVE", "POS"):
        return "positive"
    return s.lower()


def clean_mosquito_dataframe(raw: pd.DataFrame) -> pd.DataFrame:
    missing = set(COLUMN_RENAME) - set(raw.columns)
    if missing:
        raise ValueError(f"Mosquito sheet missing columns: {sorted(missing)}")

    out = raw.rename(columns=COLUMN_RENAME).copy()
    n_start = len(out)

    out["trap_set_date"] = pd.to_datetime(out["trap_set_date"], errors="coerce")
    out["trap_pickup_date"] = pd.to_datetime(out["trap_pickup_date"], errors="coerce")

    out["attractant_used"] = out["attractant_used"].map(_clean_text)

    out["trap_set_year"] = out["trap_set_date"].dt.year
    out["trap_set_month"] = out["trap_set_date"].dt.month
    out["season"] = out["trap_set_month"].map(_month_to_season)

    for col in ("city", "county", "collection_site_type"):
        out[col] = out[col].map(lambda x: _clean_text(x).title() if _clean_text(x) else None)

    out["collection_method"] = out["collection_method"].map(_clean_text)

    out["nearest_street_address"] = out["nearest_street_address"].map(_clean_text)

    out["state"] = out["state"].map(lambda x: _clean_text(x).upper() if _clean_text(x) else None)

    out["genus"] = out["genus"].map(_clean_text)
    out["species"] = out["species"].map(_clean_text)
    out["species_binomial"] = [_species_binomial(g, s) for g, s in zip(out["genus"], out["species"])]

    for col in ("females_collected", "males_collected", "adults_unknown_sex_collected"):
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0).astype(int)

    out["total_adults_collected"] = (
        out["females_collected"] + out["males_collected"] + out["adults_unknown_sex_collected"]
    )

    out["detected_normalized"] = out["detected_raw"].map(_normalize_detected)
    out["missing_taxon"] = out["genus"].isna() & out["species"].isna()

    dup_count = int(out.duplicated().sum())
    out = out.drop_duplicates()
    n_after = len(out)

    logger.info(
        "Mosquito rows: start=%s after_dedupe=%s duplicate_rows_removed=%s",
        n_start,
        n_after,
        dup_count,
    )
    logger.info("Missing taxon rows: %s", int(out["missing_taxon"].sum()))
    logger.info("Detected distribution:\n%s", out["detected_normalized"].value_counts(dropna=False))

    cols = [
        "collection_method",
        "attractant_used",
        "collection_location_id",
        "uid_arbovirus_submission",
        "nearest_street_address",
        "city",
        "state",
        "county",
        "collection_site_type",
        "trap_set_date",
        "trap_set_time_of_day",
        "trap_pickup_date",
        "trap_pickup_time_of_day",
        "trap_set_year",
        "trap_set_month",
        "season",
        "genus",
        "species",
        "species_binomial",
        "females_collected",
        "males_collected",
        "adults_unknown_sex_collected",
        "total_adults_collected",
        "detected_raw",
        "detected_normalized",
        "missing_taxon",
        "staff_person",
        "notes",
    ]
    return out[cols].sort_values(["trap_set_date", "collection_location_id"]).reset_index(drop=True)


def load_raw_mosquito(path: str | Path | None = None) -> pd.DataFrame:
    p = Path(path) if path is not None else MOSQUITO_RAW_XLSX
    return pd.read_excel(p, sheet_name="mosquitoSurveillanceData")


def run_clean_mosquito(
    raw_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> pd.DataFrame:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raw = load_raw_mosquito(raw_path)
    cleaned = clean_mosquito_dataframe(raw)
    out = Path(output_path) if output_path is not None else MOSQUITO_CLEAN_CSV
    out.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(out, index=False)
    logger.info("Wrote %s rows to %s", len(cleaned), out)
    return cleaned


if __name__ == "__main__":
    run_clean_mosquito()
