"""Exporters versus domestic stocks around D0. Description only, no model.

The groups are a fixed, stated choice made before looking at the returns:
- exporters: privately controlled companies with mostly USD revenue;
- domestic: B3 indices of consumption, real estate and small caps;
- state-controlled: kept apart, because the election bears on them directly.
A stock return uses close_adj (split- and bonus-adjusted, no dividends).
"""
from datetime import date

import numpy as np
import pandas as pd
from silo_client import SiloClient

from . import config
from .fetch import _cached

GROUPS = {
    "exporter": ["VALE3", "SUZB3", "KLBN11", "EMBJ3"],
    "state_controlled": ["PETR4", "BBAS3"],
}
DOMESTIC_INDICES = ["ICON", "IMOB", "SMLL"]


def fetch(end: date, refresh: bool) -> dict:
    silo = SiloClient()
    start = date(2026, 9, 1)
    out = {}
    for tickers in GROUPS.values():
        for t in tickers:
            out[t] = _cached(f"silo_q_{t}.csv", refresh, lambda t=t: pd.DataFrame(
                silo.rpc("quote_history", p_ticker=t, p_from=start.isoformat(),
                         p_to=end.isoformat(), p_after="")))
    for ix in DOMESTIC_INDICES:
        out[ix] = _cached(f"silo_ix_{ix}.csv", refresh, lambda ix=ix: pd.DataFrame(
            silo.index_history_all(ix, start=start.isoformat(), end=end.isoformat())))
    return out


def table(raw: dict, ibov: pd.Series, usdbrl: pd.Series, sessions: pd.DatetimeIndex) -> pd.DataFrame:
    """Log returns from the 23/10 close to D0 and to each later session held.

    usdbrl is a roll-safe FX index (exp of cumulative DOL front log returns).
    """
    pre = pd.Timestamp(config.PRE_EVENT)
    days = [d for d in sessions if d >= pd.Timestamp(config.D0)][: 1 + config.POST_DAYS]
    rows = []
    series = {}
    for name, df in raw.items():
        col = "close_adj" if "close_adj" in df else "level"
        s = pd.Series(df[col].values, index=pd.to_datetime(df["trade_date"])).sort_index()
        group = next((g for g, ts in GROUPS.items() if name in ts), "domestic")
        series[name] = (group, s)
    series["IBOV"] = ("benchmark", ibov)
    for name, (group, s) in series.items():
        s = s.reindex(sessions)
        for i, d in enumerate(days):
            lag = days[i - 1] if i else pre
            r_day = np.log(s[d] / s[lag])
            r_cum = np.log(s[d] / s[pre])
            fx_cum = np.log(usdbrl[d] / usdbrl[pre])
            rows.append({"name": name, "group": group, "day": f"D+{i}" if i else "D0", "date": d.date(),
                         "ret_day": r_day, "ret_cum": r_cum,
                         "ret_cum_vs_ibov": r_cum - np.log(ibov[d] / ibov[pre]),
                         "ret_cum_usd": r_cum - fx_cum})
    return pd.DataFrame(rows)
