"""
Reusable pandas pipeline for arsenic well-test records.

Result values behave like total arsenic in mg/L. ``Result_Cat`` is numeric in the
raw sheet; thresholds inferred from labeled rows must be confirmed with the
data owner before any regulatory interpretation.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd

from src.utils.paths import ARSENIC_CLEAN_CSV, ARSENIC_RAW_XLSX

logger = logging.getLogger(__name__)

# Inferred from non-null (Result, Result_Cat) pairs in the current export.
# Confirm with subject-matter expert (see notebook).
RESULT_CAT_RULES_DOC = (
    "Inferred mapping: 0 = non-detect (0 mg/L); 1 = (0, 0.005); "
    "2 = [0.005, 0.01); 3 = >= 0.01 mg/L (EPA drinking-water MCL reference is 0.01 mg/L)."
)


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename = {
        "Year": "test_date",
        "Street": "street",
        "City": "city",
        "State": "state",
        "Zip": "zip_raw",
        "Test": "test_name",
        "Result": "result_mgl",
        "Result_Cat": "result_category_code_raw",
        "Full_Add": "full_address",
        "Prop_Add": "property_address",
    }
    missing = set(rename) - set(df.columns)
    if missing:
        raise ValueError(f"Unexpected arsenic columns; missing: {sorted(missing)}")
    return df.rename(columns=rename)


def _parse_test_date(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")


def _zip_to_string(zip_raw: Any) -> str | None:
    if pd.isna(zip_raw):
        return None
    try:
        s = f"{int(float(zip_raw)):05d}"
    except (TypeError, ValueError):
        s = "".join(ch for ch in str(zip_raw).strip() if ch.isdigit())
    if len(s) != 5:
        return None
    return s


def infer_result_category_code(result_mgl: float | None) -> float | None:
    """Return 0–3 category code consistent with observed labeled ranges, or None if unknown."""
    if result_mgl is None or pd.isna(result_mgl):
        return None
    val = float(result_mgl)
    if val <= 0:
        return 0.0
    if val < 0.005:
        return 1.0
    if val < 0.01:
        return 2.0
    return 3.0


def _severity_label(code: float | None) -> str | None:
    if code is None or pd.isna(code):
        return None
    c = int(float(code))
    return {
        0: "non_detect",
        1: "detect_low_below_half_mcl_band",
        2: "detect_moderate_below_mcl",
        3: "at_or_above_mcl_reference",
    }.get(c, "unknown")


def clean_arsenic_dataframe(raw: pd.DataFrame) -> pd.DataFrame:
    """Return cleaned arsenic table; does not mutate input."""
    out = _standardize_columns(raw.copy())
    n_start = len(out)

    out["test_date"] = _parse_test_date(out["test_date"])
    out["year"] = out["test_date"].dt.year
    out["month"] = out["test_date"].dt.month

    out["city"] = out["city"].astype(str).str.strip().str.title()
    out["state"] = out["state"].astype(str).str.strip().str.upper()
    out["street"] = out["street"].astype(str).str.strip()
    out["full_address"] = out["full_address"].astype(str).str.strip()
    out["property_address"] = out["property_address"].astype(str).str.strip()

    out["zip5"] = out["zip_raw"].map(_zip_to_string)

    out["result_mgl"] = pd.to_numeric(out["result_mgl"], errors="coerce")
    out["result_category_code_raw"] = pd.to_numeric(
        out["result_category_code_raw"], errors="coerce"
    )

    inferred = out["result_mgl"].map(infer_result_category_code)
    out["result_category_code"] = out["result_category_code_raw"].where(
        out["result_category_code_raw"].notna(), inferred
    )
    out["result_category_inferred"] = out["result_category_code_raw"].isna() & out[
        "result_category_code"
    ].notna()

    out["contamination_severity"] = out["result_category_code"].map(_severity_label)

    dup_count = int(out.duplicated().sum())
    out = out.drop_duplicates()
    n_after_dedupe = len(out)

    logger.info("Arsenic rows: start=%s after_dedupe=%s duplicates_removed=%s", n_start, n_after_dedupe, dup_count)
    logger.info("Missing zip5: %s", int(out["zip5"].isna().sum()))
    logger.info("Missing result_category after fill: %s", int(out["result_category_code"].isna().sum()))
    logger.info("Result_Cat rules (confirm with owner): %s", RESULT_CAT_RULES_DOC)

    cols = [
        "test_date",
        "year",
        "month",
        "street",
        "city",
        "state",
        "zip5",
        "zip_raw",
        "test_name",
        "result_mgl",
        "result_category_code_raw",
        "result_category_code",
        "result_category_inferred",
        "contamination_severity",
        "full_address",
        "property_address",
    ]
    return out[cols].sort_values(["test_date", "city", "full_address"]).reset_index(drop=True)


def load_raw_arsenic(path: str | Path | None = None) -> pd.DataFrame:
    p = Path(path) if path is not None else ARSENIC_RAW_XLSX
    return pd.read_excel(p, sheet_name="Sheet1")


def run_clean_arsenic(
    raw_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> pd.DataFrame:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raw = load_raw_arsenic(raw_path)
    cleaned = clean_arsenic_dataframe(raw)
    out = Path(output_path) if output_path is not None else ARSENIC_CLEAN_CSV
    out.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(out, index=False)
    logger.info("Wrote %s rows to %s", len(cleaned), out)
    return cleaned


if __name__ == "__main__":
    run_clean_arsenic()
