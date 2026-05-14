"""
Environmental Health Intelligence Dashboard — home page.

Run from the repository root:

./scripts/run_dashboard.sh

Or: ``export PYTHONPATH="$(pwd)" && streamlit run app.py``
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from streamlit_app.ui_style import apply_dashboard_style


def main() -> None:
    st.set_page_config(
        page_title="Environmental Health Intelligence",
        page_icon="🧭",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_dashboard_style()

    top, nav = st.columns([1.15, 1], vertical_alignment="top")
    with top:
        st.title("Environmental Health Intelligence")
        st.caption("Maps, filters, and plain-language context for arsenic testing and mosquito surveillance.")
    with nav:
        st.markdown("**Open a workspace**")
        a, b = st.columns(2)
        with a:
            st.page_link("pages/02_Arsenic_Explorer.py", label="Arsenic Explorer", icon="💧", use_container_width=True)
            st.page_link("pages/04_Environmental_Insights.py", label="Environmental Insights", icon="✨", use_container_width=True)
        with b:
            st.page_link("pages/03_Mosquito_Surveillance.py", label="Mosquito Surveillance", icon="🦟", use_container_width=True)
            st.page_link("pages/05_Methods_and_Limitations.py", label="Methods & limitations", icon="📋", use_container_width=True)

    st.divider()

    with st.container(border=True):
        st.markdown(
            """
            ### Purpose
            This workspace helps a **non-technical researcher** explore two complementary datasets:
            private well arsenic tests and public-health mosquito surveillance. The goal is not “more charts,”
            but **clear geography**, **simple filters**, and **short explanations** that stay close to the data.
            """
        )

    c1, c2 = st.columns(2, gap="large")
    with c1:
        with st.container(border=True):
            st.markdown("#### What is inside")
            st.markdown(
                """
                - **Arsenic Explorer:** distributions, yearly testing activity, filters, and an interactive map.
                - **Mosquito Surveillance:** species mix, seasonality, detection outcomes, and a city-level map.
                """
            )
    with c2:
        with st.container(border=True):
            st.markdown("#### How to use this dashboard")
            st.markdown(
                """
                1. Pick **Arsenic** or **Mosquito** from the cards above or the **sidebar**.
                2. Use **filters** to narrow time and place.
                3. Expand **“How to interpret this”** before sharing a chart externally.
                """
            )

    st.divider()
    st.info(
        "The **home page** is an overview only. **Maps and charts** are on **Arsenic Explorer** and **Mosquito Surveillance**. "
        "If a map is blank there, confirm `data/geo/mi_counties_tiger2025.geojson` or `data/geo/mi_counties.geojson` exists."
    )


# Streamlit executes this file as a script; do not rely on ``__name__ == "__main__"``.
main()
