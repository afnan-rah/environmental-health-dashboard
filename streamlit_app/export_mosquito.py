"""Downloadable exports for Mosquito Surveillance (matplotlib PNG + Plotly HTML)."""

from __future__ import annotations

from io import BytesIO

import folium
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go

from src.analysis import mosquito_patterns as mp
from src.visualization.folium_maps import MOSQUITO_COLORS
from streamlit_app.export_common import (
    ExportBundle,
    fig_html,
    map_html,
    mpl_axes,
    mpl_save,
    mpl_style_axes,
    plotly_title,
    plotly_xlabel,
    plotly_ylabel,
    zip_bytes,
    zip_html_only,
    zip_png_only,
)

__all__ = [
    "ExportBundle",
    "build_mosquito_export_bundle",
    "zip_bytes",
    "zip_png_only",
    "zip_html_only",
]

_DETECTION_COLORS = {
    "positive": "#c62828",
    "not_detected": "#2e7d32",
}


def chart_png_mpl(stem: str, filtered, fig: go.Figure) -> bytes | None:
    title = plotly_title(fig, stem)
    xlab = plotly_xlabel(fig)
    ylab = plotly_ylabel(fig)

    if stem == "species_counts":
        sub = filtered.copy()
        sub["species_label"] = sub["species_binomial"].fillna("Unidentified / not recorded")
        counts = (
            sub.groupby("species_label", as_index=False)
            .size()
            .rename(columns={"size": "records"})
            .sort_values("records", ascending=False)
            .head(10)
            .sort_values("records")
        )
        if counts.empty:
            return None
        f, ax = mpl_axes((8, 6))
        ax.barh(counts["species_label"], counts["records"], color="#a78bfa")
        mpl_style_axes(ax, title=title, xlabel=xlab or "Trap records", ylabel=ylab or "Species")
        return mpl_save(f)

    if stem == "season_counts":
        order = ["spring", "summer", "fall", "winter"]
        counts = filtered.groupby("season", as_index=False).size().rename(columns={"size": "records"})
        counts["season"] = pd.Categorical(counts["season"], categories=order, ordered=True)
        counts = counts.sort_values("season")
        if counts.empty:
            return None
        f, ax = mpl_axes((8, 5))
        ax.bar(counts["season"].astype(str), counts["records"], color="#38bdf8")
        mpl_style_axes(ax, title=title, xlabel=xlab or "Season", ylabel=ylab or "Records")
        return mpl_save(f)

    if stem == "detection_by_month":
        sub = filtered[filtered["trap_set_month"].notna()].copy()
        if sub.empty:
            return None
        sub["month"] = sub["trap_set_month"].astype(int)
        det = (
            sub.groupby(["month", "detected_normalized"])
            .size()
            .unstack(fill_value=0)
            .sort_index()
        )
        if det.empty:
            return None
        f, ax = mpl_axes((9, 5))
        bottom = None
        for col in det.columns:
            color = _DETECTION_COLORS.get(str(col), "#546e7a")
            ax.bar(
                det.index.astype(str),
                det[col].values,
                bottom=bottom,
                label=str(col),
                color=color,
            )
            bottom = det[col].values if bottom is None else bottom + det[col].values
        mpl_style_axes(ax, title=title, xlabel=xlab or "Month", ylabel=ylab or "Records")
        ax.legend(facecolor="#151f32", labelcolor="#e8eef7", fontsize=8)
        return mpl_save(f)

    if stem == "site_type_totals":
        tbl = (
            filtered.groupby("collection_site_type", as_index=False)
            .size()
            .rename(columns={"size": "records"})
            .sort_values("records", ascending=False)
        )
        if tbl.empty:
            return None
        f, ax = mpl_axes((9, 5))
        ax.bar(tbl["collection_site_type"], tbl["records"], color="#2dd4bf")
        mpl_style_axes(ax, title=title, xlabel=xlab or "Site type", ylabel=ylab or "Trap records")
        plt.setp(ax.get_xticklabels(), rotation=-25, ha="left")
        return mpl_save(f)

    if stem == "site_type_avg_catch":
        tbl = (
            filtered.groupby("collection_site_type", as_index=False)["total_adults_collected"]
            .mean()
            .sort_values("total_adults_collected", ascending=False)
        )
        if tbl.empty:
            return None
        f, ax = mpl_axes((9, 5))
        ax.bar(tbl["collection_site_type"], tbl["total_adults_collected"], color="#fb923c")
        mpl_style_axes(ax, title=title, xlabel=xlab or "Site type", ylabel=ylab or "Mean adults")
        plt.setp(ax.get_xticklabels(), rotation=-25, ha="left")
        return mpl_save(f)

    return None


def map_snapshot_png(filtered, *, dpi: int = 150) -> bytes | None:
    plot_df = filtered.dropna(subset=["map_latitude", "map_longitude"])
    if plot_df.empty:
        return None

    f, ax = mpl_axes((10, 8))
    for det, group in plot_df.groupby("detected_normalized", dropna=False):
        color = MOSQUITO_COLORS.get(str(det), "#90a4ae")
        ax.scatter(
            group["map_longitude"],
            group["map_latitude"],
            c=color,
            s=28,
            alpha=0.85,
            edgecolors="white",
            linewidths=0.3,
            label=str(det) if det is not None else "unknown",
        )
    mpl_style_axes(
        ax,
        title="Mosquito surveillance (city-centered)",
        xlabel="Longitude",
        ylabel="Latitude",
    )
    leg = ax.legend(loc="upper right", fontsize=8, framealpha=0.85)
    if leg:
        for text in leg.get_texts():
            text.set_color("#e8eef7")
    buf = BytesIO()
    f.tight_layout()
    f.savefig(buf, format="png", dpi=dpi, facecolor=f.get_facecolor())
    plt.close(f)
    return buf.getvalue()


def _add_chart_pair(bundle: ExportBundle, stem: str, fig: go.Figure, filtered) -> None:
    bundle.chart_labels[stem] = plotly_title(fig, stem)
    bundle.files[f"{stem}.html"] = fig_html(fig)
    png = chart_png_mpl(stem, filtered, fig)
    if png is not None:
        bundle.files[f"{stem}.png"] = png
        bundle.png_chart_count += 1
    else:
        bundle.png_errors.append(f"{bundle.chart_labels[stem]}: no data for PNG export")


def build_mosquito_export_bundle(
    filtered,
    fmap: folium.Map | None,
    *,
    include_map: bool = True,
) -> ExportBundle:
    bundle = ExportBundle()
    _add_chart_pair(bundle, "species_counts", mp.figure_species_counts(filtered), filtered)
    _add_chart_pair(bundle, "season_counts", mp.figure_season_counts(filtered), filtered)
    _add_chart_pair(bundle, "detection_by_month", mp.figure_detection_by_month(filtered), filtered)
    _add_chart_pair(bundle, "site_type_totals", mp.figure_site_type_totals(filtered), filtered)
    _add_chart_pair(bundle, "site_type_avg_catch", mp.figure_site_type_avg_catch(filtered), filtered)

    if include_map and fmap is not None:
        bundle.files["interactive_map.html"] = map_html(fmap)
        bundle.chart_labels["interactive_map"] = "Interactive map (city-centered surveillance)"
        snap = map_snapshot_png(filtered)
        if snap is not None:
            bundle.files["map_snapshot.png"] = snap
            bundle.chart_labels["map_snapshot"] = "Map snapshot (city-centered)"
            bundle.png_chart_count += 1
    return bundle
