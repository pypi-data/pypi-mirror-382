# 🧭 dynamic-sarimax

[![PyPI Version](https://img.shields.io/pypi/v/dynamic-sarimax.svg)](https://pypi.org/project/dynamic-sarimax/)
[![Python Versions](https://img.shields.io/pypi/pyversions/dynamic-sarimax.svg)](https://pypi.org/project/dynamic-sarimax/)
[![License](https://img.shields.io/github/license/NefariousNiru/dynamic-sarimax.svg)](https://github.com/NefariousNiru/dynamic-sarimax/blob/main/LICENSE)
[![Tests](https://github.com/NefariousNiru/dynamic-sarimax/actions/workflows/ci.yml/badge.svg)](https://github.com/NefariousNiru/dynamic-sarimax/actions)

---

**Delay-aware SARIMAX wrapper** that fixes the common pitfalls of `statsmodels.SARIMAX`:
proper lag alignment for exogenous variables, train-only scaling, and safe rolling-origin
evaluation — all built-in.

---

## ✨ Why this exists

Plain SARIMAX requires you to hand-align exogenous regressors (e.g. lagged mobility, weather),
risking leakage or off-by-one bugs.  
`dynamic-sarimax` makes this safe by construction.

**Key guarantees**

- ✅ For delay `b`, trains only on valid pairs `(y_t, x_{t-b})` — never imputes missing lags.  
- ✅ Scalers are fit *only on training windows* during CV.  
- ✅ Forecasting refuses to run if required future exogenous rows are missing.  
- ✅ Rolling-origin evaluation and AIC-based delay selection included.

---

## 🚀 Quickstart

```bash
# create venv and install deps
poetry install

# run example (uses example CSV under examples/)
poetry run python examples/ili_quickstart.py
````

```python
from dynamic_sarimax import (
    SarimaxConfig,
    select_delay_by_aic,
    rolling_evaluate,
)

cfg = SarimaxConfig(order=(5,0,2), seasonal_order=(1,0,0,52))
best_b, best_aic = select_delay_by_aic(y_train, x_train, delays=[1,2,3], cfg=cfg)
print(f"Best lag = {best_b}  |  AIC = {best_aic:.2f}")

res = rolling_evaluate(y, x, cfg, delay=best_b, horizons=24, train_frac=0.8)
print(res.head())
```

---

## 📈 Example output

```
Chosen delay b (on 80% train): 2 | Train AIC: 1234.56

Per-horizon scores (rolling validation on last 20%):
 h  n_origins     MSE  sMAPE
 1         52   0.103   8.12
 2         51   0.109   8.54
 ...

Average MSE   = 0.124
Average sMAPE = 8.77 %
```

---

## ⚙️ Installation

```bash
pip install dynamic-sarimax
# or
poetry add dynamic-sarimax
```

Python ≥ 3.10, tested on 3.10–3.12.

---

## 🧩 Components

| Module          | Purpose                                        |
| :-------------- | :--------------------------------------------- |
| `config.py`     | Parameter dataclasses for SARIMAX and lag spec |
| `features.py`   | Safe lagging + scaling transformer             |
| `model.py`      | Wrapper around `statsmodels.SARIMAX`           |
| `selection.py`  | Delay (lag) selection via AIC                  |
| `evaluation.py` | Rolling-origin cross-validation                |
| `metrics.py`    | MSE & sMAPE helpers                            |

---

## 🧪 Testing

```bash
poetry run pytest -q
```


## 🪞 Project links

* [Contributing guide](./CONTRIBUTING.md)
* [Licence](./LICENSE)
* [Issues](https://github.com/NefariousNiru/dynamic-sarimax/issues)
* [PyPI package](https://pypi.org/project/dynamic-sarimax/)

---

## 📜 License

Apache-2.0 © 2025 Nirupom Bose Roy
Contributions welcome!
