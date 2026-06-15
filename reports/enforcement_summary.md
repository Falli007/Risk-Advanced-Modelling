# Manufacturing Recall Risk Watchlist

_Generated 2026-06-14 from 3,000 openFDA drug enforcement (recall) records covering 2012-06-20 to 2026-05-13._

## What this means

Across 740 firms with at least one recall in this dataset, 1 firm(s) are flagged **Critical** and 50 firm(s) **High** risk based on how often they recall product, how severe those recalls are (Class I = most severe, both as a raw rate and via a severity classifier), and how recent their most recent recall is.

## Top-risk firms

| Firm | Recalls | Class I rate | Severity score (model) | Risk band |
|---|---|---|---|---|
| King Bio Inc. | 78 | 100% | 99% | Critical |
| Green Lumber Holdings, LLC | 2 | 100% | 98% | High |
| Supercore Products Group Inc. | 1 | 100% | 98% | High |
| Pyramids Wholesale Inc. | 2 | 100% | 98% | High |
| FA Online Inc | 1 | 100% | 98% | High |

## Severity classifier

A text-based classifier (TF-IDF on `reason_for_recall` + firm location/voluntary flag, logistic regression) predicts P(Class I) per recall, achieving a 5-fold cross-validated ROC-AUC of **0.97** on 3,000 recalls (297 Class I, 9.9% prevalence). The mean predicted probability per firm (`severity_risk`) is used alongside the raw Class I rate in the risk score above, since the raw rate alone is unstable for firms with only one or two recalls. Model saved to `models/recall_severity_classifier.joblib`.

## Severity comparison

The top-ranked firm's Class I recall rate is statistically different from all other firms combined (chi-square p=0.0000).

## Reporting-volume anomalies

5 month(s) in this dataset had recall volumes more than 2.5 standard deviations from the mean — worth checking against known industry events (e.g. contamination outbreaks, supply-chain issues, new FDA enforcement priorities).

## Important caveats

- A recall *count* does not reflect units shipped, patients affected, or company size — a large manufacturer will naturally have more recalls than a small one.

- Firms with only one or two recalls can show a 100% raw Class I rate purely by chance — the model-based `severity_risk` score is included specifically to reduce (not eliminate) this small-sample instability.

- This is a single snapshot; trend direction (improving vs. worsening) requires re-running this analysis over time.

## Recommended next steps

1. Quality/regulatory team to review the Critical/High firms' `reason_for_recall` text for common root causes (e.g. contamination, labeling, potency).

2. Normalise by firm size/market share if available, to avoid penalising large manufacturers purely for volume.

3. Track risk bands over successive quarters to identify firms trending toward higher risk.
