"""Generic weighted risk-scoring engine.

Each module defines its own named risk factors (already normalised to 0-1) and
weights; this engine combines them into a single score and risk band, which
keeps the scoring approach consistent and explainable across modules.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

DEFAULT_BANDS = [
    (0.0, 0.25, "Low"),
    (0.25, 0.5, "Medium"),
    (0.5, 0.75, "High"),
    (0.75, 1.01, "Critical"),  # 1.01 so a perfect 1.0 score falls in the top band
]


@dataclass
class RiskScoringEngine:
    """Combine normalised risk factors (0-1) into a weighted score and band.

    `weights` maps factor name -> weight. Weights need not sum to 1; they are
    normalised automatically. `bands` is a list of (low_inclusive, high_exclusive,
    label) tuples covering [0, 1].
    """
    weights: dict[str, float]
    bands: list[tuple[float, float, str]] = field(default_factory=lambda: list(DEFAULT_BANDS))

    def __post_init__(self) -> None:
        total = sum(self.weights.values())
        if total <= 0:
            raise ValueError("weights must sum to a positive number")
        self._normalised_weights = {k: v / total for k, v in self.weights.items()}

    def score_row(self, factors: dict[str, float]) -> float:
        """Compute a weighted score for one record. Missing factors are treated
        as 0 (no contribution) but still divided by the full weight total, so
        missing data lowers the score rather than being imputed."""
        score = 0.0
        for name, weight in self._normalised_weights.items():
            value = factors.get(name)
            if value is None:
                continue
            score += weight * max(0.0, min(1.0, value))
        return round(score, 4)

    def band_for(self, score: float) -> str:
        for low, high, label in self.bands:
            if low <= score < high:
                return label
        return self.bands[-1][2]

    def score_dataframe(self, df: pd.DataFrame, score_col: str = "risk_score",
                         band_col: str = "risk_band") -> pd.DataFrame:
        """Score every row of `df` using its columns as factor values.

        Columns named in `weights` that are missing from `df` are treated as
        all-NaN (i.e. contribute 0 to every row's score)."""
        out = df.copy()
        factor_cols = list(self._normalised_weights.keys())
        for col in factor_cols:
            if col not in out.columns:
                out[col] = float("nan")

        out[score_col] = out[factor_cols].apply(
            lambda row: self.score_row(row.dropna().to_dict()), axis=1
        )
        out[band_col] = out[score_col].apply(self.band_for)
        return out
