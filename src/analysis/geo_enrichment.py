"""Attach approximate map coordinates and county labels using ZIP and city references."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

from src.utils.paths import (
    KENT_CITY_CENTROIDS_CSV,
    ZIP_REFERENCE_CSV,
    resolve_mi_counties_geojson,
)


def _county_fips_lookup(geojson_path: Path) -> dict[str, str]:
    data = json.loads(Path(geojson_path).read_text())
    lookup: dict[str, str] = {}
    for feat in data.get("features", []):
        props = feat.get("properties", {}) or {}
        name = props.get("NAME")
        fid = feat.get("id")
        if fid is None and props.get("GEOID") is not None:
            fid = str(props["GEOID"])
        if name and fid is not None:
            lookup[str(name).strip().lower()] = str(fid)
    return lookup


def load_zip_reference() -> pd.DataFrame:
    return pd.read_csv(ZIP_REFERENCE_CSV, dtype={"zip5": str})


def load_city_centroids() -> pd.DataFrame:
    return pd.read_csv(KENT_CITY_CENTROIDS_CSV)


def enrich_arsenic_for_maps(df: pd.DataFrame) -> pd.DataFrame:
    """Add ZIP centroid coordinates and county FIPS for choropleth joins."""
    z = load_zip_reference()
    out = df.merge(z, on="zip5", how="left", suffixes=("", "_zipref"))
    out = out.rename(
        columns={
            "latitude": "map_latitude",
            "longitude": "map_longitude",
            "county_name": "county_from_zip",
        }
    )
    lookup = _county_fips_lookup(resolve_mi_counties_geojson())
    county_key = out["county_from_zip"].astype(str).str.strip().str.lower()
    out["county_fips"] = county_key.map(lambda n: lookup.get(n) if n and n != "nan" else None)
    return out


def enrich_mosquito_for_maps(df: pd.DataFrame) -> pd.DataFrame:
    """Join city centroids and add a small deterministic jitter so markers separate."""
    cities = load_city_centroids()
    merged = df.merge(cities[["city", "latitude", "longitude"]], on="city", how="left")
    merged = merged.rename(columns={"latitude": "map_latitude", "longitude": "map_longitude"})

    def jitter(row: pd.Series) -> tuple[float, float]:
        key = str(row.get("collection_location_id", row.name))
        h = int(hashlib.md5(key.encode(), usedforsecurity=False).hexdigest()[:8], 16)
        dx = ((h % 101) - 50) / 8000.0
        dy = (((h // 101) % 101) - 50) / 8000.0
        return dx, dy

    jit = merged.apply(jitter, axis=1)
    merged["map_jitter_lon"] = jit.apply(lambda t: t[0])
    merged["map_jitter_lat"] = jit.apply(lambda t: t[1])
    merged["map_latitude"] = merged["map_latitude"] + merged["map_jitter_lat"]
    merged["map_longitude"] = merged["map_longitude"] + merged["map_jitter_lon"]
    return merged
