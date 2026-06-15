import pandas as pd

from src.risk_framework.risk_scoring import RiskScoringEngine


def test_score_row_weighted_average():
    engine = RiskScoringEngine(weights={"a": 1, "b": 1})
    score = engine.score_row({"a": 1.0, "b": 0.0})
    assert score == 0.5


def test_band_assignment():
    engine = RiskScoringEngine(weights={"a": 1})
    assert engine.band_for(0.1) == "Low"
    assert engine.band_for(0.3) == "Medium"
    assert engine.band_for(0.6) == "High"
    assert engine.band_for(1.0) == "Critical"


def test_score_dataframe_handles_missing_columns():
    engine = RiskScoringEngine(weights={"frequency": 2, "severity": 1})
    df = pd.DataFrame({"frequency": [1.0, 0.0, 0.5]})
    result = engine.score_dataframe(df)
    assert "risk_score" in result.columns
    assert "risk_band" in result.columns
    # severity missing entirely -> only frequency contributes
    assert result.loc[0, "risk_score"] > 0
