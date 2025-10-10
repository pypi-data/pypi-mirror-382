# src/dynamic_sarimax/utils.py
from __future__ import annotations
import numpy as np
import pandas as pd


def ensure_series(
    x: pd.Series | pd.DataFrame | np.ndarray, name: str = "x"
) -> pd.Series:
    if isinstance(x, pd.Series):
        return x
    if isinstance(x, pd.DataFrame):
        if x.shape[1] != 1:
            raise ValueError(f"{name} must be 1-D when passed here; got {x.shape}")
        return x.iloc[:, 0]
    if isinstance(x, np.ndarray):
        if x.ndim != 1:
            raise ValueError(f"{name} must be 1-D array; got shape {x.shape}")
        return pd.Series(x)
    raise TypeError(f"Unsupported type for {name}: {type(x)}")


def ensure_dataframe(
    X: pd.Series | pd.DataFrame | None, name: str = "X"
) -> pd.DataFrame | None:
    if X is None:
        return None
    if isinstance(X, pd.DataFrame):
        return X
    if isinstance(X, pd.Series):
        col = X.name if (X.name is not None and X.name != 0) else "exog"
        return X.to_frame(name=col)
    raise TypeError(f"Unsupported type for {name}: {type(X)}")


def check_monotone_index(obj: pd.Series | pd.DataFrame, name: str) -> None:
    idx = obj.index
    if not idx.is_monotonic_increasing:
        raise ValueError(f"{name} index must be monotone increasing")
    if idx.has_duplicates:
        raise ValueError(f"{name} index has duplicates")


def safe_shift(s: pd.Series, b: int) -> pd.Series:
    if b < 0:
        raise ValueError("delay must be >= 0")
    return s.shift(b)


def finite_mask_df(df: pd.DataFrame) -> pd.Series:
    m = np.all(np.isfinite(df.values), axis=1)
    return pd.Series(m, index=df.index)
