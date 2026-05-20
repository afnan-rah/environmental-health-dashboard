"""Active Plotly template and figure styling (synced from Streamlit theme toggle)."""

from __future__ import annotations

import plotly.graph_objects as go

from streamlit_app.light_palette import SAND, SLATE, SLATE_MUTED, TAN, WARM

_ACTIVE: str = "plotly_dark"
_THEME_KEY = "eh_theme"


def _theme_from_session() -> str:
    try:
        import streamlit as st

        return st.session_state.get(_THEME_KEY, "dark")
    except Exception:
        return "dark" if _ACTIVE == "plotly_dark" else "light"


def set_template(name: str) -> None:
    global _ACTIVE
    _ACTIVE = name


def get_template() -> str:
    return _ACTIVE


def sync_template_from_session() -> str:
    """Align global template with ``st.session_state['eh_theme']`` before building figures."""
    theme = _theme_from_session()
    tpl = "plotly_white" if theme == "light" else "plotly_dark"
    set_template(tpl)
    try:
        import plotly.io as pio

        pio.templates.default = tpl
    except Exception:
        pass
    return tpl


def is_light() -> bool:
    return sync_template_from_session() == "plotly_white"


def finalize_figure(fig: go.Figure) -> go.Figure:
    """Apply template + explicit backgrounds so charts match dashboard light/dark mode."""
    tpl = sync_template_from_session()
    if tpl == "plotly_white":
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor=WARM,
            plot_bgcolor=SAND,
            font=dict(color=SLATE),
            colorway=[SLATE, TAN, SLATE_MUTED, WARM],
            title=dict(font=dict(color=SLATE, size=16)),
            legend=dict(font=dict(color=SLATE)),
            xaxis=dict(
                title_font=dict(color=SLATE_MUTED),
                tickfont=dict(color=SLATE_MUTED),
                gridcolor=TAN,
                linecolor=TAN,
                zerolinecolor=TAN,
            ),
            yaxis=dict(
                title_font=dict(color=SLATE_MUTED),
                tickfont=dict(color=SLATE_MUTED),
                gridcolor=TAN,
                linecolor=TAN,
                zerolinecolor=TAN,
            ),
        )
    else:
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0b1220",
            plot_bgcolor="#151f32",
            font=dict(color="#e8eef7"),
            title=dict(font=dict(color="#f0fdfa", size=16)),
            legend=dict(font=dict(color="#e8eef7")),
            xaxis=dict(
                title_font=dict(color="#94a3b8"),
                tickfont=dict(color="#94a3b8"),
                gridcolor="#334155",
                linecolor="#475569",
                zerolinecolor="#475569",
            ),
            yaxis=dict(
                title_font=dict(color="#94a3b8"),
                tickfont=dict(color="#94a3b8"),
                gridcolor="#334155",
                linecolor="#475569",
                zerolinecolor="#475569",
            ),
        )
    return fig
