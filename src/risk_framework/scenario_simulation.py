"""Monte Carlo scenario simulation utilities."""
from __future__ import annotations

import numpy as np
import pandas as pd


def simulate_enrollment_completion(
    target_enrollment: int,
    current_enrollment: int,
    monthly_rate_mean: float,
    monthly_rate_std: float,
    n_simulations: int = 10_000,
    max_months: int = 60,
    random_state: int | None = 42,
) -> pd.DataFrame:
    """Monte Carlo simulation of months-to-complete-enrollment for a clinical trial.

    Each simulation draws a monthly enrollment rate per month from
    Normal(monthly_rate_mean, monthly_rate_std), clipped at 0, and accumulates
    until `target_enrollment` is reached or `max_months` is exceeded.

    Returns a DataFrame with one row per simulation: columns
    `months_to_complete` (NaN if not completed within max_months) and
    `completed` (bool).
    """
    if monthly_rate_mean <= 0:
        raise ValueError("monthly_rate_mean must be positive")

    rng = np.random.default_rng(random_state)
    remaining = max(0, target_enrollment - current_enrollment)

    rates = rng.normal(monthly_rate_mean, monthly_rate_std, size=(n_simulations, max_months))
    rates = np.clip(rates, 0, None)
    cumulative = np.cumsum(rates, axis=1)

    completed_mask = cumulative >= remaining
    months_to_complete = np.full(n_simulations, np.nan)
    any_completed = completed_mask.any(axis=1)
    first_month = completed_mask.argmax(axis=1)
    months_to_complete[any_completed] = first_month[any_completed] + 1

    return pd.DataFrame({
        "months_to_complete": months_to_complete,
        "completed": ~np.isnan(months_to_complete),
    })


def summarise_simulation(results: pd.DataFrame, target_date_horizon_months: int | None = None) -> dict:
    """Summarise a scenario simulation: completion probability, percentiles,
    and (optionally) probability of completing within `target_date_horizon_months`."""
    completed = results.loc[results["completed"], "months_to_complete"]
    summary = {
        "n_simulations": len(results),
        "p_complete_within_horizon": float(results["completed"].mean()),
        "median_months_to_complete": float(completed.median()) if not completed.empty else None,
        "p10_months": float(completed.quantile(0.10)) if not completed.empty else None,
        "p90_months": float(completed.quantile(0.90)) if not completed.empty else None,
    }
    if target_date_horizon_months is not None and not completed.empty:
        summary["p_complete_by_target"] = float((completed <= target_date_horizon_months).mean())
    return summary
