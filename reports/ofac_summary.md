# Sanctions Screening Triage — OFAC SDN List

_Generated 2026-06-14. Screened 8 vendor names against 9,741 OFAC SDN entity records (downloaded live from Treasury)._

## What this means

3 of 8 screened names produced a fuzzy match (score >= 75) against the SDN list and require analyst review before onboarding or payment. 5 produced no qualifying match and can be cleared, pending standard due diligence.

## Matches requiring review

| Vendor name (candidate) | Closest SDN match | Score | Risk band |
|---|---|---|---|
| Aerocaribean Airlins | AEROCARIBBEAN AIRLINES | 95 | Critical |
| Banco Nacional de Cuba SA | BANCO NACIONAL DE CUBA | 94 | Critical |
| Anglo Caribbean Co Ltd | ANGLO-CARIBBEAN CO., LTD. | 89 | Critical |

## Cleared (no qualifying match)

- Acme Logistics Group Inc
- Global Freight Solutions Ltd
- Northwind Pharma Supplies BV
- Meridian Clinical Research LLC
- Sunrise Medical Devices Pty Ltd

## Important caveats

- A fuzzy name match is a **lead for review**, not a sanctions determination. Analysts must compare addresses, dates of birth, ID numbers, and program tags on the full SDN record before escalating.

- Common/generic words (e.g. 'Holdings', 'Group', 'International') can produce false-positive matches purely from shared vocabulary — review the *whole* name, not just the score.

- The SDN list changes frequently; screening results are only valid as of the pull date above and should be refreshed before each screening run.

## Recommended next steps

1. Compliance analyst to review each 'matches requiring review' row against the full SDN record (address, aliases, program).

2. For confirmed matches, escalate per the firm's sanctions escalation procedure and freeze any pending transactions.

3. Re-run this screening on a recurring schedule (e.g. before each new vendor onboarding and periodically against the existing vendor base, since the SDN list changes over time).
