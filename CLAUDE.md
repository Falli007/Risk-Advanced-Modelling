# Risk & Advanced Modelling — Simulation Project

## Purpose

This repository simulates the day-to-day work of a **Data Scientist – Risk & Advanced
Modelling** role at a data & analytics consultancy, working client-facing in **regulated /
life sciences** environments. The goal is to practise the full workflow: connecting to real
external data, building risk/predictive/scenario models, detecting anomalies and emerging
threats, and communicating findings to technical and non-technical stakeholders.

All data sources below are **real, public, and free** (no paid API keys required), so the
project reflects genuine data quality issues (missingness, inconsistent coding, duplicates,
reporting lag) rather than clean synthetic data.

## Role Context (what this project is practising)

- Designing risk models, predictive models, and scenario-based simulations
- Building ML/statistical models intended for production-style deployment (reproducible,
  versioned, monitored)
- Threat detection, risk scoring, and anomaly detection
- Working with large, messy, regulatory/clinical/operational datasets
- Translating regulatory/business requirements into analytical frameworks
- Exploratory data analysis to surface patterns, trends, risks
- Communicating results to both technical and non-technical audiences
- Awareness of governance, compliance, and safety-critical considerations (even when
  working with public data, treat it as if it were sensitive — no shortcuts that wouldn't
  be acceptable with real regulated/clinical data)

## Modules

Each module is a self-contained mini-engagement with its own data connector, risk
framework component, and stakeholder-facing output.

### 1. Pharmacovigilance Signal Detection (`faers`)
- **Data source**: openFDA Drug Adverse Event API (FAERS) — `https://api.fda.gov/drug/event.json`
- **Scenario**: A pharma client wants early warning of new drug–adverse event "signals".
- **Techniques**: disproportionality analysis (PRR, ROR, with chi-square / confidence
  intervals), trend analysis over report dates, anomaly detection on signal scores.
- **Output**: ranked signal watchlist + plain-English summary memo.

### 2. Drug & Device Recall / Manufacturing Quality Risk (`enforcement`)
- **Data source**: openFDA Enforcement (Recalls) API —
  `https://api.fda.gov/drug/enforcement.json` and `https://api.fda.gov/device/enforcement.json`
- **Scenario**: Identify manufacturers/products with elevated recall risk and classify
  recall severity (Class I/II/III) drivers.
- **Techniques**: risk scoring framework (frequency × severity × recency), classification
  model for recall class, anomaly detection on recall volume by firm/state/time.

### 3. Clinical Trial Risk & Scenario Modelling (`clinicaltrials`)
- **Data source**: ClinicalTrials.gov API v2 — `https://clinicaltrials.gov/api/v2/studies`
- **Scenario**: A trial sponsor wants a risk score per trial (enrollment risk, completion
  risk, protocol amendment risk) and "what-if" scenario simulations for enrollment timelines.
- **Techniques**: risk scoring framework, survival/time-to-event style features, Monte
  Carlo scenario simulation for enrollment completion dates.

### 4. Sanctions / Compliance Entity Screening (`ofac`)
- **Data source**: US Treasury OFAC Specially Designated Nationals (SDN) list —
  `https://www.treasury.gov/ofac/downloads/sdn.csv` (and consolidated list)
- **Scenario**: A financial-services/life-sciences client needs to screen counterparties
  against sanctions lists and flag fuzzy-match anomalies (typos, transliterations).
- **Techniques**: fuzzy/approximate string matching, anomaly detection on match-score
  distributions, risk scoring/triage framework for compliance analysts.

## Shared Risk Framework (`src/risk_framework/`)

Common, reusable components used across modules — build these generically, not tied to
one module's data shape:

- `signal_detection.py` — PRR, ROR, chi-square, confidence intervals
- `anomaly_detection.py` — z-score / control charts, Isolation Forest, seasonal baselines
- `risk_scoring.py` — generic weighted risk-scoring engine (configurable weights, bands:
  Low / Medium / High / Critical)
- `scenario_simulation.py` — Monte Carlo simulation utilities
- `stats.py` — hypothesis testing helpers (t-tests, chi-square, A/B style comparisons)

## Data Conventions

- Raw pulls from external APIs go in `data/raw/<module>/` (never edited by hand).
- Cleaned/feature-engineered data goes in `data/processed/<module>/`.
- Reference/lookup data (e.g. drug name dictionaries, MedDRA-style groupings if used) in
  `data/external/`.
- Always record the **pull date** and **API query parameters** alongside any cached data
  (e.g. a sidecar `.json` metadata file) — regulatory data changes over time and results
  must be reproducible/traceable.
- Cache API responses locally (data/raw) to avoid hammering public APIs and to keep
  notebooks reproducible offline.

## Tech Stack

- Python 3.11+, `pandas`, `numpy`, `scikit-learn`, `scipy`, `statsmodels`
- `requests` for API access
- `matplotlib` / `plotly` for visualisation
- `rapidfuzz` for fuzzy matching (OFAC module)
- Notebooks in `notebooks/` for EDA and model development; production-style code refactored
  into `src/`
- `pytest` for tests of risk framework functions (these are the "production" components —
  test them properly)

## Communication / Deliverables Convention

For each module, produce two outputs:
1. **Technical notebook** (`notebooks/`) — full analysis, assumptions, validation.
2. **Stakeholder summary** (`reports/<module>_summary.md`) — plain-English findings,
   risk ratings, and recommended actions, written for a non-technical client sponsor.
   Avoid jargon; lead with "what this means" before "how we got there".

## Working Conventions

- No fabricated data. If an API is unavailable, say so rather than substituting synthetic
  data silently — note the limitation in the report.
- Be explicit about assumptions and limitations of any risk score or model (this mirrors
  real regulatory scrutiny).
- Keep modules independent — a connector or model in one module should not import from
  another module's folder, only from `src/risk_framework/` or `src/utils/`.
- Treat all data as if it were sensitive regulated data: no plotting/printing of full raw
  records into reports, aggregate before sharing.
