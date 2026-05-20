"""Home workspace content (used as a callable page via ``st.Page`` in ``app.py``)."""

from __future__ import annotations

import streamlit as st


def render_home() -> None:
    top, nav = st.columns([1.15, 1], vertical_alignment="top")
    with top:
        st.title("Environmental Health Intelligence")
        st.caption("Maps, filters, and plain-language context for arsenic testing and mosquito surveillance.")
    with nav:
        st.markdown("**Open a workspace**")
        a, b = st.columns(2)
        with a:
            if st.button("💧 Arsenic Explorer", use_container_width=True, key="nav_arsenic"):
                st.switch_page("pages/02_Arsenic_Explorer.py")
            if st.button("✨ Environmental Insights", use_container_width=True, key="nav_insights"):
                st.switch_page("pages/04_Environmental_Insights.py")
        with b:
            if st.button("🦟 Mosquito Surveillance", use_container_width=True, key="nav_mosquito"):
                st.switch_page("pages/03_Mosquito_Surveillance.py")
            if st.button("📋 Methods & limitations", use_container_width=True, key="nav_methods"):
                st.switch_page("pages/05_Methods_and_Limitations.py")

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
