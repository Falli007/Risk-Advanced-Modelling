"""Connector for the ClinicalTrials.gov API v2.

Docs: https://clinicaltrials.gov/data-api/api
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.utils.http_cache import load_or_fetch_json

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
RAW_DIR = Path("data/raw/clinicaltrials")


def fetch_studies(condition: str, status: str | None = None, max_records: int = 500,
                   page_size: int = 100, force_refresh: bool = False) -> pd.DataFrame:
    """Fetch studies for a given condition, paging via nextPageToken.

    `status` filters on overallStatus, e.g. "RECRUITING", "COMPLETED", "TERMINATED".
    """
    all_studies: list[dict] = []
    page_token = None
    page = 0
    while len(all_studies) < max_records:
        params: dict = {"query.cond": condition, "pageSize": min(page_size, max_records - len(all_studies))}
        if status:
            params["filter.overallStatus"] = status
        if page_token:
            params["pageToken"] = page_token

        cache_name = f"{condition.lower().replace(' ', '_')}_{status or 'any'}_p{page}"
        payload = load_or_fetch_json(RAW_DIR, cache_name, BASE_URL, params, force_refresh=force_refresh)

        studies = payload.get("studies", [])
        if not studies:
            break
        all_studies.extend(studies)

        page_token = payload.get("nextPageToken")
        page += 1
        if not page_token:
            break

    return _flatten_studies(all_studies)


def _flatten_studies(studies: list[dict]) -> pd.DataFrame:
    rows = []
    for study in studies:
        protocol = study.get("protocolSection", {})
        ident = protocol.get("identificationModule", {})
        status_mod = protocol.get("statusModule", {})
        design = protocol.get("designModule", {})
        sponsor = protocol.get("sponsorCollaboratorsModule", {})
        conditions = protocol.get("conditionsModule", {})
        oversight = protocol.get("oversightModule", {})

        enrollment_info = design.get("enrollmentInfo", {})

        rows.append({
            "nct_id": ident.get("nctId"),
            "brief_title": ident.get("briefTitle"),
            "overall_status": status_mod.get("overallStatus"),
            "why_stopped": status_mod.get("whyStopped"),
            "start_date": status_mod.get("startDateStruct", {}).get("date"),
            "primary_completion_date": status_mod.get("primaryCompletionDateStruct", {}).get("date"),
            "completion_date": status_mod.get("completionDateStruct", {}).get("date"),
            "study_type": design.get("studyType"),
            "phases": ", ".join(design.get("phases", []) or []),
            "enrollment_count": enrollment_info.get("count"),
            "enrollment_type": enrollment_info.get("type"),
            "lead_sponsor": sponsor.get("leadSponsor", {}).get("name"),
            "lead_sponsor_class": sponsor.get("leadSponsor", {}).get("class"),
            "conditions": ", ".join(conditions.get("conditions", []) or []),
            "is_fda_regulated_drug": oversight.get("isFdaRegulatedDrug"),
            "is_fda_regulated_device": oversight.get("isFdaRegulatedDevice"),
        })
    return pd.DataFrame(rows)
