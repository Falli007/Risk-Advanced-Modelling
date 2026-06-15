"""Connector for the openFDA Enforcement (Recalls) API.

Docs: https://open.fda.gov/apis/drug/enforcement/ and
      https://open.fda.gov/apis/device/enforcement/
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.utils.http_cache import load_or_fetch_json

BASE_URLS = {
    "drug": "https://api.fda.gov/drug/enforcement.json",
    "device": "https://api.fda.gov/device/enforcement.json",
}
RAW_DIR = Path("data/raw/enforcement")

FIELDS = [
    "recall_number", "status", "classification", "product_type", "product_description",
    "reason_for_recall", "recalling_firm", "city", "state", "country",
    "report_date", "recall_initiation_date", "voluntary_mandated", "distribution_pattern",
]


def fetch_recalls(category: str = "drug", search: str | None = None, limit: int = 100,
                   max_records: int = 1000, force_refresh: bool = False) -> pd.DataFrame:
    """Fetch recall/enforcement records for `category` ('drug' or 'device').

    `search` uses openFDA's Lucene-style query syntax, e.g. "state:CA" or
    "report_date:[20230101+TO+20231231]". Pass None for the most recent records.
    """
    if category not in BASE_URLS:
        raise ValueError(f"category must be one of {list(BASE_URLS)}, got {category!r}")
    base_url = BASE_URLS[category]

    all_results: list[dict] = []
    skip = 0
    while skip < max_records:
        page_limit = min(limit, max_records - skip)
        params: dict = {"limit": page_limit, "skip": skip}
        if search:
            params["search"] = search

        cache_name = f"{category}_{(search or 'recent').replace(':', '_').replace(' ', '_')}_skip{skip}"
        try:
            payload = load_or_fetch_json(RAW_DIR, cache_name, base_url, params, force_refresh=force_refresh)
        except Exception as exc:
            if skip == 0:
                raise RuntimeError(f"openFDA enforcement request failed for {category}: {exc}") from exc
            break

        results = payload.get("results", [])
        if not results:
            break
        all_results.extend(results)
        skip += len(results)
        if len(results) < page_limit:
            break

    if not all_results:
        return pd.DataFrame(columns=FIELDS + ["category"])

    df = pd.DataFrame(all_results)
    for field in FIELDS:
        if field not in df.columns:
            df[field] = None
    df = df[FIELDS]
    df["category"] = category
    return df
