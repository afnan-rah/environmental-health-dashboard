from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from streamlit_app.cached_loaders import get_arsenic, get_mosquito
from streamlit_app.ui_style import ensure_theme_applied

ensure_theme_applied()

st.markdown(
    """
<style>
section[data-testid="stTabs"] > div:first-child button {
  letter-spacing: 0.02em;
}
</style>
    """,
    unsafe_allow_html=True,
)

st.title("Methods & Limitations")
st.caption(
    "Pipeline documentation: how raw files become maps and charts—and what this dashboard does not claim."
)

arsenic = get_arsenic()
mosquito = get_mosquito()

# --- KPI strip ---------------------------------------------------------------
with st.container(border=True):
    st.markdown("##### Snapshot")
    k1, k2, k3 = st.columns(3)
    k1.metric("Arsenic records (cleaned)", f"{len(arsenic):,}")
    k2.metric("Mosquito records (cleaned)", f"{len(mosquito):,}")
    k3.metric(
        "Processed tables",
        "2",
        help="arsenic_cleaned.csv · mosquito_cleaned.csv",
    )

st.divider()

# --- Tabbed body ---------------------------------------------------------------
tab_overview, tab_as, tab_ms, tab_limits, tab_quality = st.tabs(
    ["Overview", "Arsenic", "Mosquito", "Limitations", "Data quality"]
)

with tab_overview:
    with st.container(border=True):
        st.markdown("##### Reproducibility")
        st.markdown(
            """
            | Layer | Location |
            |:------|:---------|
            | Arsenic cleaning | `src/cleaning/clean_arsenic.py` |
            | Mosquito cleaning | `src/cleaning/clean_mosquito.py` |
            | Geo enrichment | `src/analysis/geo_enrichment.py` |
            | Plotly analytics | `src/analysis/arsenic_patterns.py`, `mosquito_patterns.py` |
            | Folium maps | `src/visualization/folium_maps.py` |
            | Cached loaders | `streamlit_app/cached_loaders.py` (`@st.cache_data`) |
            """
        )
    st.markdown("")
    with st.container(border=True):
        st.markdown("##### Outputs")
        st.markdown(
            """
            - **`data/processed/arsenic_cleaned.csv`** — written by the arsenic cleaning entrypoint; not hand-edited in normal workflows.
            - **`data/processed/mosquito_cleaned.csv`** — same for the mosquito pipeline.
            - **Enrichment** (ZIP centroids, county FIPS, city centroids + jitter) happens at load time in the dashboard, not persisted as separate CSVs in this flow.
            """
        )

with tab_as:
    st.markdown("Private-well arsenic: Excel → pandas → CSV → ZIP/county joins → Plotly & Folium.")
    with st.expander("Raw file, columns, dates & ZIP", expanded=False):
        st.markdown(
            r"""
            **Raw**

            - `ARSENIC_RAW_XLSX` → `data/raw/ALL_ArsenicTests_Mapping_071524.xlsx`, sheet **`Sheet1`**, `pandas.read_excel`.

            **Strict rename**

            - Requires: `Year`, `Street`, `City`, `State`, `Zip`, `Test`, `Result`, `Result_Cat`, `Full_Add`, `Prop_Add` → snake_case (`test_date`, `zip_raw`, `result_mgl`, `result_category_code_raw`, …). Missing columns → `ValueError`.

            **Dates**

            - `test_date` = `pd.to_datetime(..., errors="coerce")`; `year`, `month` from timestamp.

            **`zip5`**

            - Numeric ZIP → `float`→`int`→`f"{n:05d}"`; strings → digits only. Must be length **5** or null.

            **`result_mgl`**

            - `pd.to_numeric` on `Result` (**mg/L**, total As in this project).

            **`Result_Cat`**

            - `result_category_code_raw` numeric; `result_category_code` = raw where present else `infer_result_category_code(result_mgl)`:
                - missing → `None` · `≤0` → **0** · `(0, 0.005)` → **1** · `[0.005, 0.01)` → **2** · `≥0.01` → **3**
            - `result_category_inferred` = raw missing & code present.
            - **Confirm cutpoints with the data owner** before compliance language.

            **`contamination_severity`**

            - `0`→`non_detect` · `1`→`detect_low_below_half_mcl_band` · `2`→`detect_moderate_below_mcl` · `3`→`at_or_above_mcl_reference` · else `unknown`.

            **Dedupe / sort**

            - `drop_duplicates()` default row equality; sort `test_date`, `city`, `full_address`; INFO logs for row counts & missingness.
            """
        )
    with st.expander("Geographic enrichment (`enrich_arsenic_for_maps`)", expanded=False):
        st.markdown(
            """
            - **`mi_zip_reference.csv`** — `zip5` as string; **left** merge adds centroid lat/lon → `map_latitude` / `map_longitude`, and `county_name` → `county_from_zip`.
            - **County FIPS** — `resolve_mi_counties_geojson()` prefers `mi_counties_tiger2025.geojson`, then 2024, then `mi_counties.geojson`. Lookup: lowercased GeoJSON `NAME` → feature `id` or `GEOID`.
            - **Caveat** — Points are **ZIP centroids**, not wellheads; ZIP→county can mis-assign border / multi-county ZIPs.
            """
        )
    with st.expander("Explorer: filters, metrics & Plotly", expanded=False):
        st.markdown(
            r"""
            - **Filters** — multiselect `year`, optional `city`, multiselect `contamination_severity`.
            - **`elevated_rate`** — % rows with `contamination_severity == "at_or_above_mcl_reference"`.
            - **Histogram** — `px.histogram`, `x=result_mgl`, `nbins=40`, `plotly_dark`, `bargap=0.05`; vline **0.01 mg/L** (note: `result_display_mgl` 99th-pct clip exists in code but is **not** the histogram axis).
            - **Tests / year** — `groupby("year").size()`.
            - **Top cities** — `groupby("city").size()`, head **10**.
            - **County elevated bar** — drop null `county_from_zip`; `elevated` boolean; `groupby` → `tests`, `elevated_share`; top **12** by tests sort.
            """
        )
    with st.expander("Folium map (`build_arsenic_folium_map`)", expanded=False):
        st.markdown(
            r"""
            - **Basemap** — CartoDB `dark_matter` (default).
            - **Choropleth** — Only if `show_county_choropleth`, `county_fips` present, and after `groupby("county_fips")` the gate **`agg["tests"].max() >= 5`** passes. `elevated_rate` = mean(`severity == at_or_above_mcl_reference`). Bins from Folium/`numpy.histogram` on values.
            - **Legend** — `color_scale.text_color = #e8eef4` on dark basemap.
            - **Markers** — `CircleMarker` r=6, `SEVERITY_COLORS`; optional `MarkerCluster`.
            - **HeatMap** — `[lat, lon, result_mgl or 0]`, `radius=18`, `blur=22`, `min_opacity=0.25`.
            """
        )

with tab_ms:
    st.markdown("Kent-area surveillance: Excel → pandas → CSV → city centroids + jitter → Plotly & Folium.")
    with st.expander("Raw file, columns, dates & taxa", expanded=False):
        st.markdown(
            r"""
            **Raw**

            - `MOSQUITO_RAW_XLSX` → `data/raw/mosquitoSurveillanceData_2021_Kent (Final).xlsx`, sheet **`mosquitoSurveillanceData`**.

            **`COLUMN_RENAME`**

            - All keys must exist or `ValueError`. Includes trap dates, site type, genus/species, sex counts, `Detected`→`detected_raw`.

            **Dates**

            - `trap_set_date`, `trap_pickup_date` → `pd.to_datetime(..., errors="coerce")`; `trap_set_year`, `trap_set_month` from set date.

            **`season`**

            - Dec–Feb `winter` · Mar–May `spring` · Jun–Aug `summer` · Sep–Nov `fall`.

            **Text**

            - `_clean_text` strip / drop `"nan"`; city, county, site type → `.title()`; `state` upper.

            **`species_binomial`**

            - Both missing → `None` · genus only → `Genus sp.` · `sp.`/`sp` → `Genus sp.` · else `Genus species`.

            **Counts**

            - Sex columns → numeric, `fillna(0)`, `int`; **`total_adults_collected`** = sum of three columns.

            **`detected_normalized`**

            - `ND` / `N/D` / `NOT DETECTED` → `not_detected` · `POSITIVE` / `POS` → `positive` · else lowercased string.

            **`missing_taxon`** — both genus & species null after clean.

            **Dedupe / sort** — `drop_duplicates`; sort `trap_set_date`, `collection_location_id`.
            """
        )
    with st.expander("Geographic enrichment (`enrich_mosquito_for_maps`)", expanded=False):
        st.markdown(
            r"""
            - **`kent_area_city_centroids.csv`** — **left** merge on `city` → `map_latitude` / `map_longitude`.
            - **Jitter** — MD5 UTF-8 `str(collection_location_id)` (`usedforsecurity=False`), first 8 hex as int \(h\):
                - \(\Delta_{lon} = ((h \bmod 101) - 50) / 8000\)
                - \(\Delta_{lat} = (((h // 101) \bmod 101) - 50) / 8000\)
            - **Not** survey-grade coordinates—visual separation only.
            """
        )
    with st.expander("Explorer: charts & metrics", expanded=False):
        st.markdown(
            r"""
            - **Species** — fill null binomial as `"Unidentified / not recorded"`; top **10**; horizontal bar, `plotly_dark`.
            - **Season** — `groupby("season").size()` with order `spring`…`winter`.
            - **Detection × month** — non-null `trap_set_month`; stacked bars, `barmode="stack"`.
            - **Site type** — (1) counts + sum adults (2) mean adults; x tick **-25°**.
            - **Positive %** — among non-null `detected_normalized`, share `== "positive"` × 100 (else 0%).
            """
        )
    with st.expander("Folium map (`build_mosquito_folium_map`)", expanded=False):
        st.markdown(
            r"""
            - **Markers** — `CircleMarker` r=6; `MOSQUITO_COLORS` for known outcomes; null/other → `#90a4ae`.
            - **Cluster** — `MarkerCluster` on all points.
            - **HeatMap (optional)** — `total_adults_collected` → float, `clip(lower=0.5)`, cap at **95th percentile**, divide by cap → weights in ~[0,1]; `radius=20`, `blur=18`, `min_opacity=0.22`.
            """
        )

with tab_limits:
    with st.container(border=True):
        st.markdown("##### What this dashboard is not")
        st.markdown(
            """
            - **Administrative records only** — no exposure modeling, dose, hydrology, or well-construction covariates.
            - **Descriptive charts** — no p-values, regression, or spatial inference unless you add them later.
            - **Sampling bias** — high counts reflect **activity and reporting**, not unbiased prevalence.
            - **Arsenic categories** — imputed `Result_Cat` is for analytics convenience; validate against lab/program rules externally.
            - **Mosquito ND** — laboratory “not detected” for the target agent in that batch, not proof of zero mosquitoes.
            - **No street geocoding** — arsenic: ZIP centroids; mosquito: city centroid + deterministic jitter.
            """
        )

with tab_quality:
    st.markdown("Missing values in the **processed** CSVs the app reads today.")
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        with st.container(border=True):
            st.markdown("##### Arsenic — missing %")
            a_miss = (arsenic[["zip5", "result_mgl", "contamination_severity"]].isna().mean() * 100).round(1)
            st.dataframe(
                a_miss.rename("missing_%").to_frame(),
                width="stretch",
                column_config={"missing_%": st.column_config.NumberColumn(format="%.1f %%")},
            )
    with c2:
        with st.container(border=True):
            st.markdown("##### Mosquito — missing %")
            m_miss = (
                mosquito[
                    ["species_binomial", "detected_normalized", "trap_set_date", "collection_site_type"]
                ]
                .isna()
                .mean()
                * 100
            ).round(1)
            st.dataframe(
                m_miss.rename("missing_%").to_frame(),
                width="stretch",
                column_config={"missing_%": st.column_config.NumberColumn(format="%.1f %%")},
            )
    st.info(
        "**County outlines:** Prefer Census **TIGER/Line** via `scripts/extract_mi_counties_tiger.py` → `data/geo/mi_counties_tiger*.geojson`. "
        "The app falls back to `data/geo/mi_counties.geojson` when TIGER files are absent."
    )
