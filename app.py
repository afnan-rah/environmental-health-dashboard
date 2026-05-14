"""
Environmental Health Intelligence Dashboard — home page.

Run from the repository root:

PYTHONPATH=. streamlit run app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st


def main() -> None:
    st.set_page_config(
        page_title="Environmental Health Intelligence",
        page_icon="🧭",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("Environmental Health Intelligence Dashboard")
    st.caption("Plain-language maps and charts for arsenic testing and mosquito surveillance.")

    st.markdown(
        """
        ### Purpose
        This workspace helps a **non-technical researcher** explore two complementary datasets:
        private well arsenic tests and public-health mosquito surveillance. The goal is not “more charts,”
        but **clear geography**, **simple filters**, and **short explanations** that stay close to the data.

        ### What is inside
        - **Arsenic Explorer:** distributions, yearly testing activity, filters, and an interactive map.
        - **Mosquito Surveillance:** species mix, seasonality, detection outcomes, and a city-level map.
        - **Environmental Insights:** cautious, plain-English takeaways that connect the two views.
        - **Methods & Limitations:** where the numbers come from—and what they cannot prove.

        ### How to use this dashboard
        1. Start with **Arsenic** or **Mosquito** depending on your question.
        2. Use the **filters** to narrow time and place—broad views hide important local detail.
        3. Read the **“How to interpret this”** boxes before sharing a chart externally.

        **Tip:** Use the sidebar pages on the left to navigate.
        """
    )

    st.divider()
    st.info(
        "If maps look empty, confirm you ran the app from the repository root and that `data/geo/mi_counties.geojson` exists."
    )


if __name__ == "__main__":
    main()
