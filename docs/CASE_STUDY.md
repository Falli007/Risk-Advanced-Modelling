# Case Study: Risk & Advanced Modelling for a Regulated Life-Sciences Client

## Context

This case study simulates an engagement for a **Data Scientist – Risk & Advanced
Modelling** consultant working client-facing in regulated/life-sciences environments. A
client portfolio (a pharma sponsor, a manufacturer, a clinical trial sponsor, and a
compliance team) needs early warning of emerging risks across four areas: drug safety
signals, manufacturing/recall quality, clinical trial delivery risk, and sanctions
exposure.

All data is **real, live, and public** — pulled directly from openFDA, ClinicalTrials.gov,
and the US Treasury OFAC sanctions list — so the data quality issues (missingness,
inconsistent coding, reporting lag, small positive classes) are the same ones a real
engagement would face. Nothing here is synthetic or fabricated. See
[CLAUDE.md](../CLAUDE.md) for the underlying role brief, module specs, and working
conventions.

Each module below follows the same shape: **situation → approach → result →
recommendation**, mirroring how this work would be packaged for a client.

---

## Module 1 — Pharmacovigilance signal detection (HUMIRA, openFDA FAERS)

**Situation**: The client wants early warning of adverse-event "signals" — reactions
reported disproportionately often for their drug versus drugs in general — and a way to
flag individual case reports that look statistically unusual.

**Approach**: Pulled 685,851 FAERS reports for HUMIRA (out of 20.3M total reports) and ran
disproportionality analysis (PRR/ROR with chi-square significance and 95% confidence
intervals) on the most common reaction terms. A 3,000-report sample was scored for
case-level anomalies with an Isolation Forest (contamination = 5%) on patient age,
reaction count, drug count, and seriousness.

**Result**: 12 of the screened reaction terms are reported disproportionately more often
for HUMIRA than for drugs generally — most notably Rheumatoid Arthritis (PRR 12.9,
95% CI 12.7-13.0) and Injection Site Haemorrhage (PRR 8.1). 150 of the 3,000 sampled
case reports (5%) were flagged as statistically unusual and prioritised for review.

**Recommendation**: Treat the Critical/High-band signals as candidates for a formal
pharmacovigilance signal assessment (most are already labelled risks for an
anti-TNF biologic, which is itself a useful sanity check on the method). Flagged
case reports should be triaged by a safety reviewer, with the caveat that "anomalous"
here means *statistically unusual for this drug's typical report profile*, not a
confirmed safety issue — there is no ground-truth label for the unsupervised model.

→ Full write-up: [`reports/faers_summary.md`](../reports/faers_summary.md) · Notebook:
[`01_faers_signal_detection.ipynb`](../notebooks/01_faers_signal_detection.ipynb)

---

## Module 2 — Recall / manufacturing quality risk (openFDA Enforcement)

**Situation**: The client (a manufacturer or distributor relationship-risk team) wants to
identify which firms in their supply chain carry elevated recall risk, and what drives the
severity of those recalls.

**Approach**: Pulled 3,000 drug enforcement (recall) records spanning 2012-2026. Trained a
Logistic Regression classifier (TF-IDF on the recall reason text + one-hot encoded state
and voluntary/mandated flag) to predict P(Class I recall) — the most severe category.
Combined recall frequency, recency, and the model's severity prediction into a per-firm
weighted risk score across 740 firms. Ran a z-score/control-chart anomaly check on
monthly recall volume.

**Result**: The severity classifier reached **ROC-AUC 0.97** under 5-fold cross-validation
(class I recalls are ~10% of the data, so CV rather than a single split was used to avoid
an unstable estimate). 1 firm was flagged **Critical** and 50 **High** risk — topped by a
firm with 78 recalls, 100% of which were Class I and scored 99% by the severity model.

**Recommendation**: Prioritise supplier-quality review for the Critical/High firms,
starting with the one firm combining high recall *frequency* with a near-certain Class I
*severity* profile — a combination that's rare (most high-frequency recallers in this
dataset are lower severity) and therefore a stronger signal than either factor alone.

→ Full write-up: [`reports/enforcement_summary.md`](../reports/enforcement_summary.md) ·
Notebook: [`02_enforcement_recall_risk.ipynb`](../notebooks/02_enforcement_recall_risk.ipynb)

---

## Module 3 — Clinical trial risk & enrollment scenario modelling (Diabetes, ClinicalTrials.gov)

**Situation**: A trial sponsor wants a per-trial risk score (likelihood of termination,
reporting-quality risk) across their therapeutic area, plus a realistic forecast of when
their largest currently-recruiting trial will finish enrolling.

**Approach**: Pulled 478 trials across 5 related Diabetes conditions. Trained a
RandomForest classifier (class_weight='balanced') on 455 trials with a settled status to
predict P(terminated/withdrawn/suspended) from enrollment target, phase, study type,
sponsor class, and FDA-regulation flags — chosen over Logistic Regression, which scored
near-random (ROC-AUC ~0.59) on this data. Combined that prediction with reporting-quality
and trial-scale risk into a per-trial score. Ran a Monte Carlo simulation (drawing from the
benchmark monthly enrollment rate across the cohort) to forecast completion timelines for
the largest recruiting trial.

**Result**: The termination-risk classifier reached **ROC-AUC 0.84** (5-fold CV; only 43 of
455 trials, 9.5%, were terminated/withdrawn/suspended, so minority-class metrics carry
wide uncertainty at this sample size). 81 of 478 trials have an "Unknown" registry status
(sponsor stopped updating) — itself a reporting-risk flag. 4 trials were flagged **High**
risk, 0 **Critical**. The enrollment simulation showed the target trial's enrollment goal
is large relative to the cohort's typical recruitment pace.

**Recommendation**: Engage sponsors of the 4 High-risk trials and the 81 trials with
"Unknown" status to confirm current trial state — a registry-reporting gap is itself an
operational risk for a sponsor relying on public registry data. For the enrollment
forecast, either re-baseline the target's monthly enrollment rate against this trial's
own early recruitment data (the cohort benchmark may not reflect site-specific factors)
or budget for a longer recruitment window.

→ Full write-up: [`reports/clinicaltrials_summary.md`](../reports/clinicaltrials_summary.md) ·
Notebook: [`03_clinicaltrials_risk.ipynb`](../notebooks/03_clinicaltrials_risk.ipynb)

---

## Module 4 — Sanctions / compliance entity screening (OFAC SDN list)

**Situation**: A compliance team needs to screen a batch of counterparty/vendor names
against the US Treasury's Specially Designated Nationals (SDN) list and triage likely
matches for analyst review, despite typos, abbreviations, and transliteration differences
in how names are recorded.

**Approach**: Downloaded the live SDN list (9,741 entity names) and fuzzy-matched 8
illustrative vendor names against it (`rapidfuzz`), keeping matches scoring ≥75/100. Match
strength was fed into the shared risk-scoring engine to produce Critical/Low triage bands.

**Result**: 3 of 8 names produced a qualifying fuzzy match — including a 1-character typo
("Aerocaribean Airlins" → "AEROCARIBBEAN AIRLINES", score 95) and a formatting/punctuation
variant ("Anglo Caribbean Co Ltd" → "ANGLO-CARIBBEAN CO., LTD.", score 89) — both the kind
of near-miss an exact-match screen would let through. The remaining 5 names produced no
match and were cleared pending standard due diligence.

**Recommendation**: Route the 3 matches to a compliance analyst to check identifying
details (address, aliases, program tags) on the full SDN record before any
escalation — a name match alone is a lead, not a determination. Re-run screening on a
recurring schedule, since the SDN list changes frequently.

→ Full write-up: [`reports/ofac_summary.md`](../reports/ofac_summary.md) · Notebook:
[`04_ofac_screening.ipynb`](../notebooks/04_ofac_screening.ipynb)

---

## How it fits together

```
external APIs (openFDA, ClinicalTrials.gov, Treasury OFAC)
        │  cached with pull-date + query metadata (data/raw/)
        ▼
notebooks/  ── EDA, modelling, risk scoring (per module)
        │
        ├──► models/            trained model artifacts + .meta.json cards
        ├──► data/processed/    risk-scored, dashboard-ready outputs
        └──► reports/           plain-English stakeholder summaries
                │
                ▼
        app/dashboard.py  (Streamlit) — interactive risk dashboard
```

The shared `src/risk_framework/` package (signal detection, anomaly detection, risk
scoring, scenario simulation, hypothesis testing) is used identically across all four
modules — each module supplies the inputs, the framework supplies the methodology.

## Reflections / what I'd do differently with a real client

- **Class imbalance is the recurring theme.** Both supervised classifiers have small
  positive classes (~10%); cross-validation rather than a single split was essential to
  get an honest performance estimate, and even then the minority-class metrics carry wide
  confidence intervals. With a real client I'd push for either more historical data or a
  cost-sensitive framing of the decision (what does a missed Critical actually cost?)
  rather than optimising a single metric.
- **Unsupervised ≠ validated.** The FAERS anomaly model and the recall-volume
  anomaly check have no ground truth — "anomalous" is a statistical statement, not a
  safety/quality conclusion. Every output that depends on them carries that caveat
  explicitly, which is the standard I'd hold any model to under real regulatory scrutiny.
- **A risk score is a triage tool, not a verdict.** This is most visible in the OFAC
  module — a 95% fuzzy match is a *lead*, and treating it as anything more would create
  false-positive operational friction (and, in the opposite direction, over-reliance on a
  score could mean a real hit gets waved through because "the score wasn't that high").
