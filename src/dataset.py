"""Build the aligned daily table of asset moves and factor moves.

Rules:
- A session is kept only when every core input has a value on it, and each
  change is taken between two kept sessions, so asset and factor changes
  always cover the same calendar interval.
- DI and NTN-B: change in bp. FX, Ibovespa, S&P 500, Brent, dollar: log return.
- DI changes come from one contract per day (B3's own prev_settlement_rate).
- The DOL front return on day t uses one contract for both t and t-1.
"""
import numpy as np
import pandas as pd

from . import config


def _di(df: pd.DataFrame) -> pd.DataFrame:
    df = df.assign(trade_date=pd.to_datetime(df["trade_date"])).set_index("trade_date").sort_index()
    return pd.DataFrame({
        "level": df["settlement_rate"],
        "open": df["open_px"],
        "close": df["close_px"],
    })


def _dol_front(dol: pd.DataFrame, sessions: pd.DatetimeIndex) -> pd.DataFrame:
    """Settlement of the front DOL contract, rolled DOL_ROLL_SESSIONS before expiry."""
    dol = dol.assign(trade_date=pd.to_datetime(dol["trade_date"]),
                     contract_month=pd.to_datetime(dol["contract_month"]))
    px = dol.pivot_table(index="trade_date", columns="ticker", values="settlement_price")
    months = dol.drop_duplicates("ticker").set_index("ticker")["contract_month"].sort_values()
    # Expiry = first session in the contract month (B3: first business day).
    # A contract whose month starts after the last session has not expired.
    pos = {t: (sessions.searchsorted(m) if m <= sessions[-1] else np.inf) for t, m in months.items()}
    rows = []
    for i, day in enumerate(sessions):
        live = [t for t, p in pos.items() if i < p - config.DOL_ROLL_SESSIONS]
        if not live:
            continue
        front = min(live, key=lambda t: months[t])
        prev = sessions[i - 1] if i > 0 else None
        cur_px = px.at[day, front] if day in px.index else np.nan
        prev_px = px.at[prev, front] if prev is not None and prev in px.index else np.nan
        rows.append({"trade_date": day, "front": front, "level": cur_px, "prev_same": prev_px})
    out = pd.DataFrame(rows).set_index("trade_date")
    return out


def _fred(df: pd.DataFrame) -> pd.Series:
    s = pd.to_numeric(df["value"], errors="coerce")
    s.index = pd.to_datetime(df["date"])
    return s.dropna()


def _ntnb(tesouro: pd.DataFrame) -> pd.Series:
    t = tesouro.copy()
    t.columns = [c.strip() for c in t.columns]
    t = t[(t["Tipo Titulo"].str.strip() == config.NTNB_TITLE)
          & (pd.to_datetime(t["Data Vencimento"], dayfirst=True).dt.date == config.NTNB_MATURITY)]
    s = pd.Series(pd.to_numeric(t["Taxa Compra Manha"], errors="coerce").values,
                  index=pd.to_datetime(t["Data Base"], dayfirst=True)).sort_index()
    return s[~s.index.duplicated()].dropna()


def build(raw: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (moves, levels). moves: one row per kept session."""
    di29, di35 = _di(raw["DI1F29"]), _di(raw["DI1F35"])
    ibov = raw["IBOV"].assign(trade_date=pd.to_datetime(raw["IBOV"]["trade_date"]))
    ibov = ibov.set_index("trade_date")["level"].sort_index()
    f = {k: _fred(raw[k]) for k in config.FRED}

    core = pd.concat({"DI1F29": di29["level"], "DI1F35": di35["level"], "IBOV": ibov,
                      "UST2Y": f["UST2Y"], "UST10Y": f["UST10Y"], "SPX": f["SPX"]},
                     axis=1).dropna()
    sessions = core.index
    dol = _dol_front(raw["DOL"], sessions).reindex(sessions)
    core["USDBRL"] = dol["level"]
    core = core.dropna(subset=["USDBRL"])
    sessions = core.index
    dol = dol.reindex(sessions)

    levels = core.copy()
    for k in ("VIX", "BRENT", "USD_BROAD"):
        levels[k] = f[k].reindex(sessions)
    if "TESOURO" in raw:
        levels["NTNB35"] = _ntnb(raw["TESOURO"]).reindex(sessions)

    m = pd.DataFrame(index=sessions)
    m["DI1F29"] = levels["DI1F29"].diff() * 100
    m["DI1F35"] = levels["DI1F35"].diff() * 100
    # Same contract on both days: a roll never shows up as a return.
    m["USDBRL"] = np.log(dol["level"] / dol["prev_same"])
    m["IBOV"] = np.log(levels["IBOV"]).diff()
    if "NTNB35" in levels:
        m["NTNB35"] = levels["NTNB35"].diff() * 100
    m["d_ust10y_bp"] = levels["UST10Y"].diff() * 100
    m["d_slope_bp"] = (levels["UST10Y"] - levels["UST2Y"]).diff() * 100
    m["r_spx"] = np.log(levels["SPX"]).diff()
    m["d_vix"] = levels["VIX"].diff()
    m["r_brent"] = np.log(levels["BRENT"]).diff()
    m["r_usd_broad"] = np.log(levels["USD_BROAD"]).diff()
    # Gap in days covered by each change, for the audit trail.
    m["gap_days"] = pd.Series(sessions, index=sessions).diff().dt.days
    levels["dol_front"] = dol["front"]
    return m.iloc[1:], levels
