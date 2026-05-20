"""Folium map builders for dashboards and notebooks."""

from __future__ import annotations

import html
import json
from pathlib import Path

import folium
import pandas as pd
from folium.plugins import HeatMap, MarkerCluster

SEVERITY_COLORS: dict[str, str] = {
    "non_detect": "#9e9e9e",
    "detect_low_below_half_mcl_band": "#ffd54f",
    "detect_moderate_below_mcl": "#fb8c00",
    "at_or_above_mcl_reference": "#c62828",
}


def prefer_dark_basemap(dark_basemap: bool | None = None) -> bool:
    """Use light map tiles when the dashboard theme is light."""
    if dark_basemap is not None:
        return dark_basemap
    try:
        import streamlit as st

        return st.session_state.get("eh_theme", "dark") != "light"
    except Exception:
        return True


def _default_center(df: pd.DataFrame) -> tuple[float, float]:
    if df.empty or df["map_latitude"].isna().all():
        return 43.05, -85.68
    lat = float(df["map_latitude"].median())
    lon = float(df["map_longitude"].median())
    return lat, lon


def _popup_html(row: pd.Series) -> str:
    city = html.escape(str(row.get("city", "")))
    dt = html.escape(str(row.get("test_date", ""))[:10])
    res = row.get("result_mgl", float("nan"))
    sev = html.escape(str(row.get("contamination_severity", "")))
    zip5 = html.escape(str(row.get("zip5", "")))
    return (
        f"<div style='min-width:180px;font-size:13px'>"
        f"<b>{city}</b><br/>"
        f"ZIP: {zip5}<br/>"
        f"Test date: {dt}<br/>"
        f"Result: {res:.4f} mg/L<br/>"
        f"Severity: {sev}"
        f"</div>"
    )


def build_arsenic_folium_map(
    df: pd.DataFrame,
    county_geojson: str | Path,
    *,
    show_cluster: bool = True,
    show_heatmap: bool = False,
    show_county_choropleth: bool = True,
    choropleth_metric: str = "elevated_rate",
    dark_basemap: bool | None = None,
) -> folium.Map:
    """Interactive map: county outline, optional choropleth, clustered severity markers."""
    dark_basemap = prefer_dark_basemap(dark_basemap)
    plot_df = df.dropna(subset=["map_latitude", "map_longitude"]).copy()
    center = _default_center(plot_df)
    tiles = "CartoDB dark_matter" if dark_basemap else "cartodbpositron"
    m = folium.Map(location=list(center), zoom_start=9, tiles=tiles)

    gj_path = Path(county_geojson)
    geo_data = json.loads(gj_path.read_text())

    folium.GeoJson(
        geo_data,
        name="Michigan counties",
        style_function=lambda _feat: {
            "color": "#64748b" if dark_basemap else "#596e79",
            "weight": 1,
            "fillOpacity": 0.06 if dark_basemap else 0.02,
            "fillColor": "#1e293b" if dark_basemap else "#ffffff",
        },
    ).add_to(m)

    if show_county_choropleth and "county_fips" in plot_df.columns and choropleth_metric:
        g = plot_df.dropna(subset=["county_fips"]).copy()
        g["elevated_flag"] = (g["contamination_severity"] == "at_or_above_mcl_reference").astype(float)
        agg = (
            g.groupby("county_fips", as_index=False)
            .agg(tests=("elevated_flag", "size"), elevated_rate=("elevated_flag", "mean"))
        )
        if not agg.empty and agg["tests"].max() >= 5:
            choro = folium.Choropleth(
                geo_data=geo_data,
                data=agg,
                columns=["county_fips", "elevated_rate"],
                key_on="feature.id",
                fill_color="YlOrRd",
                line_color="#94a3b8" if dark_basemap else "#c7b198",
                line_weight=1,
                fill_opacity=0.5,
                nan_fill_opacity=0.05,
                legend_name="Share of tests at/above reference band",
                name="County choropleth (ZIP-linked)",
            )
            if choro.color_scale is not None:
                choro.color_scale.text_color = "#e8eef4" if dark_basemap else "#596e79"
            choro.add_to(m)

    markers_layer = MarkerCluster(name="Arsenic tests (clustered)") if show_cluster else None
    for _, row in plot_df.iterrows():
        color = SEVERITY_COLORS.get(str(row.get("contamination_severity")), "#607d8b")
        marker = folium.CircleMarker(
            location=(float(row["map_latitude"]), float(row["map_longitude"])),
            radius=6,
            color=color,
            weight=1,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            popup=folium.Popup(_popup_html(row), max_width=260),
        )
        if markers_layer is not None:
            marker.add_to(markers_layer)
        else:
            marker.add_to(m)
    if markers_layer is not None:
        markers_layer.add_to(m)

    if show_heatmap and not plot_df.empty:
        heat_data = [
            [float(r["map_latitude"]), float(r["map_longitude"]), float(r["result_mgl"] or 0.0)]
            for _, r in plot_df.iterrows()
        ]
        HeatMap(heat_data, radius=18, blur=22, min_opacity=0.25, name="Result intensity (heat)").add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    return m


MOSQUITO_COLORS = {
    "positive": "#c62828",
    "not_detected": "#2e7d32",
}


def build_mosquito_folium_map(
    df: pd.DataFrame, *, show_heatmap: bool = False, dark_basemap: bool | None = None
) -> folium.Map:
    dark_basemap = prefer_dark_basemap(dark_basemap)
    plot_df = df.dropna(subset=["map_latitude", "map_longitude"]).copy()
    center = _default_center(plot_df)
    tiles = "CartoDB dark_matter" if dark_basemap else "cartodbpositron"
    m = folium.Map(location=list(center), zoom_start=10, tiles=tiles)
    cluster = MarkerCluster(name="Surveillance records")
    for _, row in plot_df.iterrows():
        det = row.get("detected_normalized")
        if det is None or (isinstance(det, float) and pd.isna(det)):
            color = "#90a4ae"
        else:
            color = MOSQUITO_COLORS.get(str(det), "#546e7a")
        sp = html.escape(str(row.get("species_binomial", "Unknown")))
        site = html.escape(str(row.get("collection_site_type", "")))
        city = html.escape(str(row.get("city", "")))
        dt = html.escape(str(row.get("trap_set_date", ""))[:10])
        adults = int(row.get("total_adults_collected", 0) or 0)
        popup = (
            f"<div style='min-width:200px;font-size:13px'>"
            f"<b>{city}</b> — {site}<br/>"
            f"Date: {dt}<br/>"
            f"Species: {sp}<br/>"
            f"Adults collected: {adults}<br/>"
            f"Detection: {html.escape(str(det))}"
            f"</div>"
        )
        folium.CircleMarker(
            location=(float(row["map_latitude"]), float(row["map_longitude"])),
            radius=6,
            color=color,
            weight=1,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            popup=folium.Popup(popup, max_width=280),
        ).add_to(cluster)
    cluster.add_to(m)

    if show_heatmap and not plot_df.empty:
        weights = plot_df["total_adults_collected"].fillna(0).astype(float).clip(lower=0.5)
        cap = float(weights.quantile(0.95)) if len(weights) > 1 else float(weights.max())
        cap = max(cap, 1.0)
        heat_data = [
            [float(lat), float(lon), min(float(w), cap) / cap]
            for lat, lon, w in zip(
                plot_df["map_latitude"].astype(float),
                plot_df["map_longitude"].astype(float),
                weights,
            )
        ]
        HeatMap(
            heat_data,
            radius=20,
            blur=18,
            min_opacity=0.22,
            name="Adults collected (heat)",
        ).add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    return m
