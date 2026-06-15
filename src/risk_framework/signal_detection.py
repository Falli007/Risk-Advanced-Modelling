"""Disproportionality analysis for pharmacovigilance-style signal detection.

Given counts of (drug of interest, event of interest) vs all other drug/event
combinations, computes the standard 2x2 contingency-table signal statistics:
PRR (Proportional Reporting Ratio), ROR (Reporting Odds Ratio), and chi-square.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import chi2_contingency


@dataclass
class SignalResult:
    drug: str
    event: str
    a: int  # reports with drug AND event
    b: int  # reports with drug, NOT event
    c: int  # reports with event, NOT drug
    d: int  # reports with neither
    prr: float
    prr_ci_low: float
    prr_ci_high: float
    ror: float
    ror_ci_low: float
    ror_ci_high: float
    chi_square: float
    p_value: float

    @property
    def meets_signal_threshold(self) -> bool:
        """Common pharmacovigilance heuristic: PRR >= 2, chi-square >= 4, a >= 3."""
        return self.prr >= 2 and self.chi_square >= 4 and self.a >= 3


def compute_signal(a: int, b: int, c: int, d: int, drug: str = "", event: str = "") -> SignalResult:
    """Compute PRR, ROR, and chi-square for a 2x2 table.

    a = drug & event, b = drug & not event, c = not drug & event, d = neither.
    """
    if min(a, b, c, d) < 0:
        raise ValueError("Counts must be non-negative")

    # 95% CI via log-transform standard error (Haldane-Anscombe correction for zero cells)
    has_zero_cell = 0 in (a, b, c, d)
    a_, b_, c_, d_ = ((x + 0.5 if has_zero_cell else x) for x in (a, b, c, d))

    prr = _safe_ratio(a_, a_ + b_, c_, c_ + d_)
    ror = _safe_ratio(a_, b_, c_, d_)

    prr_se = np.sqrt((1 / a_) - (1 / (a_ + b_)) + (1 / c_) - (1 / (c_ + d_)))
    ror_se = np.sqrt((1 / a_) + (1 / b_) + (1 / c_) + (1 / d_))

    prr_ci_low, prr_ci_high = _ci_from_log(prr, prr_se)
    ror_ci_low, ror_ci_high = _ci_from_log(ror, ror_se)

    table = np.array([[a, b], [c, d]])
    chi_sq, p_value, _, _ = chi2_contingency(table, correction=True)

    return SignalResult(
        drug=drug, event=event, a=a, b=b, c=c, d=d,
        prr=prr, prr_ci_low=prr_ci_low, prr_ci_high=prr_ci_high,
        ror=ror, ror_ci_low=ror_ci_low, ror_ci_high=ror_ci_high,
        chi_square=chi_sq, p_value=p_value,
    )


def _safe_ratio(a: int, a_plus_b: int, c: int, c_plus_d: int) -> float:
    if a_plus_b == 0 or c == 0 or c_plus_d == 0:
        return float("nan")
    return (a / a_plus_b) / (c / c_plus_d)


def _ci_from_log(point_estimate: float, log_se: float) -> tuple[float, float]:
    if point_estimate <= 0 or np.isnan(point_estimate) or log_se == 0:
        return (float("nan"), float("nan"))
    log_est = np.log(point_estimate)
    low = np.exp(log_est - 1.96 * log_se)
    high = np.exp(log_est + 1.96 * log_se)
    return (low, high)
