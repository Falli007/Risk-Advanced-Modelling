import pandas as pd

from src.risk_framework.anomaly_detection import zscore_anomalies, isolation_forest_anomalies


def test_zscore_flags_outlier():
    series = pd.Series([10, 11, 9, 10, 11, 9, 100])
    flags = zscore_anomalies(series, threshold=2.0)
    assert flags.iloc[-1]
    assert not flags.iloc[0]


def test_zscore_constant_series_no_flags():
    series = pd.Series([5, 5, 5, 5])
    flags = zscore_anomalies(series)
    assert not flags.any()


def test_isolation_forest_flags_some_rows():
    df = pd.DataFrame({
        "x": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 50],
        "y": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 50],
    })
    flags = isolation_forest_anomalies(df, ["x", "y"], contamination=0.1)
    assert flags.iloc[-1]
