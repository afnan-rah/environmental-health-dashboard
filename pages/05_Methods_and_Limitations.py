from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from streamlit_app.cached_loaders import get_arsenic, get_mosquito
from streamlit_app.ui_style import apply_dashboard_style

apply_dashboard_style()


st.title("Methods & Limitations")
st.caption("Credibility lives here: what we did, what we assumed, and what we did not do.")

arsenic = get_arsenic()
mosquito = get_mosquito()

st.markdown(
    """
    ### Data sources
    - **Arsenic:** cleaned export in `data/processed/arsenic_cleaned.csv` produced from the original Excel mapping file.
    - **Mosquito:** cleaned Kent surveillance extract in `data/processed/mosquito_cleaned.csv`.

    ### Cleaning (high level)
    - Column names standardized, dates parsed, duplicates removed, and a small set of derived fields created (for example severity labels and mosquito season).
    - Missing `Result_Cat` values in the arsenic sheet were filled using **mg/L bands inferred from labeled rows** in the same file. **Your program should confirm those thresholds** before any external compliance language.

    ### Geography
    - **Arsenic map points** use **ZIP-code centroids** from an offline postal reference (`pgeocode` generated `mi_zip_reference.csv`). That is appropriate for **exploration**, not for parcel-level decisions.
    - **County outlines** prefer a local **Census TIGER/Line** extract (`mi_counties_tiger2025.geojson` or `mi_counties_tiger2024.geojson`) when you build it from `tl_*_us_county` under `data/raw/`; otherwise the app falls back to `data/geo/mi_counties.geojson`.
    - **Mosquito map points** use **city centroids** (geocoded once, stored as `kent_area_city_centroids.csv`) plus a deterministic jitter so markers do not stack.

    ### What we did **not** do
    - No full street geocoding pipeline (optional future work).
    - No statistical modeling of exposure or risk.
    - No adjustment for uneven sampling across cities, trap types, or seasons.

    ### Observational limitations
    - These datasets are **administrative records** of testing and surveillance. They can miss **who drinks the water**, **which traps failed**, and **what was not sampled**.
    - **Correlation is not causation.** A map highlight is a reason to ask better questions—not proof of harm by itself.
    """
)

st.subheader("Missingness snapshot (current files)")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**Arsenic — percent of rows missing**")
    a_miss = (arsenic[["zip5", "result_mgl", "contamination_severity"]].isna().mean() * 100).round(1)
    st.dataframe(a_miss.rename("missing_%").to_frame(), width="stretch")
with c2:
    st.markdown("**Mosquito — percent of rows missing**")
    m_miss = (
        mosquito[["species_binomial", "detected_normalized", "trap_set_date", "collection_site_type"]]
        .isna()
        .mean()
        * 100
    ).round(1)
    st.dataframe(m_miss.rename("missing_%").to_frame(), width="stretch")

st.info(
    "If you need reproducible downloads for Census TIGER/Line shapefiles, use official U.S. Census endpoints in your environment; "
    "this repository ships a lightweight Michigan county GeoJSON for mapping overlays."
)
