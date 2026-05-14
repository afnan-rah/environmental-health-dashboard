"""Exploratory metrics and Plotly charts for mosquito surveillance."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def figure_species_counts(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    sub = df.copy()
    sub["species_label"] = sub["species_binomial"].fillna("Unidentified / not recorded")
    counts = (
        sub.groupby("species_label", as_index=False)
        .size()
        .rename(columns={"size": "records"})
        .sort_values("records", ascending=False)
        .head(top_n)
    )
    fig = px.bar(
        counts.sort_values("records"),
        x="records",
        y="species_label",
        orientation="h",
        title=f"Top {top_n} species labels (including unidentified rows)",
        labels={"records": "Trap records", "species_label": "Species"},
    )
    fig.update_layout(template="plotly_white")
    return fig


def figure_season_counts(df: pd.DataFrame) -> go.Figure:
    order = ["spring", "summer", "fall", "winter"]
    counts = df.groupby("season", as_index=False).size().rename(columns={"size": "records"})
    counts["season"] = pd.Categorical(counts["season"], categories=order, ordered=True)
    counts = counts.sort_values("season")
    fig = px.bar(
        counts,
        x="season",
        y="records",
        title="Trap records by season (based on trap set month)",
        labels={"season": "Season", "records": "Records"},
    )
    fig.update_layout(template="plotly_white")
    return fig


def figure_detection_by_month(df: pd.DataFrame) -> go.Figure:
    sub = df[df["trap_set_month"].notna()].copy()
    sub["month"] = sub["trap_set_month"].astype(int)
    det = (
        sub.groupby(["month", "detected_normalized"], as_index=False)
        .size()
        .rename(columns={"size": "records"})
    )
    fig = px.bar(
        det,
        x="month",
        y="records",
        color="detected_normalized",
        title="Detection outcomes by trap-set month",
        labels={"month": "Month", "records": "Records", "detected_normalized": "Outcome"},
    )
    fig.update_layout(template="plotly_white", barmode="stack")
    return fig


def figure_site_type_totals(df: pd.DataFrame) -> go.Figure:
    tbl = (
        df.groupby("collection_site_type", as_index=False)
        .agg(records=("collection_site_type", "size"), adults=("total_adults_collected", "sum"))
        .sort_values("records", ascending=False)
    )
    fig = px.bar(
        tbl,
        x="collection_site_type",
        y="records",
        title="Where traps were placed (record counts)",
        labels={"collection_site_type": "Site type", "records": "Trap records"},
    )
    fig.update_layout(template="plotly_white", xaxis_tickangle=-25)
    return fig


def figure_site_type_avg_catch(df: pd.DataFrame) -> go.Figure:
    tbl = (
        df.groupby("collection_site_type", as_index=False)["total_adults_collected"]
        .mean()
        .sort_values("total_adults_collected", ascending=False)
    )
    fig = px.bar(
        tbl,
        x="collection_site_type",
        y="total_adults_collected",
        title="Average adult mosquitoes collected per record, by site type",
        labels={"collection_site_type": "Site type", "total_adults_collected": "Mean adults"},
    )
    fig.update_layout(template="plotly_white", xaxis_tickangle=-25)
    return fig


def interpret_species(df: pd.DataFrame) -> str:
    top = (
        df.assign(species_label=df["species_binomial"].fillna("Unidentified / not recorded"))
        .groupby("species_label")
        .size()
        .sort_values(ascending=False)
        .head(2)
    )
    if top.empty:
        return "Species labels are missing for most rows—interpret species charts cautiously."
    lead = top.index[0]
    return (
        f"The most common label is **{lead}**, which often reflects **genus-level reporting** (for example “Culex sp.”) rather than a single species everywhere. "
        "That is normal in surveillance templates, but it limits fine-grained species risk statements."
    )


def interpret_season(df: pd.DataFrame) -> str:
    counts = df.groupby("season").size()
    if counts.empty:
        return "Season could not be computed for most rows."
    peak = counts.idxmax()
    return (
        f"Activity is concentrated in **{str(peak).title()}** in this 2021 Kent extract. "
        "Seasonal patterns reflect **weather and ecology**, but they also reflect **where and when your program chose to trap**."
    )


def interpret_detection(df: pd.DataFrame) -> str:
    known = df["detected_normalized"].notna()
    if not known.any():
        return "Detection outcomes are mostly missing—check the raw “Detected” field and template guidance."
    pos_share = float((df.loc[known, "detected_normalized"] == "positive").mean() * 100)
    return (
        f"Among rows with a known detection label, about **{pos_share:.1f}%** are marked **positive**. "
        "“ND” means not detected for the target assay in that batch—**not** “no mosquitoes present.”"
    )


def interpret_site_types(df: pd.DataFrame) -> str:
    top = (
        df.groupby("collection_site_type", as_index=False)
        .size()
        .rename(columns={"size": "records"})
        .sort_values("records", ascending=False)
        .head(1)
    )
    if top.empty:
        return "Site type information is missing."
    name = top.iloc[0]["collection_site_type"]
    return (
        f"Most records come from **{name}** settings in this file. "
        "Comparing site types is useful for **operations and outreach**, but it is not a randomized experiment—**trap protocols differ** by location type."
    )
