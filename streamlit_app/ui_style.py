"""Shared Streamlit look-and-feel (CSS + small layout helpers)."""

from __future__ import annotations

import streamlit as st


def apply_dashboard_style() -> None:
    """Inject once per run: typography, surfaces, sidebar polish."""
    st.markdown(
        """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --eh-accent: #2dd4bf;
    --eh-accent-dim: #14b8a6;
    --eh-surface: #151f32;
    --eh-glow: rgba(45, 212, 191, 0.12);
  }
  html, body, [data-testid="stAppViewContainer"] * {
    font-family: 'Outfit', ui-sans-serif, system-ui, sans-serif !important;
  }
  [data-testid="stAppViewContainer"] {
    background: radial-gradient(1200px 600px at 10% -10%, rgba(45,212,191,0.08), transparent 55%),
                radial-gradient(900px 500px at 100% 0%, rgba(56,189,248,0.06), transparent 50%),
                linear-gradient(180deg, #0b1220 0%, #0a0f18 100%) !important;
  }
  [data-testid="stHeader"] {
    background: rgba(11, 18, 32, 0.85) !important;
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(148, 163, 184, 0.12);
  }
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #121b2e 0%, #0f1729 100%) !important;
    border-right: 1px solid rgba(148, 163, 184, 0.1);
  }
  [data-testid="stSidebar"] .stMarkdown h1, [data-testid="stSidebar"] .stMarkdown h2 {
    font-weight: 600;
    letter-spacing: -0.02em;
    color: #f1f5f9 !important;
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
  }
  .stExpander {
    border: 1px solid rgba(148, 163, 184, 0.15) !important;
    border-radius: 12px !important;
    background: rgba(21, 31, 50, 0.65) !important;
    overflow: hidden;
  }
  div[data-testid="stExpanderDetails"] > div {
    border-top: 1px solid rgba(148, 163, 184, 0.1);
  }
  h1 {
    font-weight: 700 !important;
    letter-spacing: -0.04em !important;
    line-height: 1.15 !important;
    color: #f0fdfa !important;
    text-shadow: 0 0 42px rgba(45, 212, 191, 0.22);
  }
  h2, h3 {
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
    color: #f1f5f9 !important;
  }
  .stCaption, [data-testid="stCaption"] {
    color: #94a3b8 !important;
    font-size: 1rem !important;
  }
  hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(45,212,191,0.35), transparent);
    margin: 1.5rem 0;
  }
  [data-testid="stDecoration"] { display: none; }
  div[data-testid="stAlert"] {
    background: rgba(21, 31, 50, 0.85) !important;
    border: 1px solid rgba(45, 212, 191, 0.28) !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
  }
</style>
        """,
        unsafe_allow_html=True,
    )
