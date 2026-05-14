from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.analysis import arsenic_patterns as ap
from src.analysis import insights_narrative as ins
from streamlit_app.cached_loaders import get_arsenic, get_arsenic_enriched, get_mosquito
from streamlit_app.ui_style import apply_dashboard_style

apply_dashboard_style()


st.title("Environmental Insights")
st.caption("Research-oriented synthesis — written to be honest about what the spreadsheets can and cannot show.")

with st.expander("How to interpret this page", expanded=False):
    st.markdown(
        """
        These blurbs are **descriptive** summaries of the current files. They are **not** causal explanations and they are **not** regulatory determinations.
        When language sounds strong, read **Methods & Limitations** next.
        """
    )

arsenic = get_arsenic()
mosquito = get_mosquito()
arsenic_geo = get_arsenic_enriched()

with st.container(border=True):
    st.subheader("Testing patterns")
    st.markdown(ins.testing_activity_story(arsenic))

with st.container(border=True):
    st.subheader("Hotspot-style geography (ZIP-linked counties)")
    st.markdown(ins.hotspot_story(arsenic_geo))

with st.container(border=True):
    st.subheader("Temporal change (simple split)")
    st.markdown(ins.temporal_change_story(arsenic))

with st.container(border=True):
    st.subheader("Surveillance gaps (mosquito taxonomy)")
    st.markdown(ins.surveillance_gap_story(mosquito))

with st.container(border=True):
    st.subheader("Where the two datasets overlap in place names")
    st.markdown(ins.overlap_teaser(arsenic, mosquito))

st.divider()
st.info(
    f"Snapshot metrics for transparency: **{len(arsenic):,}** arsenic rows after cleaning; "
    f"**{ap.elevated_rate(arsenic):.1f}%** at/above the reference band overall; **{len(mosquito):,}** mosquito rows after cleaning."
)
