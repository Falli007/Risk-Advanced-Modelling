"""Fuzzy name matching for compliance/sanctions screening."""
from __future__ import annotations

import pandas as pd
from rapidfuzz import fuzz, process


def screen_names(candidate_names: list[str], watchlist_names: pd.Series,
                  score_threshold: float = 80.0, limit: int = 3) -> pd.DataFrame:
    """For each candidate name, find the best matches in `watchlist_names`.

    Matching is case-insensitive (sanctions lists are typically all-uppercase
    while a client's vendor master data rarely is), but the original casing of
    `matched_name` is preserved in the output for readability.

    Returns one row per (candidate, match) pair with columns:
    candidate_name, matched_name, score. Only matches scoring >= score_threshold
    are returned; candidates with no qualifying match get a row with NaN match
    fields and score 0, so every candidate appears at least once (useful for
    audit trails of "screened, no hit").
    """
    choices = watchlist_names.dropna().unique().tolist()
    choices_lower = {c.lower(): c for c in choices}
    rows = []
    for name in candidate_names:
        matches = process.extract(name.lower(), list(choices_lower.keys()), scorer=fuzz.token_sort_ratio, limit=limit)
        qualifying = [m for m in matches if m[1] >= score_threshold]
        if not qualifying:
            rows.append({"candidate_name": name, "matched_name": None, "score": 0.0})
            continue
        for matched_lower, score, _ in qualifying:
            rows.append({"candidate_name": name, "matched_name": choices_lower[matched_lower], "score": float(score)})
    return pd.DataFrame(rows)
