Project handoff: Product Line Profitability & Margin Performance Analysis

Overview

This repository contains a reproducible analytics pipeline and Streamlit dashboard for Nassau Candy Distributor. It includes ETL, cleaning, KPI calculations, Pareto and cost diagnostics, margin-risk scoring, and an interactive Streamlit app.

Quick setup (Windows)

1. Clone the repo and change directory:

```powershell
cd C:\path\to\workspace\Productline_project
```

2. Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
# if using generated requirements with pins: pip install -r requirements.txt
```

4. Add your order-level export to `data/raw/orders.csv` (or use the sample included).

Run tests

```powershell
python -m pytest -q
```

Run the Streamlit app locally

```powershell
streamlit run app/dashboard.py
```

Notes for deployment

- Streamlit Cloud: push this repo to GitHub and connect it to Streamlit Cloud; ensure `requirements.txt` is present. Set `streamlit run app/dashboard.py` as the run command if Streamlit doesn't auto-detect.

- Docker (optional): a Dockerfile is provided for containerized deployment. Build and run:

```powershell
docker build -t nassau-candy-analytics:latest .
docker run -p 8501:8501 nassau-candy-analytics:latest
```

Files of interest

- `src/` — ETL, cleaning, metrics
- `app/` — Streamlit app and page modules
- `data/raw/orders.csv` — raw order export (sample included)
- `notebooks/eda.ipynb` — exploratory notebook
- `reports/` — generated executive_summary.pdf and report artifacts
- `tests/` — unit tests
- `scripts/generate_report.py` — generates report PDF and images

Handoff checklist

- [ ] Confirm dataset access and refresh cadence
- [ ] Provide any API/DB credentials or data extract instructions
- [ ] Decide deployment target (Streamlit Cloud / internal server / Docker)
- [ ] Schedule automated runs (cron, Azure/AWS scheduler) if needed
- [ ] Share stakeholder contacts for UAT and signoff

Contact

For questions about code or deployment steps, review `README.md` or contact the code author.
