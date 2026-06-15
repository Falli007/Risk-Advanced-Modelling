"""Generic anomaly detection helpers used across modules."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


def zscore_anomalies(series: pd.Series, threshold: float = 3.0) -> pd.Series:
    """Return a boolean Series flagging values more than `threshold` standard
    deviations from the mean. NaNs are never flagged."""
    s = series.astype(float)
    mean, std = s.mean(), s.std(ddof=0)
    if std == 0 or np.isnan(std):
        return pd.Series(False, index=series.index)
    z = (s - mean) / std
    return z.abs() > threshold


def rolling_volume_anomalies(df: pd.DataFrame, date_col: str, freq: str = "M",
                              threshold: float = 3.0) -> pd.DataFrame:
    """Aggregate record counts per period and flag volume spikes via z-score.

    Returns a DataFrame indexed by period with columns: count, zscore, is_anomaly.
    """
    dates = pd.to_datetime(df[date_col], errors="coerce")
    counts = dates.dt.to_period(freq).value_counts().sort_index()
    counts.index = counts.index.to_timestamp()
    result = counts.to_frame("count")
    result["is_anomaly"] = zscore_anomalies(result["count"], threshold=threshold)
    mean, std = result["count"].mean(), result["count"].std(ddof=0)
    result["zscore"] = (result["count"] - mean) / std if std else 0.0
    return result


def isolation_forest_anomalies(df: pd.DataFrame, feature_cols: list[str],
                                contamination: float = 0.05,
                                random_state: int = 42) -> pd.Series:
    """Fit an Isolation Forest on `feature_cols` and return a boolean Series
    flagging the most anomalous rows (proportion ~= `contamination`).

    Rows with missing values in any feature column are never flagged (treated
    as not-anomalous by default since they're excluded from fitting/scoring).
    """
    data = df[feature_cols].copy()
    valid_mask = data.notna().all(axis=1)

    flags = pd.Series(False, index=df.index)
    if valid_mask.sum() < 10:
        return flags

    model = IsolationForest(contamination=contamination, random_state=random_state)
    predictions = model.fit_predict(data.loc[valid_mask])
    flags.loc[valid_mask] = predictions == -1
    return flags
