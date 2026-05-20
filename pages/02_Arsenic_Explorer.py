from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import plotly.io as pio
import streamlit as st
from streamlit_folium import st_folium

from src.analysis import arsenic_patterns as ap
from src.utils.paths import resolve_mi_counties_geojson
from src.visualization.folium_maps import build_arsenic_folium_map
from streamlit_app.cached_loaders import get_arsenic_enriched
from streamlit_app.download_section import render_download_section
from streamlit_app.export_arsenic import build_arsenic_export_bundle
from streamlit_app.ui_style import apply_dashboard_style

apply_dashboard_style()
pio.templates.default = "plotly_dark"

_ARSENIC_CHART_STEMS = (
    "arsenic_histogram",
    "tests_per_year",
    "top_cities_by_tests",
    "county_elevated_rate",
)


st.title("Arsenic Explorer")
st.caption("Private well arsenic tests — distributions, trends, and a ZIP-centroid map.")

with st.expander("How to interpret this page", expanded=False):
    st.markdown(
        """
        - **Results are in mg/L** in this file. The dashed **0.01 mg/L** line is a common *reference* level for drinking water in the U.S.—confirm what your program uses before external communication.
        - **Map points are ZIP centroids**, not exact taps. A county label comes from the ZIP reference table, so border ZIPs can look “wrong” at the county level.
        - **More tests in a city** usually means **more sampling activity**, not automatically worse water for every home.
        """
    )

df_full = get_arsenic_enriched()

years = sorted(df_full["year"].dropna().unique().astype(int).tolist())
cities = sorted(df_full["city"].dropna().unique().tolist())
severities = sorted(df_full["contamination_severity"].dropna().unique().tolist())

c1, c2, c3 = st.columns(3)
with c1:
    year_pick = st.multiselect("Years", years, default=years)
with c2:
    city_pick = st.multiselect("Cities (optional)", cities, default=[])
with c3:
    sev_pick = st.multiselect("Severity bands", severities, default=severities)

year_pick = year_pick or years
sev_pick = sev_pick or severities

filtered = df_full[df_full["year"].isin(year_pick)]
if city_pick:
    filtered = filtered[filtered["city"].isin(city_pick)]
filtered = filtered[filtered["contamination_severity"].isin(sev_pick)]

if filtered.empty:
    st.warning("No rows match your filters. Reset selections to see data.")
    st.stop()

st.subheader("Overview")
st.markdown(
    f"{ap.interpret_histogram(filtered)}\n\n"
    f"{ap.interpret_elevated_share(filtered)}\n\n"
    f"{ap.interpret_yearly_trend(filtered)}\n\n"
    f"{ap.interpret_top_cities(filtered)}\n\n"
    f"{ap.interpret_county_rates(filtered)}"
)

st.subheader("Results")
m1, m2, m3 = st.columns(3)
m1.metric("Tests shown", f"{len(filtered):,}")
m2.metric("At/above reference band", f"{ap.elevated_rate(filtered):.1f}%")
m3.metric("Cities represented", f"{filtered['city'].nunique():,}")

fig_hist = ap.figure_arsenic_histogram(filtered)
fig_year = ap.figure_tests_per_year(filtered)
fig_cities = ap.figure_top_cities(filtered)
fig_county = ap.figure_county_elevated_rate(filtered)

left, right = st.columns(2)
with left:
    st.plotly_chart(fig_hist, width="stretch")
with right:
    st.plotly_chart(fig_year, width="stretch")

left, right = st.columns(2)
with left:
    st.plotly_chart(fig_cities, width="stretch")
with right:
    st.plotly_chart(fig_county, width="stretch")

st.subheader("Interactive map")
st.caption("Markers are color-coded by severity; counties can be shaded by ZIP-linked elevated rate (where sample size allows).")

show_cluster = st.toggle("Cluster markers (recommended for many points)", value=True)
show_heat = st.toggle("Heat layer (result intensity)", value=False)

mappable = filtered.dropna(subset=["map_latitude", "map_longitude"])
fmap = None
if mappable.empty:
    st.warning(
        "No rows have map coordinates (missing ZIP match in `mi_zip_reference.csv`). "
        "Charts above still work; fix ZIPs or rebuild the reference to see points."
    )
else:
    fmap = build_arsenic_folium_map(
        filtered,
        resolve_mi_counties_geojson(),
        show_cluster=show_cluster,
        show_heatmap=show_heat,
        show_county_choropleth=True,
    )
    st_folium(fmap, use_container_width=True, height=650)

st.subheader("Download figures & map")
st.caption(
    "Each chart exports as **PNG** (static image for slides) and **HTML** (interactive Plotly). "
    "The map includes **interactive HTML** plus a **map snapshot PNG**. "
    "Exports do not launch Chrome (safe on macOS)."
)

render_download_section(
    lambda: build_arsenic_export_bundle(filtered, fmap, include_map=fmap is not None),
    chart_stems=_ARSENIC_CHART_STEMS,
    zip_prefix="arsenic_explorer",
    export_key=(
        len(filtered),
        tuple(year_pick),
        tuple(sorted(city_pick)),
        tuple(sev_pick),
        show_cluster,
        show_heat,
        fmap is not None,
    ),
    session_bundle_key="arsenic_export_bundle",
    session_key_key="arsenic_export_key",
)
