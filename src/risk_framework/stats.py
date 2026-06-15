"""Hypothesis testing helpers for exploratory comparisons (e.g. comparing
recall rates between two manufacturers, or reaction rates between two drugs)."""
from __future__ import annotations

from dataclasses import dataclass

from scipy.stats import chi2_contingency, ttest_ind


@dataclass
class TestResult:
    test_name: str
    statistic: float
    p_value: float
    significant_at_05: bool


def two_proportion_chi_square(success_a: int, total_a: int, success_b: int, total_b: int) -> TestResult:
    """Chi-square test of independence for comparing two proportions
    (e.g. recall rate of Firm A vs Firm B)."""
    table = [
        [success_a, total_a - success_a],
        [success_b, total_b - success_b],
    ]
    stat, p_value, _, _ = chi2_contingency(table, correction=True)
    return TestResult("chi_square_2proportion", float(stat), float(p_value), p_value < 0.05)


def two_sample_ttest(sample_a, sample_b, equal_var: bool = False) -> TestResult:
    """Welch's t-test (default) comparing means of two samples."""
    stat, p_value = ttest_ind(sample_a, sample_b, equal_var=equal_var, nan_policy="omit")
    return TestResult("welch_ttest" if not equal_var else "students_ttest",
                       float(stat), float(p_value), p_value < 0.05)
