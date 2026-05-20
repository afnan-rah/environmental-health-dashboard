"""Downloadable exports for the Arsenic Explorer (matplotlib PNG + Plotly HTML)."""

from __future__ import annotations

from io import BytesIO

import folium
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from src.analysis import arsenic_patterns as ap
from src.visualization.folium_maps import SEVERITY_COLORS
from streamlit_app.export_common import (
    ExportBundle,
    _MPL_BG,
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
    "build_arsenic_export_bundle",
    "zip_bytes",
    "zip_png_only",
    "zip_html_only",
]


def chart_png_mpl(stem: str, filtered, fig: go.Figure) -> bytes | None:
    title = plotly_title(fig, stem)
    xlab = plotly_xlabel(fig)
    ylab = plotly_ylabel(fig)

    if stem == "arsenic_histogram":
        sub = filtered["result_mgl"].dropna()
        if sub.empty:
            return None
        f, ax = mpl_axes((8, 5))
        ax.hist(sub, bins=40, color="#2dd4bf", edgecolor=_MPL_BG, alpha=0.9)
        ax.axvline(0.01, color="#ef4444", linestyle="--", linewidth=1.5, label="0.01 mg/L reference line")
        mpl_style_axes(ax, title=title, xlabel=xlab or "Arsenic (mg/L)", ylabel=ylab or "Number of tests")
        ax.legend(facecolor="#151f32", labelcolor="#e8eef7")
        return mpl_save(f)

    if stem == "tests_per_year":
        counts = filtered.groupby("year").size()
        if counts.empty:
            return None
        f, ax = mpl_axes((8, 5))
        ax.bar(counts.index.astype(str), counts.values, color="#38bdf8")
        mpl_style_axes(ax, title=title, xlabel=xlab or "Year", ylabel=ylab or "Tests recorded")
        return mpl_save(f)

    if stem == "top_cities_by_tests":
        tbl = ap.top_cities_by_tests(filtered, n=10).sort_values("tests")
        if tbl.empty:
            return None
        f, ax = mpl_axes((8, 6))
        ax.barh(tbl["city"], tbl["tests"], color="#a78bfa")
        mpl_style_axes(ax, title=title, xlabel=xlab or "Tests", ylabel=ylab or "City")
        return mpl_save(f)

    if stem == "county_elevated_rate":
        tbl = ap.county_testing_table(filtered).head(12).sort_values("elevated_pct")
        if tbl.empty:
            return None
        f, ax = mpl_axes((8, 6))
        ax.barh(tbl["county_from_zip"], tbl["elevated_pct"], color="#fb923c")
        mpl_style_axes(
            ax,
            title=title,
            xlabel=xlab or "Percent of tests (%)",
            ylabel=ylab or "County",
        )
        return mpl_save(f)

    return None


def map_snapshot_png(filtered, *, dpi: int = 150) -> bytes | None:
    plot_df = filtered.dropna(subset=["map_latitude", "map_longitude"])
    if plot_df.empty:
        return None

    f, ax = mpl_axes((10, 8))
    for sev, group in plot_df.groupby("contamination_severity", dropna=False):
        color = SEVERITY_COLORS.get(str(sev), "#607d8b")
        ax.scatter(
            group["map_longitude"],
            group["map_latitude"],
            c=color,
            s=28,
            alpha=0.85,
            edgecolors="white",
            linewidths=0.3,
            label=str(sev) if sev is not None else "unknown",
        )
    mpl_style_axes(
        ax,
        title="Arsenic tests (ZIP centroids)",
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


def build_arsenic_export_bundle(
    filtered,
    fmap: folium.Map | None,
    *,
    include_map: bool = True,
) -> ExportBundle:
    bundle = ExportBundle()
    _add_chart_pair(bundle, "arsenic_histogram", ap.figure_arsenic_histogram(filtered), filtered)
    _add_chart_pair(bundle, "tests_per_year", ap.figure_tests_per_year(filtered), filtered)
    _add_chart_pair(bundle, "top_cities_by_tests", ap.figure_top_cities(filtered), filtered)
    _add_chart_pair(bundle, "county_elevated_rate", ap.figure_county_elevated_rate(filtered), filtered)

    if include_map and fmap is not None:
        bundle.files["interactive_map.html"] = map_html(fmap)
        bundle.chart_labels["interactive_map"] = "Interactive map (ZIP-centroid arsenic tests)"
        snap = map_snapshot_png(filtered)
        if snap is not None:
            bundle.files["map_snapshot.png"] = snap
            bundle.chart_labels["map_snapshot"] = "Map snapshot (ZIP centroids)"
            bundle.png_chart_count += 1
    return bundle
