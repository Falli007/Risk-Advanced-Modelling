# Clinical Trial Risk & Enrollment Scenario — Diabetes (5 related conditions combined)

_Generated 2026-06-14 from 478 unique trials registered on ClinicalTrials.gov across 5 related 'Diabetes' conditions._

## What this means

Of 478 trials reviewed, 43 have been terminated, withdrawn, or suspended, and 81 have an 'Unknown' status (the sponsor has stopped updating the registry). 0 trial(s) are flagged **Critical** and 4 **High** risk overall.

## Termination-risk classifier

A RandomForest classifier trained on 455 trials with a settled status (43 terminated/withdrawn/suspended, 9.5%) predicts P(termination/withdrawal/suspension) from enrollment target, phase, study type, sponsor class, and FDA-regulation flags. 5-fold cross-validated ROC-AUC: **0.84**. This is the dominant factor (weight 0.5) in the risk score below. Model saved to `models/clinical_trial_termination_classifier.joblib`.

## Highest-risk trials

| NCT ID | Title | Status | Why stopped | Termination risk (model) | Risk band |
|---|---|---|---|---|---|
| NCT01565096 | Effect of Adding Vildagliptin on Beta Cell Function and Card | UNKNOWN | - | 57% | High |
| NCT02477761 | Sustained Effects of a Non-glucidic Nutrient Preload on Gluc | UNKNOWN | - | 53% | High |
| NCT00673296 | Intravitreal Injection of Bevacizumab and Gas for Diabetic P | UNKNOWN | - | 52% | High |
| NCT01253928 | Pioglitazone, Body Composition,Insulin Sensitivity and Prote | UNKNOWN | - | 43% | High |
| NCT03859245 | Photobiomodulation & Ketogenic Diet for Treatment of Mid-per | UNKNOWN | - | 38% | Medium |

## Enrollment scenario for the largest recruiting trial

**NCT07135570** ("My Eyes, My Light": Amar Chokh, Amar Alo) is targeting **20000** participants. Using a benchmark enrollment rate of **8.5 participants/month** (derived from completed Diabetes (5 related conditions combined) trials, winsorized to remove outlier registries):

- At this benchmark rate, **0% of 10,000 simulations** completed enrollment within the 60-month simulation horizon — this trial's target enrollment is large relative to the typical recruitment pace observed in this therapeutic area. This itself is a risk signal worth escalating to the sponsor (re-baseline the target, add sites, or extend the timeline).

## Important caveats

- 'Enrollment count' on ClinicalTrials.gov is typically the *target*, not actual enrollment-to-date — this simulation assumes enrollment starts from zero.

- The benchmark rate is derived from a small, condition-specific sample and is sensitive to a handful of large registry-style studies — treat it as a planning reference, not a forecast.

- The termination-risk classifier was trained on only 43 positive cases — treat its scores as a triage aid, not a precise probability.

- 'Unknown' status often reflects administrative lapses, not necessarily trial failure — but it removes visibility for sponsors and regulators alike.

## Recommended next steps

1. Sponsor to follow up on 'Unknown'-status trials to confirm current status.

2. Review terminated/withdrawn trials' `why_stopped` text for recurring causes (funding, recruitment, safety) to inform protocol design for new trials.

3. Re-run the enrollment scenario quarterly with actual enrollment-to-date once available, to refine the forecast.
