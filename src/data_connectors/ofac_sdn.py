"""Connector for the US Treasury OFAC Specially Designated Nationals (SDN) list.

Source: https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV
(no API key required; the endpoint requires a browser-like User-Agent header).
"""
from __future__ import annotations

from io import StringIO
from pathlib import Path

import pandas as pd

from src.utils.http_cache import load_or_fetch_text

URL = "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV"
RAW_DIR = Path("data/raw/ofac")

# The SDN.CSV has no header row; this is the documented column order.
COLUMNS = [
    "ent_num", "sdn_name", "sdn_type", "program", "title", "call_sign",
    "vess_type", "tonnage", "grt", "vess_flag", "vess_owner", "remarks",
]


def fetch_sdn_list(force_refresh: bool = False) -> pd.DataFrame:
    """Fetch the full OFAC SDN list as a DataFrame."""
    text = load_or_fetch_text(RAW_DIR, "sdn", URL, ext="csv", force_refresh=force_refresh)
    df = pd.read_csv(
        StringIO(text), header=None, names=COLUMNS, quotechar='"',
        skipinitialspace=True, on_bad_lines="skip",
    )
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
    df = df.replace("-0-", pd.NA)
    return df
