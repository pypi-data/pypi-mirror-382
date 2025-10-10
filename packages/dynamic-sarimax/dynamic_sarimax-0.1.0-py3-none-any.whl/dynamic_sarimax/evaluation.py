# src/dynamic_sarimax/evaluation.py
from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Optional
from .config import SarimaxConfig, ExogLagSpec
from .features import ExogLagTransformer
from .model import DynamicSarimax
from .metrics import mse, smape


def rolling_evaluate(
    y: pd.Series,
    X: Optional[pd.Series | pd.DataFrame],
    cfg: SarimaxConfig,
    delay: Optional[int],
    horizons: int,
    train_frac: float = 0.8,
    min_train: int = 30,
) -> pd.DataFrame:
    N = len(y)
    train_end0 = int(np.floor(train_frac * N))
    test_start = train_end0
    last_origin = N - horizons
    if last_origin < test_start:
        raise ValueError("horizons too large relative to series length")

    rows = []
    Xdf = (
        None
        if X is None
        else (
            X
            if isinstance(X, pd.DataFrame)
            else X.to_frame(name=getattr(X, "name", "exog"))
        )
    )

    for o in range(test_start, last_origin + 1):
        y_tr = y.iloc[:o]
        X_tr = None if Xdf is None else Xdf.iloc[:o]
        if delay is None:
            model = DynamicSarimax(cfg=cfg, lagger=None)
            model.fit(y_tr, None)
            steps = horizons
            yhat = model.forecast(steps=steps)
            ytrue = y.iloc[o : o + steps].reset_index(drop=True)
            for h in range(steps):
                rows.append(
                    {
                        "origin": o,
                        "h": h + 1,
                        "y_true": float(ytrue.iloc[h]),
                        "y_hat": float(yhat.iloc[h]),
                    }
                )
            continue

        lagger = ExogLagTransformer(ExogLagSpec(delay=delay, scale=True))
        model = DynamicSarimax(cfg=cfg, lagger=lagger)
        model.fit(y_tr, X_tr)
        if model._fit_res.nobs < min_train:
            continue

        X_full = Xdf
        yhat = model.forecast(steps=horizons, X_future=X_full, start_idx=o)
        ytrue = y.iloc[o : o + horizons].reset_index(drop=True)
        for h in range(horizons):
            rows.append(
                {
                    "origin": o,
                    "h": h + 1,
                    "y_true": float(ytrue.iloc[h]),
                    "y_hat": float(yhat.iloc[h]),
                }
            )

    out = pd.DataFrame(rows)
    if out.empty:
        raise RuntimeError("No evaluations produced - check inputs")

    agg = (
        out.groupby("h", as_index=False)
        .apply(
            lambda g: pd.Series(
                {
                    "n_origins": len(g),
                    "MSE": mse(g["y_true"].values, g["y_hat"].values),
                    "sMAPE": smape(g["y_true"].values, g["y_hat"].values),
                }
            ),
            include_groups=False,
        )
        .reset_index(drop=True)
    )

    macro_MSE = agg["MSE"].mean()
    macro_sMAPE = agg["sMAPE"].mean()

    agg.attrs["macro_MSE"] = float(macro_MSE)
    agg.attrs["macro_sMAPE"] = float(macro_sMAPE)
    return agg
