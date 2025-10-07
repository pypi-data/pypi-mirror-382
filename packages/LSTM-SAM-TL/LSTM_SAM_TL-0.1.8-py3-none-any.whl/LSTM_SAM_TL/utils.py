from __future__ import annotations

from typing import Tuple
import numpy as np
from sklearn.preprocessing import MinMaxScaler


def normalize_xy(X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, MinMaxScaler, MinMaxScaler]:
    """
    MinMax-scale X and y to [0,1].
    Returns (X_scaled, y_scaled, x_scaler, y_scaler)
    """
    x_scaler = MinMaxScaler()
    y_scaler = MinMaxScaler(feature_range=(0, 1))
    Xn = x_scaler.fit_transform(X)
    yn = y_scaler.fit_transform(y.reshape(-1, 1))
    return Xn, yn, x_scaler, y_scaler


def create_rnn_dataset(X: np.ndarray, y: np.ndarray, lookback: int):
    """
    Turn (X, y) into overlapping windows for RNNs.

    X_out shape: (N - lookback, lookback, n_features)
    y_out shape: (N - lookback, 1)
    """
    Xr, yr = [], []
    for i in range(len(X) - lookback):
        Xr.append(X[i:i + lookback])
        yr.append(y[i + lookback])
    return np.array(Xr), np.array(yr)
