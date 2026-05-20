"""Streamlit UI package for the environmental health dashboard."""

from streamlit_app.ui_style import (
    apply_dashboard_style,
    apply_plotly_theme,
    ensure_theme_applied,
    render_theme_selector,
)

__all__ = [
    "apply_dashboard_style",
    "apply_plotly_theme",
    "ensure_theme_applied",
    "render_theme_selector",
]
