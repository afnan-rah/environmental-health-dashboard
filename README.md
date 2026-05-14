# Environmental Health Intelligence Dashboard

A polished environmental analytics workspace for **non-technical researchers**: clear maps, filters, trends, and plain-language context—built on a **reproducible** path from raw spreadsheets to a Streamlit app.

## What this delivers

- **Arsenic module (planned):** test locations, hotspots, filters (year / city / ZIP), trends, severity context.
- **Mosquito module (planned):** surveillance sites, counts/species, detection trends, seasonal comparison.
- **Combined intelligence (later):** geographic overlap and interpretation support for public health narratives.

## Architecture

```
Raw Excel → cleaning pipeline → processed datasets → analysis → maps / charts → Streamlit → research-friendly insights
```

## Repository layout

| Path | Purpose |
|------|--------|
| `data/raw/` | Original spreadsheets (do not edit in place). |
| `data/processed/` | Standardized outputs from the cleaning pipeline. |
| `notebooks/` | Exploratory analysis and QA. |
| `src/cleaning/` | Ingestion and normalization code. |
| `src/analysis/` | Metrics, hotspots, trends. |
| `src/visualization/` | Shared map/chart helpers. |
| `src/utils/` | Paths, config, shared helpers. |
| `streamlit_app/` | Optional multipage Streamlit pieces as the app grows. |
| `outputs/` | Exported figures, tables, or reports. |
| `app.py` | Main Streamlit entrypoint. |

## Environment setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run app.py
```

## Data

Place new raw files in `data/raw/`. Regenerate anything in `data/processed/` using the pipeline in `src/cleaning/` (to be expanded in later phases).
