#!/usr/bin/env python3
"""Download a Michigan-only county GeoJSON for offline mapping overlays."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "data" / "geo" / "mi_counties.geojson"
    out.parent.mkdir(parents=True, exist_ok=True)

    url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
    with urllib.request.urlopen(url, timeout=120) as resp:
        gj = json.load(resp)

    mi_features = [f for f in gj["features"] if str(f.get("id", "")).startswith("26")]
    out.write_text(json.dumps({"type": "FeatureCollection", "features": mi_features}))
    print(f"Wrote {len(mi_features)} county features to {out}")


if __name__ == "__main__":
    main()
