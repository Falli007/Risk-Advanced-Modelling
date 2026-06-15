import math

from src.risk_framework.signal_detection import compute_signal


def test_no_disproportionality_gives_prr_near_one():
    # Same rate of event in both drug and non-drug groups -> PRR ~ 1
    result = compute_signal(a=10, b=90, c=100, d=900, drug="DrugX", event="EventY")
    assert math.isclose(result.prr, 1.0, rel_tol=0.05)
    assert not result.meets_signal_threshold


def test_strong_disproportionality_is_flagged():
    # Event much more common with the drug than without
    result = compute_signal(a=50, b=50, c=10, d=990, drug="DrugX", event="EventY")
    assert result.prr > 2
    assert result.chi_square > 4
    assert result.meets_signal_threshold


def test_zero_cell_handled_without_error():
    result = compute_signal(a=5, b=0, c=10, d=100, drug="DrugX", event="EventY")
    assert result.ror > 0
    assert not math.isnan(result.ror_ci_low)
