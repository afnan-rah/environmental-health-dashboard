"""
Environmental Health Intelligence Dashboard — main Streamlit entrypoint.
"""

from __future__ import annotations

import streamlit as st


def main() -> None:
    st.set_page_config(
        page_title="Environmental Health Intelligence",
        page_icon="🧭",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("Environmental Health Intelligence Dashboard")
    st.caption(
        "Explore environmental test and surveillance data with maps, filters, "
        "and readable summaries—designed for researchers who are not software engineers."
    )

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Arsenic testing")
        st.info(
            "Coming next: location explorer, hotspot views, year / city / ZIP filters, "
            "trend charts, and severity framing in plain language."
        )
    with col2:
        st.subheader("Mosquito surveillance")
        st.info(
            "Coming next: trap and collection sites, species and count summaries, "
            "detection trends, and seasonal comparisons."
        )

    st.divider()
    st.subheader("Workflow")
    st.markdown(
        """
        1. **Raw data** live in `data/raw/` (Excel and similar).
        2. **Cleaning** scripts in `src/cleaning/` produce standardized tables in `data/processed/`.
        3. **Analysis** in `src/analysis/` and notebooks supports QA and methods.
        4. **This app** surfaces the results with strong mapping and short explanations.
        """
    )


if __name__ == "__main__":
    main()
