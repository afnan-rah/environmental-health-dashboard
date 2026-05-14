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

### Run the dashboard (recommended)

From the **repository root** (`environmental-health-dashboard/`):

```bash
chmod +x scripts/run_dashboard.sh   # once
./scripts/run_dashboard.sh
```

Your browser should open to **Local URL** (usually `http://localhost:8501`).  
Use the **left sidebar** to open **Arsenic Explorer**, **Mosquito Surveillance**, etc.

**Alternative (same effect):**

```bash
source venv/bin/activate
export PYTHONPATH="$(pwd)"
streamlit run app.py
```

If imports fail with `ModuleNotFoundError: src`, you forgot `PYTHONPATH` or the run script—always run from the repo root.

### Run the exploration notebooks (graphs)

1. Open this **folder** in Cursor/VS Code (not an isolated notebook file outside the repo).
2. `source venv/bin/activate` then `pip install -r requirements.txt`
3. **One-time kernel:**  
   `python -m ipykernel install --user --name environmental-health-dashboard --display-name "Python (env-health-dashboard)"`
4. Open `notebooks/01_data_exploration.ipynb` or `notebooks/02_exploratory_analysis.ipynb`.
5. **Select kernel:** *Python (env-health-dashboard)* (or pick `venv/bin/python`).
6. **Run All** (or run cells top to bottom).  
   If Plotly charts are blank, in notebook `02` change the first code cell to  
   `pio.renderers.default = "notebook_connected"` instead of `"vscode"`.

## Data

Place new raw files in `data/raw/`. Regenerate anything in `data/processed/` using the pipeline in `src/cleaning/` (to be expanded in later phases).
