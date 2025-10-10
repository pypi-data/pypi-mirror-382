# src/dynamic_sarimax/features.py
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd
from .config import ExogLagSpec
from .utils import ensure_dataframe, check_monotone_index, safe_shift, finite_mask_df


@dataclass
class _Scaler:
    mean_: float | None = None
    std_: float | None = None

    def fit(self, s: pd.Series) -> None:
        self.mean_ = float(np.nanmean(s.values))
        sd = float(np.nanstd(s.values, ddof=1))
        self.std_ = 1.0 if (not np.isfinite(sd) or sd == 0.0) else sd

    def transform(self, s: pd.Series) -> pd.Series:
        if self.mean_ is None or self.std_ is None:
            raise RuntimeError("Scaler not fit")
        return (s - self.mean_) / self.std_


class ExogLagTransformer:
    """Safe lag + train-only scaling with strict alignment."""

    def __init__(self, spec: ExogLagSpec):
        if spec.delay < 0:
            raise ValueError("delay must be >= 0")
        self.spec = spec
        self._scalers: dict[str, _Scaler] = {}
        self._mask: pd.Series | None = None
        self._columns: list[str] | None = None
        self._fitted_index: pd.Index | None = None

    def _lag_all(self, Xdf: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame(
            {col: safe_shift(Xdf[col], self.spec.delay) for col in Xdf.columns},
            index=Xdf.index,
        )

    def fit(self, X: pd.Series | pd.DataFrame, y: pd.Series) -> "ExogLagTransformer":
        Xdf = ensure_dataframe(X, name="X")
        if Xdf is None:
            raise ValueError("Exogenous X required for ExogLagTransformer.fit")
        check_monotone_index(Xdf, "X")
        check_monotone_index(y, "y")
        if not Xdf.index.equals(y.index):
            common = Xdf.index.intersection(y.index)
            Xdf = Xdf.loc[common]
            y = y.loc[common]
        Xlag = self._lag_all(Xdf)
        mask = finite_mask_df(Xlag)
        self._mask = mask
        self._columns = list(Xdf.columns)
        self._fitted_index = Xdf.index

        if self.spec.scale:
            for col in Xlag.columns:
                sc = _Scaler()
                sc.fit(Xlag.loc[mask, col])
                self._scalers[col] = sc
        return self

    def transform(self, X: pd.Series | pd.DataFrame) -> pd.DataFrame:
        if self._columns is None or self._mask is None:
            raise RuntimeError("Transformer not fit")
        Xdf = ensure_dataframe(X, name="X")
        if list(Xdf.columns) != self._columns:
            Xdf = Xdf.copy()
            Xdf.columns = self._columns
        Xlag = self._lag_all(Xdf)
        if self.spec.scale:
            for col, sc in self._scalers.items():
                Xlag[col] = sc.transform(Xlag[col])
        return Xlag

    def mask(self) -> pd.Series:
        if self._mask is None:
            raise RuntimeError("Transformer not fit")
        return self._mask.copy()

    def trim_target(self, y: pd.Series) -> pd.Series:
        if self._mask is None:
            raise RuntimeError("Transformer not fit")
        return y.loc[self._mask]

    def future_block(
        self, X_full: pd.DataFrame, start_idx: int, steps: int
    ) -> pd.DataFrame:
        """Return lagged+scaled exog for indices [start_idx, start_idx+steps-1]."""
        if self._columns is None:
            raise RuntimeError("Transformer not fit")
        Xdf = ensure_dataframe(X_full, name="X_full")
        if Xdf.shape[1] != len(self._columns):
            raise ValueError(
                f"Future exogenous column count mismatch. Expected {len(self._columns)}, got {Xdf.shape[1]}"
            )
        if list(Xdf.columns) != self._columns:
            Xdf = Xdf.copy()
            Xdf.columns = self._columns
        Xlag = self._lag_all(Xdf)
        if self.spec.scale:
            for col, sc in self._scalers.items():
                Xlag[col] = sc.transform(Xlag[col])
        block = Xlag.iloc[start_idx : start_idx + steps]
        if not np.all(np.isfinite(block.values)):
            raise ValueError(
                "future_block contains NaN/Inf - not enough history for lagged exog at these horizons"
            )
        return block
