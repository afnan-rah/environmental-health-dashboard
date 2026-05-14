"""Streamlit-cached dataset loaders (import only from Streamlit pages)."""

from __future__ import annotations

import streamlit as st
from pandas import DataFrame

from src.analysis.geo_enrichment import enrich_arsenic_for_maps, enrich_mosquito_for_maps
from src.analysis.loaders import load_arsenic_cleaned, load_mosquito_cleaned


@st.cache_data(show_spinner=False)
def get_arsenic() -> DataFrame:
    return load_arsenic_cleaned()


@st.cache_data(show_spinner=False)
def get_mosquito() -> DataFrame:
    return load_mosquito_cleaned()


@st.cache_data(show_spinner=False)
def get_arsenic_enriched() -> DataFrame:
    return enrich_arsenic_for_maps(load_arsenic_cleaned())


@st.cache_data(show_spinner=False)
def get_mosquito_enriched() -> DataFrame:
    return enrich_mosquito_for_maps(load_mosquito_cleaned())
