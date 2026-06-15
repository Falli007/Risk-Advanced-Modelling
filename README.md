# Risk & Advanced Modelling — Simulation Project

Four independent risk-analytics modules for a regulated/life-sciences setting, each
pulling **real, live, public regulatory data** (openFDA, ClinicalTrials.gov, US Treasury
OFAC), built on a shared risk-scoring/ML framework, and surfaced through an interactive
dashboard with stakeholder-facing reports.

📄 **[Read the case study](docs/CASE_STUDY.md)** for the situation/approach/result/
recommendation behind each module, the overall architecture, and lessons learned.
See [CLAUDE.md](CLAUDE.md) for the underlying role brief and working conventions.

## Risk dashboard

A Streamlit app (`app/dashboard.py`) presents the risk outputs of all four modules in one
place — risk-banded watchlists, charts, model performance cards, and the stakeholder
summaries — so a reviewer can explore the results without running any code.

```bash
streamlit run app/dashboard.py
```

| Pharmacovigilance signals (FAERS) | Recall / manufacturing risk (Enforcement) |
|---|---|
| ![FAERS dashboard](docs/screenshots/faers.png) | ![Enforcement dashboard](docs/screenshots/enforcement.png) |

| Clinical trial risk & scenarios | Sanctions screening (OFAC) |
|---|---|
| ![Clinical trials dashboard](docs/screenshots/clinicaltrials.png) | ![OFAC dashboard](docs/screenshots/ofac.png) |

The dashboard reads pre-generated outputs from `data/processed/<module>/`, so run each
notebook at least once first (each notebook's final cells write these processed files
alongside the `reports/*.md` summaries).

## Modules

| # | Module | Data source | Notebook | Report |
|---|--------|-------------|----------|--------|
| 1 | Pharmacovigilance signal detection | [openFDA FAERS](https://open.fda.gov/apis/drug/event/) | `notebooks/01_faers_signal_detection.ipynb` | `reports/faers_summary.md` |
| 2 | Recall / manufacturing quality risk | [openFDA Enforcement](https://open.fda.gov/apis/drug/enforcement/) | `notebooks/02_enforcement_recall_risk.ipynb` | `reports/enforcement_summary.md` |
| 3 | Clinical trial risk & scenario modelling | [ClinicalTrials.gov v2](https://clinicaltrials.gov/data-api/api) | `notebooks/03_clinicaltrials_risk.ipynb` | `reports/clinicaltrials_summary.md` |
| 4 | Sanctions / compliance entity screening | [OFAC SDN list](https://sanctionslistservice.ofac.treas.gov/) | `notebooks/04_ofac_screening.ipynb` | `reports/ofac_summary.md` |

All four notebooks run end-to-end against live data and have been executed at least once.

Run notebooks in order from the `notebooks/` directory (each is self-contained). First
runs will fetch and cache data into `data/raw/<module>/`; subsequent runs use the cache.

### How a risk score is built

Each module's `risk_score` is a **weighted composite**, produced by the shared
`RiskScoringEngine` (`src/risk_framework/risk_scoring.py`) from several inputs — some
rule-based/statistical, some the output of an ML model:

- **FAERS**: PRR/ROR signal strength + statistical confidence + report volume.
- **Enforcement**: recall frequency + recency + a logistic-regression model's predicted
  P(Class I recall).
- **Clinical trials**: a RandomForest model's predicted P(terminated/withdrawn/suspended)
  + reporting-quality risk + trial-scale risk.
- **OFAC**: fuzzy match strength against the SDN list.

## Models

Modules 1-3 each train and persist a model to `models/`, with a `.meta.json`
sidecar recording features, training date, dataset size, and (where applicable)
cross-validated performance metrics:

| Model | Type | Dataset | CV performance |
|---|---|---|---|
| `faers_case_anomaly_iforest.joblib` | IsolationForest (unsupervised) | 3,000 HUMIRA FAERS reports | 5.0% flagged at contamination=0.05 (no ground-truth labels) |
| `recall_severity_classifier.joblib` | Logistic Regression (TF-IDF + OneHotEncoder) | 3,000 openFDA drug recalls (9.9% Class I) | ROC-AUC 0.97 (5-fold stratified CV) |
| `clinical_trial_termination_classifier.joblib` | RandomForest | 455 trials across 5 related Diabetes conditions (9.5% terminated/withdrawn/suspended) | ROC-AUC 0.84 (5-fold stratified CV) |

All classifiers are evaluated via cross-validation rather than a single
train/test split, since the positive classes are small (a single split gave
misleadingly optimistic or unstable numbers). See each notebook's "caveats"
section and the corresponding `.meta.json` for details and known limitations.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Project layout

```
app/                    # Streamlit risk dashboard
src/data_connectors/    # one module per external API
src/risk_framework/     # shared, reusable risk-modelling components
src/utils/               # HTTP fetch + caching with pull metadata
data/raw/                # cached raw API responses + .meta.json sidecars (gitignored)
data/processed/          # cleaned/feature-engineered data, consumed by the dashboard
models/                  # trained model artifacts (.joblib) + metadata (.meta.json)
notebooks/               # analysis notebooks, one per module
reports/                 # stakeholder-facing summaries (markdown)
tests/                   # unit tests for src/risk_framework
docs/screenshots/        # dashboard screenshots used in this README
```

## Running tests

```bash
pytest
```

## Limitations & governance notes

This is a practice/portfolio project, not a production system or a regulatory submission.
All data is real and pulled live from public sources, but:

- Risk scores are **decision-support aids for analyst triage**, not automated
  determinations — every report and dashboard page says so explicitly.
- Some inputs (e.g. the OFAC screening "vendor list", the chosen drug/therapeutic area)
  are illustrative selections for this exercise, not a real client's data — this is
  called out where it applies.
- Model caveats (class imbalance, sample size, lack of ground truth for unsupervised
  methods) are documented in each `.meta.json` and notebook rather than glossed over —
  reflecting the level of scrutiny this kind of work gets under real regulatory review.
