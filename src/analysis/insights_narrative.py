"""Plain-language synthesis strings for the Environmental Insights page."""

from __future__ import annotations

import pandas as pd

from src.analysis.arsenic_patterns import elevated_rate


def testing_activity_story(arsenic: pd.DataFrame) -> str:
    counts = arsenic.groupby("year").size().sort_index()
    if counts.empty:
        return "No arsenic test dates were available to describe multi-year activity."
    peak_year = int(counts.idxmax())
    return (
        f"The busiest calendar year in this extract is **{peak_year}** with **{int(counts.max())}** tests recorded. "
        "Interpreting peaks as “more contamination” is tempting, but it is often **more sampling**—especially when programs expand outreach."
    )


def hotspot_story(arsenic_enriched: pd.DataFrame) -> str:
    tbl = (
        arsenic_enriched.dropna(subset=["county_from_zip"])
        .assign(elevated=lambda d: d["contamination_severity"] == "at_or_above_mcl_reference")
        .groupby("county_from_zip", as_index=False)
        .agg(tests=("elevated", "size"), elevated_rate=("elevated", "mean"))
    )
    if tbl.empty:
        return "Hotspot language needs reliable geography; several ZIPs could not be placed on the map."
    tbl = tbl[tbl["tests"] >= 8]
    if tbl.empty:
        return "Counties have too few ZIP-linked tests in this slice to responsibly call a “hotspot.”"
    lead = tbl.sort_values("elevated_rate", ascending=False).iloc[0]
    return (
        f"Using ZIP-linked county labels, **{lead['county_from_zip']}** has the highest share of tests in the **at/above reference** band "
        f"among counties with at least eight tests (**{lead['elevated_rate']*100:.1f}%**). "
        "Call this a **priority geography for follow-up education**, not proof that every household there is exposed."
    )


def surveillance_gap_story(mosquito: pd.DataFrame) -> str:
    missing = int(mosquito["missing_taxon"].sum())
    total = len(mosquito)
    share = 100.0 * missing / total if total else 0.0
    return (
        f"About **{share:.1f}%** of mosquito rows are missing genus/species together. "
        "Those rows are still useful for **trap effort and site maps**, but they will **undercount species-specific narratives**. "
        "Template discipline (fill “ND” vs leaving blank) matters for year-to-year comparisons."
    )


def temporal_change_story(arsenic: pd.DataFrame) -> str:
    years = sorted(arsenic["year"].dropna().unique().tolist())
    if len(years) < 2:
        return "This arsenic extract spans limited years; trend language should stay cautious."
    early = arsenic[arsenic["year"] <= years[len(years) // 2]]
    late = arsenic[arsenic["year"] > years[len(years) // 2]]
    e_early = elevated_rate(early)
    e_late = elevated_rate(late)
    direction = "higher" if e_late > e_early + 1 else "lower" if e_late + 1 < e_early else "similar"
    return (
        f"Splitting years at the midpoint, the **at/above reference** share is **{direction}** in the later period "
        f"({e_late:.1f}% vs {e_early:.1f}%). "
        "That is a **descriptive split**, not a causal finding—well depth, geology, and sampling rules all matter."
    )


def overlap_teaser(arsenic: pd.DataFrame, mosquito: pd.DataFrame) -> str:
    cities_a = set(arsenic["city"].str.lower())
    cities_m = set(mosquito["city"].str.lower())
    overlap = sorted(cities_a & cities_m)
    if not overlap:
        return "City names do not overlap cleanly between files yet—combined mapping will improve when both datasets share the same place keys."
    preview = ", ".join(overlap[:4])
    return (
        f"Both datasets mention communities such as **{preview}**. "
        "That overlap is a starting point for **joint storytelling** (where environmental testing and vector surveillance both occur), "
        "not evidence of shared biological mechanisms."
    )
