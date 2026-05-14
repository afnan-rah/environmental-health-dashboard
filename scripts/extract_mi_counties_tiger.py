#!/usr/bin/env python3
"""
Extract Michigan counties from U.S. Census TIGER/Line ``tl_*_us_county`` shapefiles (Phase 4).

Reads the national county layer, filters ``STATEFP == '26'``, reprojects to WGS84,
optionally simplifies geometry, and writes a small GeoJSON for Folium/GeoPandas.

Example:
  python scripts/extract_mi_counties_tiger.py --year 2025
  python scripts/extract_mi_counties_tiger.py --year 2024 --simplify 0.002
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", choices=("2024", "2025"), default="2025")
    parser.add_argument(
        "--simplify",
        type=float,
        default=0.001,
        help="Degree tolerance for simplify() (0 disables). ~0.001 is light; larger = smaller file.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    shp = root / "data" / "raw" / f"tl_{args.year}_us_county" / f"tl_{args.year}_us_county.shp"
    if not shp.exists():
        raise SystemExit(f"Missing shapefile: {shp}")

    out = root / "data" / "geo" / f"mi_counties_tiger{args.year}.geojson"
    out.parent.mkdir(parents=True, exist_ok=True)

    g = gpd.read_file(shp)
    mi = g[g["STATEFP"] == "26"].copy()
    if len(mi) != 83:
        print(f"warning: expected 83 MI counties, got {len(mi)}")

    mi = mi.to_crs(4326)
    if args.simplify and args.simplify > 0:
        mi["geometry"] = mi.geometry.simplify(args.simplify, preserve_topology=True)

    # Folium Choropleth uses ``feature.id`` in this project — mirror GEOID there.
    payload = json.loads(mi.to_json())
    for feat in payload.get("features", []):
        props = feat.setdefault("properties", {})
        geoid = props.get("GEOID")
        if geoid is not None:
            feat["id"] = str(geoid)

    out.write_text(json.dumps(payload))
    print(f"Wrote {len(mi)} features to {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
