# src/dynamic_sarimax/selection.py
from __future__ import annotations
from typing import Sequence, Tuple
import pandas as pd
from .config import SarimaxConfig, ExogLagSpec
from .features import ExogLagTransformer
from .model import DynamicSarimax


def select_delay_by_aic(
    y_train: pd.Series,
    X_train: pd.Series | pd.DataFrame,
    delays: Sequence[int],
    cfg: SarimaxConfig,
    min_train: int = 30,
) -> Tuple[int, float]:
    best = (None, float("inf"))
    for b in delays:
        lagger = ExogLagTransformer(ExogLagSpec(delay=b, scale=True))
        model = DynamicSarimax(cfg=cfg, lagger=lagger)
        # fit will trim via lagger; if effective sample too small, skip
        model.fit(y_train, X_train)
        nobs = model._fit_res.nobs  # safe here
        if nobs < min_train:
            continue
        aic = model.aic()
        if aic < best[1]:
            best = (b, aic)
    if best[0] is None:
        raise RuntimeError(
            "AIC selection failed - not enough effective training data for given delays"
        )
    return best  # (best_delay, best_aic)
