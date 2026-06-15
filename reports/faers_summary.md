# Pharmacovigilance Signal Watchlist — HUMIRA

_Generated 2026-06-14 from openFDA FAERS data (685,851 reports for HUMIRA out of 20,328,575 total reports)._

## What this means

Out of HUMIRA's most commonly reported adverse events, 12 are reported disproportionately more often than for drugs in general. The table below ranks these by overall risk (statistical strength, reporting volume, and reporting confidence combined).

## Top signals

| Reaction | Reports | PRR (95% CI) | Risk band |
|---|---|---|---|
| Rheumatoid Arthritis | 34,046 | 12.9 (12.7-13.0) | Critical |
| Injection Site Haemorrhage | 16,850 | 8.1 (7.9-8.2) | High |
| Device Issue | 17,992 | 7.9 (7.7-8.0) | High |
| Injection Site Pain | 50,447 | 6.0 (5.9-6.0) | High |
| Psoriasis | 24,564 | 6.9 (6.8-7.0) | High |

## Important caveats

- openFDA data is **unvalidated** spontaneous-report data — it shows reporting patterns, not confirmed causation.

- A high signal for a condition the drug *treats* (e.g. an arthritis drug showing a signal for 'Rheumatoid arthritis') usually reflects **confounding by indication**, not a side effect — these need clinical triage, not automatic escalation.

- 0 month(s) showed anomalous reporting volume — worth checking against label changes, litigation, or media coverage in those periods.

## Case-level anomaly triage

An Isolation Forest model trained on 3,000 individual HUMIRA reports (features: number of reactions, number of co-reported drugs, patient age, seriousness) flagged 150 reports (5.0%) as statistically unusual case profiles. These are candidates for case-narrative review by signal-management staff, not confirmed issues. Model saved to `models/faers_case_anomaly_iforest.joblib`.

## Recommended next steps

1. Clinical reviewer to triage the top-ranked signals, separating known indications/contraindications from genuinely new signals.

2. Signal-management staff to review the highest-scoring case-level anomalies identified by the Isolation Forest model.

3. Re-run this analysis monthly to track trend direction (worsening vs. stable).

4. For any new genuine signal, cross-check against the product's current label and any open regulatory safety communications.
