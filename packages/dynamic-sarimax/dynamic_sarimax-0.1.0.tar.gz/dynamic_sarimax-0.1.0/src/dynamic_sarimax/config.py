# src/dynamic_sarimax/config.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class SarimaxConfig:
    order: Tuple[int, int, int]
    seasonal_order: Tuple[int, int, int, int]
    trend: str | None = "auto"  # "auto" -> "c" if d=D=0 else "n"
    enforce_stationarity: bool = False
    enforce_invertibility: bool = False

    def materialize_trend(self) -> str:
        d = self.order[1]
        D = self.seasonal_order[1]
        if self.trend == "auto":
            return "c" if (d == 0 and D == 0) else "n"
        return "n" if self.trend is None else self.trend


@dataclass(frozen=True)
class ExogLagSpec:
    delay: int  # b >= 0
    scale: bool = True
