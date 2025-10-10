# src/dynamic_sarimax/model.py
from __future__ import annotations
from typing import Optional, Dict, Any
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from .config import SarimaxConfig
from .features import ExogLagTransformer
from .utils import check_monotone_index


class DynamicSarimax:
    """SARIMAX wrapper that refuses unsafe exogenous alignment."""

    def __init__(self, cfg: SarimaxConfig, lagger: Optional[ExogLagTransformer] = None):
        self.cfg = cfg
        self.lagger = lagger
        self._fit_res = None

    def fit(self, y: pd.Series, X: Optional[pd.DataFrame] = None) -> "DynamicSarimax":
        check_monotone_index(y, "y")
        exog = None
        y_use = y
        if self.lagger is not None:
            if X is None:
                raise ValueError("Exogenous X required when lagger is set")
            check_monotone_index(X, "X")
            if not X.index.equals(y.index):
                common = X.index.intersection(y.index)
                X = X.loc[common]
                y_use = y.loc[common]
            self.lagger.fit(X, y_use)
            X_lag = self.lagger.transform(X)
            mask = self.lagger.mask()
            exog = X_lag.loc[mask]
            y_use = y_use.loc[mask]
        trend = self.cfg.materialize_trend()
        self._fit_res = SARIMAX(
            y_use.values,
            order=self.cfg.order,
            seasonal_order=self.cfg.seasonal_order,
            exog=None if exog is None else exog.values,
            trend=trend,
            enforce_stationarity=self.cfg.enforce_stationarity,
            enforce_invertibility=self.cfg.enforce_invertibility,
        ).fit(disp=False)
        return self

    def forecast(
        self,
        steps: int,
        X_future: Optional[pd.DataFrame] = None,
        start_idx: Optional[int] = None,
    ) -> pd.Series:
        if self._fit_res is None:
            raise RuntimeError("Model not fit")
        if self.lagger is None:
            pred = self._fit_res.get_forecast(steps=steps)
            return pd.Series(pred.predicted_mean)
        # with exog: require future exog aligned via lagger
        if X_future is None or start_idx is None:
            raise ValueError(
                "X_future and start_idx required when using exogenous lagger"
            )
        block = self.lagger.future_block(X_future, start_idx=start_idx, steps=steps)
        pred = self._fit_res.get_forecast(steps=steps, exog=block.values)
        return pd.Series(pred.predicted_mean)

    def aic(self) -> float:
        if self._fit_res is None:
            raise RuntimeError("Model not fit")
        return float(self._fit_res.aic)

    def model_info(self) -> Dict[str, Any]:
        if self._fit_res is None:
            raise RuntimeError("Model not fit")
        return {
            "order": self.cfg.order,
            "seasonal_order": self.cfg.seasonal_order,
            "aic": float(self._fit_res.aic),
            "nobs": int(self._fit_res.nobs),
        }
