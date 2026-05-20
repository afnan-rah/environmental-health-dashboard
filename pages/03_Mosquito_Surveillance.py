from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from streamlit_folium import st_folium

from src.analysis import mosquito_patterns as mp
from src.visualization.folium_maps import build_mosquito_folium_map
from streamlit_app.cached_loaders import get_mosquito_enriched
from streamlit_app.download_section import render_download_section
from streamlit_app.export_mosquito import build_mosquito_export_bundle
from streamlit_app.ui_style import ensure_theme_applied

_MOSQUITO_CHART_STEMS = (
    "species_counts",
    "season_counts",
    "detection_by_month",
    "site_type_totals",
    "site_type_avg_catch",
)

ensure_theme_applied()


st.title("Mosquito Surveillance")
st.caption("Kent-area 2021 template extract — species mix, seasonality, detections, and a city-centered map.")

with st.expander("How to interpret this page", expanded=False):
    st.markdown(
        """
        - **“ND”** usually means the target pathogen was **not detected** in that laboratory batch—it does **not** mean the trap was empty.
        - **Species labels** often read as “Genus sp.” That is normal for surveillance, but it limits species-specific conclusions.
        - **Map points are city centroids with a small jitter** so overlapping traps separate visually—they are **not GPS trap coordinates**.
        """
    )

df_full = get_mosquito_enriched()
species_opts = sorted(df_full["species_binomial"].fillna("Unidentified / not recorded").unique().tolist())
site_opts = sorted(df_full["collection_site_type"].dropna().unique().tolist())

c1, c2 = st.columns(2)
with c1:
    species_pick = st.multiselect("Species labels", species_opts, default=species_opts)
with c2:
    site_pick = st.multiselect("Site types", site_opts, default=site_opts)

species_pick = species_pick or species_opts
site_pick = site_pick or site_opts

filtered = df_full[df_full["species_binomial"].fillna("Unidentified / not recorded").isin(species_pick)]
if site_pick:
    filtered = filtered[filtered["collection_site_type"].isin(site_pick)]

if filtered.empty:
    st.warning("No rows match your filters.")
    st.stop()

st.subheader("Overview")
st.markdown(
    f"{mp.interpret_species(filtered)}\n\n"
    f"{mp.interpret_season(filtered)}\n\n"
    f"{mp.interpret_detection(filtered)}\n\n"
    f"{mp.interpret_site_types(filtered)}"
)

st.subheader("Results")
m1, m2, m3 = st.columns(3)
m1.metric("Records shown", f"{len(filtered):,}")
m2.metric(
    "Positive share (known outcomes)",
    f"{(filtered.loc[filtered['detected_normalized'].notna(), 'detected_normalized'] == 'positive').mean() * 100 if filtered['detected_normalized'].notna().any() else 0:.1f}%",
)
m3.metric("Median adults / record", f"{filtered['total_adults_collected'].median():.0f}")

left, right = st.columns(2)
with left:
    st.plotly_chart(mp.figure_species_counts(filtered), width="stretch")
with right:
    st.plotly_chart(mp.figure_season_counts(filtered), width="stretch")

st.plotly_chart(mp.figure_detection_by_month(filtered), width="stretch")

left, right = st.columns(2)
with left:
    st.plotly_chart(mp.figure_site_type_totals(filtered), width="stretch")
with right:
    st.plotly_chart(mp.figure_site_type_avg_catch(filtered), width="stretch")

st.subheader("Site map (city-centered)")
st.caption("Colors reflect detection labels where present.")

show_heat = st.toggle("Heat layer (adults collected intensity)", value=False)

fmap = build_mosquito_folium_map(filtered, show_heatmap=show_heat)
st_folium(fmap, use_container_width=True, height=650)

st.subheader("Download figures & map")
st.caption(
    "Each chart exports as **PNG** and **HTML** using the **same titles as on this page**. "
    "The map includes interactive HTML plus a static snapshot PNG."
)

render_download_section(
    lambda: build_mosquito_export_bundle(filtered, fmap, include_map=True),
    chart_stems=_MOSQUITO_CHART_STEMS,
    zip_prefix="mosquito_surveillance",
    export_key=(
        len(filtered),
        tuple(species_pick),
        tuple(sorted(site_pick)),
        show_heat,
    ),
    session_bundle_key="mosquito_export_bundle",
    session_key_key="mosquito_export_key",
)
