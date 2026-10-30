"""Factor baseline, event residuals and reversal. Descriptive, not causal.

For asset i: y_i,t = a_i + b_i' X_t + e_i,t, estimated only on sessions up to
the estimation end. The D0 residual is observed minus predicted with the
frozen betas and the D0 factor values. Its scale is measured three ways:
the in-sample residual sd, the sd of one-step-ahead forecast errors, and its
rank among all one-step-ahead errors since the history starts.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

from . import config


def fit(moves: pd.DataFrame, asset: str, factors, end, window: int):
    d = moves.loc[:pd.Timestamp(end), [asset, *factors]].dropna().tail(window)
    if len(d) < window:
        raise ValueError(f"{asset}: {len(d)} sessions before {end}, need {window}")
    X = sm.add_constant(d[list(factors)])
    res = sm.OLS(d[asset], X).fit(cov_type="HAC", cov_kwds={"maxlags": config.HAC_LAGS})
    return res, d


def vif(d: pd.DataFrame, factors) -> dict:
    X = sm.add_constant(d[list(factors)]).values
    return {f: float(variance_inflation_factor(X, i + 1)) for i, f in enumerate(factors)}


def oos_errors(moves: pd.DataFrame, asset: str, factors, end, window: int) -> pd.Series:
    """One-step-ahead errors: fit on `window` sessions to t-1, predict t."""
    d = moves.loc[:pd.Timestamp(end), [asset, *factors]].dropna()
    y = d[asset].values
    X = np.column_stack([np.ones(len(d)), d[list(factors)].values])
    out = {}
    for t in range(window, len(d)):
        b, *_ = np.linalg.lstsq(X[t - window:t], y[t - window:t], rcond=None)
        out[d.index[t]] = y[t] - X[t] @ b
    return pd.Series(out)


def event_rows(moves, asset, factors, res, days):
    rows = []
    for day in days:
        if day not in moves.index or moves.loc[day, [asset, *factors]].isna().any():
            continue
        x = np.r_[1.0, moves.loc[day, list(factors)].values.astype(float)]
        pred = float(x @ res.params.values)
        obs = float(moves.loc[day, asset])
        rows.append({"date": day.date(), "observed": obs, "predicted": pred, "residual": obs - pred})
    return rows


def run(moves: pd.DataFrame, assets, factor_sets: dict, flags: dict | None = None) -> dict:
    """factor_sets: name -> tuple of factor columns. flags: date -> text."""
    flags = flags or {}
    d0 = pd.Timestamp(config.D0)
    post = [d for d in moves.index if d > d0][: config.POST_DAYS]
    event, coefs, stability, errors = [], [], [], {}
    for asset in assets:
        if asset not in moves:
            continue
        for fs_name, factors in factor_sets.items():
            for end_name, end in config.EST_ENDS.items():
                for w in config.WINDOWS:
                    try:
                        res, d = fit(moves, asset, factors, end, w)
                    except ValueError:
                        continue
                    for f in res.params.index:
                        coefs.append({"asset": asset, "factors": fs_name, "est_end": end_name,
                                      "window": w, "term": f, "beta": res.params[f],
                                      "se_hac": res.bse[f], "t": res.tvalues[f]})
                    stability.append({"asset": asset, "factors": fs_name, "est_end": end_name,
                                      "window": w, "n": int(res.nobs), "r2": res.rsquared,
                                      **{f"vif_{k}": v for k, v in vif(d, factors).items()}})
                    if w != config.MAIN_WINDOW and not (fs_name == "core"):
                        continue
                    key = (asset, fs_name, end_name, w)
                    e = oos_errors(moves, asset, factors, end, w)
                    errors[key] = e
                    sd_in = float(np.sqrt(res.mse_resid))
                    sd_oos = float(e.tail(w).std())
                    rows = event_rows(moves, asset, factors, res, [d0, *post])
                    if not rows or rows[0]["date"] != d0.date():
                        continue
                    r0 = rows[0]["residual"]
                    cum = 0.0
                    for k, r in enumerate(rows):
                        cum += r["residual"]
                        rank = int((e.abs() >= abs(r["residual"])).sum()) + 1
                        event.append({
                            "asset": asset, "factors": fs_name, "est_end": end_name, "window": w,
                            "day": f"D+{k}" if k else "D0", **r,
                            "cum_residual": cum, "sd_in": sd_in, "sd_oos": sd_oos,
                            "resid_over_sd_oos": r["residual"] / sd_oos,
                            "abs_rank_vs_oos_history": rank, "oos_history_n": int(len(e)),
                            "oos_history_start": e.index.min().date() if len(e) else None,
                            "reversal_share": (-(cum - r0) / r0) if k else np.nan,
                            "r2": res.rsquared,
                            "largest_prior_abs": float(e.abs().max()),
                            "x_largest_prior": abs(r["residual"]) / float(e.abs().max()),
                            "intervention": flags.get(r["date"], ""),
                        })
    return {"event": pd.DataFrame(event), "coefs": pd.DataFrame(coefs),
            "stability": pd.DataFrame(stability), "errors": errors}


def two_day_check(levels: pd.DataFrame, assets, factors=config.CORE_FACTORS, window: int = config.MAIN_WINDOW):
    """Clock-matched check: 2-session changes ending on config.TWO_DAY_END.

    Tesouro Direto morning rates and B3 settlements sit at different times
    within a day, but both are measured at the same two dates here (23/10 and
    27/10), so the span is the same. It also spans D+1: Treasury buybacks and
    the fiscal statement of 27/10 are inside it. Observations overlap, so the
    HAC errors use the lags set in config.
    """
    m = pd.DataFrame(index=levels.index)
    for a in assets:
        if a in levels:
            m[a] = levels[a].diff(2) * 100
    m["d_ust10y_bp"] = levels["UST10Y"].diff(2) * 100
    m["d_slope_bp"] = (levels["UST10Y"] - levels["UST2Y"]).diff(2) * 100
    m["r_spx"] = np.log(levels["SPX"]).diff(2)
    end = pd.Timestamp(config.TWO_DAY_END)
    rows = []
    for a in [x for x in assets if x in m]:
        try:
            res, _ = fit(m, a, factors, config.PRE_EVENT, window)
        except ValueError:
            continue
        e = oos_errors(m, a, factors, config.PRE_EVENT, window)
        ev = event_rows(m, a, factors, res, [end])
        if not ev:
            continue
        r = ev[0]
        rows.append({"asset": a, "from": str(pd.Timestamp(config.PRE_EVENT).date()),
                     "to": str(end.date()), **r, "sd_oos": float(e.tail(window).std()),
                     "resid_over_sd_oos": r["residual"] / float(e.tail(window).std()),
                     "x_largest_prior": abs(r["residual"]) / float(e.abs().max())})
    return pd.DataFrame(rows)
