"""Shared Streamlit look-and-feel (CSS + theme toggle + Plotly template)."""

from __future__ import annotations

import streamlit as st

from streamlit_app.light_palette import SAND, SLATE, SLATE_MUTED, TAN, WARM

__all__ = [
    "apply_dashboard_style",
    "apply_plotly_theme",
    "ensure_theme_applied",
    "get_theme",
    "is_light_theme",
    "plotly_template_name",
    "render_theme_selector",
]

THEME_KEY = "eh_theme"
# Light-only CSS is injected only in light mode (no attribute scoping needed).
_LIGHT = ""

# Plain string (not an f-string) so CSS braces are not interpreted by Python.
_LAYOUT_CSS = """
  [data-testid="stAppViewContainer"],
  [data-testid="stSidebar"],
  [data-testid="stHeader"] {
    font-family: 'Outfit', ui-sans-serif, system-ui, sans-serif;
  }
  [data-testid="stAppViewContainer"] {
    background: var(--eh-bg-radial-1), var(--eh-bg-radial-2), var(--eh-bg-grad-1) !important;
    color: var(--eh-body-text);
  }
  [data-testid="stHeader"] {
    background: var(--eh-header-bg) !important;
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--eh-header-border);
  }
  [data-testid="stSidebar"] {
    background: var(--eh-sidebar-bg) !important;
    border-right: 1px solid var(--eh-sidebar-border);
  }
  [data-testid="stSidebar"] .stMarkdown h1,
  [data-testid="stSidebar"] .stMarkdown h2 {
    font-weight: 600;
    letter-spacing: -0.02em;
    color: var(--eh-subheading) !important;
  }
  [data-testid="stMainBlockContainer"],
  section.main .block-container {
    color: var(--eh-body-text);
    background-color: transparent;
  }
  [data-testid="stMainBlockContainer"] .stMarkdown p,
  [data-testid="stMainBlockContainer"] .stMarkdown li {
    color: var(--eh-body-text);
  }
  [data-testid="stMetricValue"] {
    font-weight: 700 !important;
    font-size: 1.65rem !important;
    color: var(--eh-accent) !important;
  }
  [data-testid="stMetricLabel"] {
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    opacity: 0.85;
    color: var(--eh-caption) !important;
  }
  .stExpander {
    border: 1px solid var(--eh-expander-border) !important;
    border-radius: 12px !important;
    background: var(--eh-expander-bg) !important;
    overflow: hidden;
  }
  div[data-testid="stExpanderDetails"] > div {
    border-top: 1px solid var(--eh-expander-border);
  }
  h1 {
    font-weight: 700 !important;
    letter-spacing: -0.04em !important;
    line-height: 1.15 !important;
    color: var(--eh-heading) !important;
    text-shadow: var(--eh-heading-glow);
  }
  h2, h3 {
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
    color: var(--eh-subheading) !important;
  }
  .stCaption, [data-testid="stCaption"] {
    color: var(--eh-caption) !important;
    font-size: 1rem !important;
  }
  hr {
    border: none;
    height: 1px;
    background: var(--eh-hr);
    margin: 1.5rem 0;
  }
  [data-testid="stDecoration"] { display: none; }
  div[data-testid="stAlert"] {
    background: var(--eh-alert-bg) !important;
    border: 1px solid var(--eh-alert-border) !important;
    border-radius: 12px !important;
    box-shadow: var(--eh-alert-shadow);
    color: var(--eh-body-text) !important;
  }
"""

# Streamlit config.toml uses base="dark" + teal primary; override for light palette.
_CSS_LIGHT_WIDGETS = f"""
  {_LIGHT}.stApp {{
    --primary-color: {SLATE} !important;
    --border-color: {SLATE} !important;
  }}
  {_LIGHT}section[data-testid="stSidebar"] {{
    --text-color: {SLATE} !important;
    --secondary-text-color: {SLATE_MUTED} !important;
    --primary-color: {SLATE} !important;
    color: {SLATE} !important;
  }}
  {_LIGHT}section[data-testid="stSidebar"] [data-testid="stMarkdown"] p,
  {_LIGHT}section[data-testid="stSidebar"] [data-testid="stMarkdown"] li,
  {_LIGHT}section[data-testid="stSidebar"] label,
  {_LIGHT}section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
  {_LIGHT}section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a,
  {_LIGHT}section[data-testid="stSidebar"] [data-testid="stSidebarNav"] span,
  {_LIGHT}section[data-testid="stSidebar"] [data-testid="stSidebarNav"] p {{
    color: {SLATE} !important;
  }}
  {_LIGHT}section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {{
    background-color: {TAN} !important;
    color: {SLATE} !important;
  }}
  /* Appearance: Dark / Light radio labels */
  {_LIGHT}section[data-testid="stSidebar"] [data-testid="stRadio"],
  {_LIGHT}section[data-testid="stSidebar"] [data-testid="stRadio"] label,
  {_LIGHT}section[data-testid="stSidebar"] [data-testid="stRadio"] label span,
  {_LIGHT}section[data-testid="stSidebar"] [data-testid="stRadio"] label p,
  {_LIGHT}section[data-testid="stSidebar"] [data-testid="stRadio"] label div,
  {_LIGHT}section[data-testid="stSidebar"] .stRadio label,
  {_LIGHT}section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label,
  {_LIGHT}section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label span,
  {_LIGHT}section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p,
  {_LIGHT}section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label div {{
    color: {SLATE} !important;
    -webkit-text-fill-color: {SLATE} !important;
  }}
  {_LIGHT}section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {{
    background-color: {TAN} !important;
    border-radius: 8px;
  }}
  {_LIGHT}[data-testid="stMainBlockContainer"] {{
    --primary-color: {SLATE} !important;
    background-color: {SAND} !important;
  }}
  {_LIGHT}[data-testid="stMainBlockContainer"] label,
  {_LIGHT}[data-testid="stMainBlockContainer"] [data-testid="stWidgetLabel"] p,
  {_LIGHT}[data-testid="stMainBlockContainer"] .stCheckbox label,
  {_LIGHT}[data-testid="stMainBlockContainer"] .stToggle label,
  {_LIGHT}[data-testid="stMainBlockContainer"] [data-testid="stMarkdown"] p,
  {_LIGHT}[data-testid="stMainBlockContainer"] [data-testid="stMarkdown"] li,
  {_LIGHT}[data-testid="stMainBlockContainer"] [data-testid="stMarkdown"] span,
  {_LIGHT}[data-testid="stMainBlockContainer"] [data-testid="stMarkdown"] strong {{
    color: {SLATE} !important;
  }}
  /* Filter inputs (years, cities, severity, species, etc.) */
  {_LIGHT}[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
  {_LIGHT}[data-testid="stSelectbox"] [data-baseweb="select"] > div,
  {_LIGHT}div[data-baseweb="select"] > div,
  {_LIGHT}div[data-baseweb="input"] > div,
  {_LIGHT}input[data-baseweb="input"] {{
    background-color: {WARM} !important;
    color: {SLATE} !important;
    border-color: {TAN} !important;
  }}
  {_LIGHT}[data-testid="stMultiSelect"] [data-baseweb="input"],
  {_LIGHT}[data-testid="stSelectbox"] [data-baseweb="input"] {{
    color: {SLATE} !important;
  }}
  /* Multiselect chips (e.g. each year tag) — replace default teal */
  {_LIGHT}.stApp [data-baseweb="tag"],
  {_LIGHT}.stApp span[data-baseweb="tag"],
  {_LIGHT}.stApp div[data-baseweb="tag"],
  {_LIGHT}[data-testid="stMultiSelect"] [data-baseweb="tag"],
  {_LIGHT}[data-testid="stMultiSelect"] span[data-baseweb="tag"] {{
    background-color: {TAN} !important;
    background: {TAN} !important;
    color: {SLATE} !important;
    border: 1px solid rgba(89, 110, 121, 0.35) !important;
  }}
  {_LIGHT}.stApp [data-baseweb="tag"] span,
  {_LIGHT}.stApp [data-baseweb="tag"] div,
  {_LIGHT}[data-testid="stMultiSelect"] [data-baseweb="tag"] span {{
    color: {SLATE} !important;
  }}
  {_LIGHT}.stApp [data-baseweb="tag"] svg,
  {_LIGHT}.stApp [data-baseweb="tag"] svg path,
  {_LIGHT}[data-testid="stMultiSelect"] [data-baseweb="tag"] svg,
  {_LIGHT}[data-testid="stMultiSelect"] [data-baseweb="tag"] svg path {{
    fill: {SLATE} !important;
    color: {SLATE} !important;
  }}
  {_LIGHT}[data-testid="stSlider"] label {{
    color: {SLATE} !important;
  }}
  /* Download section + action buttons */
  {_LIGHT}[data-testid="stMainBlockContainer"] [data-testid="stDownloadButton"] button,
  {_LIGHT}[data-testid="stMainBlockContainer"] .stButton > button {{
    background-color: {WARM} !important;
    color: {SLATE} !important;
    border: 1px solid {TAN} !important;
  }}
  {_LIGHT}[data-testid="stMainBlockContainer"] [data-testid="stDownloadButton"] button:hover,
  {_LIGHT}[data-testid="stMainBlockContainer"] .stButton > button:hover {{
    background-color: {TAN} !important;
    border-color: {SLATE} !important;
    color: {SLATE} !important;
  }}
  {_LIGHT}[data-testid="stMainBlockContainer"] .stButton > button[kind="primary"],
  {_LIGHT}[data-testid="stMainBlockContainer"] [data-testid="stBaseButton-primary"] button {{
    background-color: {SLATE} !important;
    color: {SAND} !important;
    border-color: {SLATE} !important;
  }}
  {_LIGHT}[data-testid="stMainBlockContainer"] .stButton > button[kind="primary"]:hover,
  {_LIGHT}[data-testid="stMainBlockContainer"] [data-testid="stBaseButton-primary"] button:hover {{
    background-color: {SLATE_MUTED} !important;
    color: {SAND} !important;
  }}
  {_LIGHT}[data-testid="stMainBlockContainer"] div[data-testid="stExpander"] summary,
  {_LIGHT}[data-testid="stMainBlockContainer"] div[data-testid="stExpander"] summary p,
  {_LIGHT}[data-testid="stMainBlockContainer"] div[data-testid="stExpander"] summary span {{
    color: {SLATE} !important;
  }}
  /* Bordered cards: st.container(border=True) in Streamlit 1.57 */
  {_LIGHT}[data-testid="stLayoutWrapper"] > div {{
    border: 2px solid {SLATE} !important;
    border-radius: 0.5rem !important;
    background-color: {WARM} !important;
    box-shadow: 0 2px 10px rgba(89, 110, 121, 0.14) !important;
  }}
  /* Horizontal dividers (st.divider) — light only */
  {_LIGHT}[data-testid="stDivider"],
  {_LIGHT}[data-testid="stDivider"] hr,
  {_LIGHT}.stDivider hr {{
    border: none !important;
    height: 2px !important;
    min-height: 2px !important;
    background: {SLATE} !important;
    opacity: 1 !important;
    margin: 1.25rem 0 !important;
  }}
  {_LIGHT}[data-testid="stMainBlockContainer"] hr {{
    border: none !important;
    height: 2px !important;
    background: {SLATE} !important;
    opacity: 1 !important;
  }}
  {_LIGHT}[data-testid="stAppViewContainer"] .stPlotlyChart {{
    background: transparent !important;
  }}
"""

_CSS_LIGHT_VARS = f"""
  :root {{
    --background-color: {SAND};
    --secondary-background-color: {WARM};
    --text-color: {SLATE};
    --primary-color: {SLATE};
    --border-color: {SLATE};
    --eh-accent: {SLATE};
    --eh-accent-dim: {SLATE_MUTED};
    --eh-surface: {WARM};
    --eh-body-text: {SLATE};
    --eh-bg-grad-1: linear-gradient(180deg, {SAND} 0%, {WARM} 100%);
    --eh-bg-radial-1: radial-gradient(1200px 600px at 10% -10%, rgba(199,177,152,0.35), transparent 55%);
    --eh-bg-radial-2: radial-gradient(900px 500px at 100% 0%, rgba(240,236,226,0.95), transparent 50%);
    --eh-header-bg: rgba(240, 236, 226, 0.92);
    --eh-header-border: {TAN};
    --eh-sidebar-bg: linear-gradient(180deg, {WARM} 0%, {SAND} 100%);
    --eh-sidebar-border: {TAN};
    --eh-heading: {SLATE};
    --eh-heading-glow: none;
    --eh-subheading: {SLATE};
    --eh-caption: {SLATE_MUTED};
    --eh-expander-bg: {WARM};
    --eh-expander-border: {TAN};
    --eh-alert-bg: {WARM};
    --eh-alert-border: {TAN};
    --eh-alert-shadow: 0 8px 24px rgba(89, 110, 121, 0.12);
    --eh-hr: linear-gradient(90deg, transparent, {TAN}, transparent);
  }}
  .stApp,
  [data-testid="stAppViewContainer"],
  section.main {{
    background-color: {SAND} !important;
    color: {SLATE} !important;
  }}
  [data-testid="stHeader"] {{
    background-color: {SAND} !important;
  }}
"""

_CSS_DARK_VARS = """
  :root {
    --eh-accent: #2dd4bf;
    --eh-accent-dim: #14b8a6;
    --eh-surface: #151f32;
    --eh-body-text: #e8eef7;
    --eh-bg-grad-1: linear-gradient(180deg, #0b1220 0%, #0a0f18 100%);
    --eh-bg-radial-1: radial-gradient(1200px 600px at 10% -10%, rgba(45,212,191,0.08), transparent 55%);
    --eh-bg-radial-2: radial-gradient(900px 500px at 100% 0%, rgba(56,189,248,0.06), transparent 50%);
    --eh-header-bg: rgba(11, 18, 32, 0.85);
    --eh-header-border: rgba(148, 163, 184, 0.12);
    --eh-sidebar-bg: linear-gradient(180deg, #121b2e 0%, #0f1729 100%);
    --eh-sidebar-border: rgba(148, 163, 184, 0.1);
    --eh-heading: #f0fdfa;
    --eh-heading-glow: 0 0 42px rgba(45, 212, 191, 0.22);
    --eh-subheading: #f1f5f9;
    --eh-caption: #94a3b8;
    --eh-expander-bg: rgba(21, 31, 50, 0.65);
    --eh-expander-border: rgba(148, 163, 184, 0.15);
    --eh-alert-bg: rgba(21, 31, 50, 0.85);
    --eh-alert-border: rgba(45, 212, 191, 0.28);
    --eh-alert-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
    --eh-hr: linear-gradient(90deg, transparent, rgba(45,212,191,0.35), transparent);
  }
"""


def get_theme() -> str:
    theme = st.session_state.get(THEME_KEY, "dark")
    return "light" if theme == "light" else "dark"


def is_light_theme() -> bool:
    return get_theme() == "light"


def plotly_template_name() -> str:
    return "plotly_white" if is_light_theme() else "plotly_dark"


def apply_plotly_theme() -> None:
    """Sync Plotly default template with the active dashboard theme."""
    from src.visualization.plotly_theme import sync_template_from_session

    sync_template_from_session()


def render_theme_selector() -> None:
    with st.sidebar:
        st.markdown("##### Appearance")
        previous = st.session_state.get(THEME_KEY, "dark")
        choice = st.radio(
            "Theme",
            options=["Dark", "Light"],
            index=1 if previous == "light" else 0,
            horizontal=True,
            key="eh_theme_radio",
            label_visibility="collapsed",
        )
        st.session_state[THEME_KEY] = choice.lower()
        if st.session_state[THEME_KEY] != previous:
            st.rerun()


def _dashboard_css_bundle() -> str:
    """Concatenate theme + layout rules (plain join — no outer f-string on layout CSS)."""
    theme_vars = _CSS_LIGHT_VARS if is_light_theme() else _CSS_DARK_VARS
    widget_css = _CSS_LIGHT_WIDGETS if is_light_theme() else ""
    return theme_vars + widget_css + _LAYOUT_CSS


def _inject_global_css(css: str) -> None:
    """Inject CSS into the main app (works on Streamlit Cloud; no JavaScript required)."""
    st.markdown(
        '<style id="eh-dashboard-theme">' + css + "</style>",
        unsafe_allow_html=True,
    )


def apply_dashboard_style() -> None:
    """Inject typography and theme-aware surfaces once per rerun."""
    st.markdown(
        "<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">"
        "<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>"
        "<link href=\"https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap\" rel=\"stylesheet\">",
        unsafe_allow_html=True,
    )
    _inject_global_css(_dashboard_css_bundle())
    apply_plotly_theme()


def ensure_theme_applied() -> None:
    """Call from pages: set Plotly template (styles are injected from app.py only)."""
    apply_plotly_theme()
