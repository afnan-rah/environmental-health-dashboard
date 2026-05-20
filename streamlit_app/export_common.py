"""Shared helpers for dashboard chart/map downloads (no Kaleido / Chrome)."""

from __future__ import annotations

import re
import tempfile
import zipfile
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path

import folium
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.graph_objects as go

_MPL_BG = "#0b1220"
_MPL_FG = "#f0fdfa"
_MPL_TICK = "#94a3b8"
_MPL_GRID = "#64748b"


@dataclass
class ExportBundle:
    files: dict[str, bytes] = field(default_factory=dict)
    chart_labels: dict[str, str] = field(default_factory=dict)
    png_chart_count: int = 0
    png_errors: list[str] = field(default_factory=list)


def plotly_title(fig: go.Figure, fallback: str = "") -> str:
    t = fig.layout.title
    if t is None:
        return fallback
    text = t.text
    return str(text).strip() if text else fallback


def plotly_xlabel(fig: go.Figure, fallback: str = "") -> str:
    ax = fig.layout.xaxis
    if ax is None or ax.title is None:
        return fallback
    text = ax.title.text
    return str(text).strip() if text else fallback


def plotly_ylabel(fig: go.Figure, fallback: str = "") -> str:
    ax = fig.layout.yaxis
    if ax is None or ax.title is None:
        return fallback
    text = ax.title.text
    return str(text).strip() if text else fallback


def fig_html(fig: go.Figure) -> bytes:
    return fig.to_html(include_plotlyjs="cdn", full_html=True).encode("utf-8")


def map_html(fmap: folium.Map) -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        path = Path(tmp.name)
    try:
        fmap.save(str(path))
        return path.read_bytes()
    finally:
        path.unlink(missing_ok=True)


def mpl_axes(figsize: tuple[float, float] = (8, 5)):
    fig, ax = plt.subplots(figsize=figsize, facecolor=_MPL_BG)
    ax.set_facecolor(_MPL_BG)
    return fig, ax


def mpl_style_axes(ax, *, title: str, xlabel: str = "", ylabel: str = "") -> None:
    if title:
        ax.set_title(title, color=_MPL_FG, fontsize=11, wrap=True)
    if xlabel:
        ax.set_xlabel(xlabel, color=_MPL_TICK)
    if ylabel:
        ax.set_ylabel(ylabel, color=_MPL_TICK)
    ax.tick_params(colors=_MPL_TICK)
    ax.grid(True, alpha=0.2, color=_MPL_GRID)


def mpl_save(fig: plt.Figure, dpi: int = 150) -> bytes:
    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


def zip_bytes(files: dict[str, bytes]) -> bytes:
    buf = BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in files.items():
            zf.writestr(name, data)
    return buf.getvalue()


def zip_png_only(files: dict[str, bytes]) -> bytes:
    return zip_bytes({k: v for k, v in files.items() if k.endswith(".png")})


def zip_html_only(files: dict[str, bytes]) -> bytes:
    return zip_bytes({k: v for k, v in files.items() if k.endswith(".html")})


def safe_filename(title: str, ext: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[-\s]+", "_", slug).strip("_")[:80] or "chart"
    return f"{slug}.{ext}"
