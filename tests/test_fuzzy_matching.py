import pandas as pd

from src.risk_framework.fuzzy_matching import screen_names


def test_case_insensitive_match():
    watchlist = pd.Series(["ANGLO-CARIBBEAN CO., LTD.", "BANCO NACIONAL DE CUBA"])
    result = screen_names(["Anglo Caribbean Co Ltd"], watchlist, score_threshold=75)
    assert result.iloc[0]["matched_name"] == "ANGLO-CARIBBEAN CO., LTD."
    assert result.iloc[0]["score"] > 75


def test_no_match_returns_none_row():
    watchlist = pd.Series(["ANGLO-CARIBBEAN CO., LTD."])
    result = screen_names(["Acme Logistics Group Inc"], watchlist, score_threshold=75)
    assert result.iloc[0]["matched_name"] is None
    assert result.iloc[0]["score"] == 0.0
