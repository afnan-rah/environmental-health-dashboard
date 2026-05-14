"""Exploratory metrics and Plotly charts for arsenic well tests."""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def figure_arsenic_histogram(df: pd.DataFrame) -> go.Figure:
    sub = df.copy()
    sub["result_display_mgl"] = sub["result_mgl"].clip(upper=sub["result_mgl"].quantile(0.99))
    fig = px.histogram(
        sub,
        x="result_mgl",
        nbins=40,
        title="Distribution of arsenic results (mg/L)",
        labels={"result_mgl": "Arsenic (mg/L)", "count": "Number of tests"},
    )
    fig.add_vline(x=0.01, line_dash="dash", line_color="red", annotation_text="0.01 mg/L reference line")
    fig.update_layout(template="plotly_white", bargap=0.05)
    return fig


def figure_tests_per_year(df: pd.DataFrame) -> go.Figure:
    counts = df.groupby("year", as_index=False).size().rename(columns={"size": "tests"})
    fig = px.bar(
        counts,
        x="year",
        y="tests",
        title="How many arsenic tests appear in each calendar year?",
        labels={"year": "Year", "tests": "Tests recorded"},
    )
    fig.update_layout(template="plotly_white")
    return fig


def top_cities_by_tests(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return (
        df.groupby("city", as_index=False)
        .size()
        .rename(columns={"size": "tests"})
        .sort_values("tests", ascending=False)
        .head(n)
    )


def figure_top_cities(df: pd.DataFrame, n: int = 10) -> go.Figure:
    tbl = top_cities_by_tests(df, n=n)
    fig = px.bar(
        tbl.sort_values("tests"),
        x="tests",
        y="city",
        orientation="h",
        title=f"Top {n} cities by number of tests",
        labels={"tests": "Tests", "city": "City"},
    )
    fig.update_layout(template="plotly_white")
    return fig


def county_testing_table(enriched: pd.DataFrame) -> pd.DataFrame:
    """Expects ``county_from_zip`` from ``enrich_arsenic_for_maps``."""
    if "county_from_zip" not in enriched.columns:
        return pd.DataFrame(columns=["county_from_zip", "tests", "elevated_share"])
    g = enriched.dropna(subset=["county_from_zip"]).copy()
    g["elevated"] = g["contamination_severity"] == "at_or_above_mcl_reference"
    out = (
        g.groupby("county_from_zip", as_index=False)
        .agg(tests=("result_mgl", "size"), elevated_share=("elevated", "mean"))
    )
    out["elevated_pct"] = (out["elevated_share"] * 100).round(1)
    return out.sort_values("tests", ascending=False)


def figure_county_elevated_rate(enriched: pd.DataFrame, top_n: int = 12) -> go.Figure:
    tbl = county_testing_table(enriched).head(top_n)
    fig = px.bar(
        tbl.sort_values("elevated_pct"),
        x="elevated_pct",
        y="county_from_zip",
        orientation="h",
        title="Share of tests at/above reference band (by county from ZIP)",
        labels={"elevated_pct": "Percent of tests (%)", "county_from_zip": "County"},
        hover_data={"tests": True},
    )
    fig.update_layout(template="plotly_white")
    return fig


def elevated_rate(df: pd.DataFrame) -> float:
    mask = df["contamination_severity"] == "at_or_above_mcl_reference"
    return float(mask.mean() * 100) if len(df) else 0.0


def interpret_histogram(df: pd.DataFrame) -> str:
    zeros = float((df["result_mgl"] <= 0).mean() * 100)
    elevated = elevated_rate(df)
    return (
        f"About **{zeros:.1f}%** of tests report exactly **0 mg/L** (non-detect style values). "
        f"About **{elevated:.1f}%** fall in the **at/above reference** band used in this dataset. "
        "The red dashed line marks **0.01 mg/L**, a common drinking-water reference point—confirm local rules."
    )


def interpret_yearly_trend(df: pd.DataFrame) -> str:
    counts = df.groupby("year").size()
    if counts.empty:
        return "Not enough years to describe a trend."
    recent_years = sorted(counts.index)[-3:]
    prior_years = [y for y in counts.index if y not in recent_years]
    recent_mean = counts.loc[recent_years].mean() if recent_years else float("nan")
    prior_mean = counts.loc[prior_years].mean() if prior_years else float("nan")
    if prior_years and recent_mean > prior_mean * 1.25:
        return (
            "Testing counts in the **most recent years** are higher than the long-run average. "
            "That often reflects **more sampling activity** (new wells, outreach, or program changes)—not necessarily worse water everywhere."
        )
    if prior_years and recent_mean < prior_mean * 0.75:
        return (
            "Recent years show **fewer recorded tests** than earlier years. "
            "This can reflect **data entry gaps**, program changes, or fewer samples—worth confirming before interpreting as improved conditions."
        )
    return (
        "Year-to-year test counts look **relatively steady**. "
        "Use the year filter in the dashboard to focus on periods you care about, and remember counts reflect **testing activity** as well as underlying conditions."
    )


def interpret_top_cities(df: pd.DataFrame) -> str:
    top = top_cities_by_tests(df, n=3)
    if top.empty:
        return "No city information available."
    names = ", ".join(top["city"].tolist())
    return (
        f"The cities with the most records right now are **{names}**. "
        "That usually means **more addresses tested** there—not automatically higher risk for every household."
    )


def interpret_county_rates(enriched: pd.DataFrame) -> str:
    tbl = county_testing_table(enriched)
    if tbl.empty:
        return "County summaries need a successful ZIP-to-county match; several ZIPs may be missing from the reference table."
    top = tbl.sort_values("elevated_pct", ascending=False).iloc[0]
    return (
        f"Among counties with enough tests to compare, **{top['county_from_zip']}** shows the highest share "
        f"of tests in the **at/above reference** band (**{top['elevated_pct']:.1f}%** over **{int(top['tests'])}** tests). "
        "County labels come from **ZIP-code reference areas**, so edge communities can look mis-assigned—treat as exploratory."
    )


def interpret_elevated_share(df: pd.DataFrame) -> str:
    pct = elevated_rate(df)
    return (
        f"**{pct:.1f}%** of cleaned tests are labeled **at/above the reference band** in this file. "
        "That percentage is useful for **program monitoring**, but it is **not** the same as population exposure without knowing which taps people actually drink from."
    )
