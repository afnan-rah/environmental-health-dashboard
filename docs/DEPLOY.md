# Publish the dashboard on the internet (free)

## Important: GitHub Pages vs Streamlit

| Platform | What it hosts | This dashboard |
|----------|----------------|----------------|
| **GitHub Pages** | Static HTML/CSS/JS only | Landing page in `docs/` (optional) |
| **Streamlit Community Cloud** | Python + Streamlit apps | **Full interactive dashboard** |

You cannot run this Streamlit app *inside* GitHub Pages. Use **Streamlit Community Cloud** for the live app, and optionally **GitHub Pages** for a short landing page that links to it.

---

## Step 1 — Push code to GitHub

From the repo root:

```bash
git add -A
git status   # confirm data/processed/*.csv and data/geo/*.geojson are included
git commit -m "Prepare dashboard for public deployment"
git push origin main
```

The cloud app needs these tracked files (already allowed in `.gitignore`):

- `data/processed/arsenic_cleaned.csv`
- `data/processed/mosquito_cleaned.csv`
- `data/processed/mi_zip_reference.csv`
- `data/processed/kent_area_city_centroids.csv`
- `data/geo/mi_counties*.geojson`

Raw Excel files under `data/raw/` are optional for the hosted app (not required if processed CSVs are committed).

---

## Step 2 — Deploy on Streamlit Community Cloud (recommended)

1. Sign in at **[share.streamlit.io](https://share.streamlit.io)** with your **GitHub** account.
2. Click **Create app** → **From existing repo**.
3. Select repository: `afnan-rah/environmental-health-dashboard`.
4. Set:
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL (optional):** e.g. `environmental-health-dashboard`
5. Click **Deploy**.

First build may take a few minutes (`pip install -r requirements.txt`).

**Live deployment:**

[https://environmental-health-dashboard-afnanrahman.streamlit.app/](https://environmental-health-dashboard-afnanrahman.streamlit.app/)

### If the deploy fails

- Open **Manage app → Logs** and check for missing files or import errors.
- Ensure `app.py` is at the repo root and processed data is pushed.
- Dependencies are in root `requirements.txt` (slim set for the app only). For local notebooks/scripts use `pip install -r requirements-dev.txt`.

---

## Step 3 — Optional GitHub Pages landing page

This repo includes a static page in `docs/index.html` and workflow `.github/workflows/deploy-pages.yml`.

1. On GitHub: **Settings → Pages → Build and deployment**
   - Source: **GitHub Actions** (the workflow deploys `docs/` on push to `main`).
2. After the workflow runs, your site is at:
   `https://afnan-rah.github.io/environmental-health-dashboard/`
3. The landing page button already points to the Streamlit app URL in `docs/index.html`.

---

## Updating the live app

Push to `main`. Streamlit Cloud redeploys automatically. GitHub Pages updates when `docs/` changes.

---

## Privacy note

The hosted app uses **processed CSVs committed to the repo**. Do not push raw spreadsheets or secrets if they contain sensitive fields you do not want public. Never commit `.streamlit/secrets.toml`.
