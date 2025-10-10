# src/dynamic_sarimax/metrics.py
from __future__ import annotations
import numpy as np


def mse(y_true, y_pred) -> float:
    y = np.asarray(y_true, dtype=float)
    yhat = np.asarray(y_pred, dtype=float)
    return float(np.mean((y - yhat) ** 2))


def smape(y_true, y_pred) -> float:
    y = np.asarray(y_true, dtype=float)
    yhat = np.asarray(y_pred, dtype=float)
    denom = np.abs(y) + np.abs(yhat)
    denom = np.where(denom == 0, 1.0, denom)
    return float(np.mean(200.0 * np.abs(y - yhat) / denom))
