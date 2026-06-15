"""Connector for the openFDA Drug Adverse Event API (FAERS).

Docs: https://open.fda.gov/apis/drug/event/
Without an API key, openFDA caps `limit` at 500 per request (1000 requires a
key) and applies a per-IP rate limit (~240 requests/min, 1000/day) — pass
`api_key` to raise both. Default page `limit` here is kept at 100 to stay
well clear of the per-minute limit during repeated notebook runs.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.utils.http_cache import load_or_fetch_json

BASE_URL = "https://api.fda.gov/drug/event.json"
RAW_DIR = Path("data/raw/faers")


def fetch_events_for_drug(drug_name: str, limit: int = 100, max_records: int = 1000,
                           api_key: str | None = None, force_refresh: bool = False) -> pd.DataFrame:
    """Fetch FAERS adverse event reports mentioning `drug_name` (matched on
    patient.drug.medicinalproduct), paging until `max_records` or exhaustion.

    Returns a flattened DataFrame with one row per (report, reaction) pair.
    """
    search = f'patient.drug.medicinalproduct:"{drug_name}"'
    all_results: list[dict] = []
    skip = 0
    while skip < max_records:
        page_limit = min(limit, max_records - skip)
        params = {"search": search, "limit": page_limit, "skip": skip}
        if api_key:
            params["api_key"] = api_key

        cache_name = f"{drug_name.lower().replace(' ', '_')}_skip{skip}_limit{page_limit}"
        try:
            payload = load_or_fetch_json(RAW_DIR, cache_name, BASE_URL, params, force_refresh=force_refresh)
        except Exception as exc:  # network or 404 (no more results)
            if skip == 0:
                raise RuntimeError(f"openFDA FAERS request failed for '{drug_name}': {exc}") from exc
            break

        results = payload.get("results", [])
        if not results:
            break
        all_results.extend(results)
        skip += len(results)
        if len(results) < page_limit:
            break

    return _flatten_reports(all_results, queried_drug=drug_name)


def fetch_reaction_counts(search: str | None = None, limit: int = 100,
                           force_refresh: bool = False) -> pd.DataFrame:
    """Fetch counts of reports per reaction term (`patient.reaction.reactionmeddrapt.exact`),
    optionally restricted by `search`. Used to build background reaction rates.

    Returns a DataFrame with columns: reaction_pt, count.
    """
    params: dict = {"count": "patient.reaction.reactionmeddrapt.exact", "limit": limit}
    if search:
        params["search"] = search

    cache_name = f"reaction_counts_{(search or 'all').replace(':', '_').replace(' ', '_').replace('\"', '')}_limit{limit}"
    payload = load_or_fetch_json(RAW_DIR, cache_name, BASE_URL, params, force_refresh=force_refresh)
    results = payload.get("results", [])
    df = pd.DataFrame(results).rename(columns={"term": "reaction_pt"})
    return df


def fetch_total_report_count(search: str | None = None, force_refresh: bool = False) -> int:
    """Return the total number of FAERS reports matching `search` (or all reports if None)."""
    params: dict = {"limit": 1}
    if search:
        params["search"] = search

    cache_name = f"total_count_{(search or 'all').replace(':', '_').replace(' ', '_').replace('\"', '')}"
    payload = load_or_fetch_json(RAW_DIR, cache_name, BASE_URL, params, force_refresh=force_refresh)
    return payload.get("meta", {}).get("results", {}).get("total", 0)


def _flatten_reports(reports: list[dict], queried_drug: str) -> pd.DataFrame:
    rows = []
    for report in reports:
        report_id = report.get("safetyreportid")
        receive_date = report.get("receivedate")
        serious = report.get("serious")
        country = report.get("primarysourcecountry")
        patient = report.get("patient", {})
        age = patient.get("patientonsetage")
        sex = patient.get("patientsex")

        reactions = patient.get("reaction", [])
        drugs = patient.get("drug", [])
        drug_names = sorted({d.get("medicinalproduct", "") for d in drugs if d.get("medicinalproduct")})

        if not reactions:
            reactions = [{}]
        for reaction in reactions:
            rows.append({
                "safetyreportid": report_id,
                "receivedate": receive_date,
                "serious": serious,
                "primarysourcecountry": country,
                "patientonsetage": age,
                "patientsex": sex,
                "queried_drug": queried_drug,
                "drugs_in_report": ", ".join(drug_names),
                "reaction_pt": reaction.get("reactionmeddrapt"),
                "reaction_outcome": reaction.get("reactionoutcome"),
            })
    return pd.DataFrame(rows)
