"""
Environmental Health Intelligence Dashboard — entrypoint and navigation.

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

from streamlit_app.home_page import render_home
from streamlit_app.ui_style import apply_dashboard_style

st.set_page_config(
    page_title="Environmental Health Intelligence",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_dashboard_style()

pg = st.navigation(
    [
        st.Page(render_home, title="Home", icon="🧭", default=True),
        st.Page("pages/02_Arsenic_Explorer.py", title="Arsenic Explorer", icon="💧"),
        st.Page("pages/03_Mosquito_Surveillance.py", title="Mosquito Surveillance", icon="🦟"),
        st.Page("pages/04_Environmental_Insights.py", title="Environmental Insights", icon="✨"),
        st.Page("pages/05_Methods_and_Limitations.py", title="Methods & limitations", icon="📋"),
    ]
)
pg.run()
