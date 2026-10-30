"""Download raw inputs into data/raw/ (git-ignored). Nothing here derives data.

Sources: SILO-BZ read API through its public SDK (B3 and BACEN data),
FRED CSV (US factors), Tesouro Transparente CSV (NTN-B). A failed download
raises; no fallback values are ever written.
"""
import io
import json
from datetime import date
from pathlib import Path

import pandas as pd
import requests
from silo_client import SiloClient

from . import config

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
MONTH_CODES = "FGHJKMNQUVXZ"


def _cached(name: str, refresh: bool, loader):
    path = RAW / name
    if path.exists() and not refresh:
        return pd.read_csv(path)
    df = loader()
    if df.empty:
        raise RuntimeError(f"{name}: source returned no rows")
    RAW.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df


def _years(start: date, end: date):
    for y in range(start.year, end.year + 1):
        yield max(start, date(y, 1, 1)), min(end, date(y, 12, 31))


def _silo_series(silo, fn, *args, start, end):
    rows = []
    for a, b in _years(start, end):
        rows += fn(*args, start=a.isoformat(), end=b.isoformat())
    return pd.DataFrame(rows)


def silo_contract(silo, ticker, start, end, refresh):
    return _cached(f"silo_{ticker}.csv", refresh,
                   lambda: _silo_series(silo, silo.future_series, ticker, start=start, end=end))


def silo_pre(silo, tenor, start, end, refresh):
    return _cached(f"silo_PRE{tenor}.csv", refresh,
                   lambda: _silo_series(silo, silo.curve_history, "PRE", tenor, start=start, end=end))


def silo_ibov(silo, start, end, refresh):
    return _cached("silo_IBOV.csv", refresh,
                   lambda: _silo_series(silo, silo.index_history_all, "IBOV", start=start, end=end))


def silo_bova11(silo, start, end, refresh):
    def load():
        rows = silo.rpc("quote_history", p_ticker="BOVA11", p_from=start.isoformat(),
                        p_to=end.isoformat(), p_fields=["open", "close"], p_after="")
        return pd.DataFrame(rows)
    return _cached("silo_BOVA11.csv", refresh, load)


def dol_tickers(start: date, end: date):
    """Every monthly DOL contract that can be the front one in [start, end]."""
    months = pd.date_range(date(start.year, start.month, 1), end + pd.DateOffset(months=2), freq="MS")
    return [(f"DOL{MONTH_CODES[m.month - 1]}{m.year % 100:02d}", m.date()) for m in months]


def silo_dol(silo, start, end, refresh):
    def load():
        frames = []
        for ticker, month in dol_tickers(start, end):
            # A contract trades for at most a few years before its month.
            a = max(start, date(month.year - 3, 1, 1))
            b = min(end, month)
            if a > b:
                continue
            df = _silo_series(silo, silo.future_series, ticker, start=a, end=b)
            if not df.empty:
                frames.append(df)
        return pd.concat(frames, ignore_index=True)
    return _cached("silo_DOL.csv", refresh, load)


def fred(series_id: str, start: date, refresh: bool):
    def load():
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd={start.isoformat()}"
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = ["date", "value"]
        return df
    return _cached(f"fred_{series_id}.csv", refresh, load)


def tesouro(refresh: bool):
    def load():
        r = requests.get(config.TESOURO_CSV, timeout=300)
        r.raise_for_status()
        return pd.read_csv(io.StringIO(r.content.decode("latin-1")), sep=";", decimal=",")
    return _cached("tesouro_direto.csv", refresh, load)


def fetch_all(end: date, refresh: bool = False, with_tesouro: bool = True):
    start = config.HISTORY_START
    silo = SiloClient()
    out = {
        "DI1F29": silo_contract(silo, "DI1F29", start, end, refresh),
        "DI1F35": silo_contract(silo, "DI1F35", start, end, refresh),
        "DOL": silo_dol(silo, start, end, refresh),
        "IBOV": silo_ibov(silo, start, end, refresh),
        "BOVA11": silo_bova11(silo, date(2026, 9, 1), end, refresh),
    }
    for name, tenor in config.PRE_TENORS.items():
        out[name] = silo_pre(silo, tenor, start, end, refresh)
    for name, sid in config.FRED.items():
        out[name] = fred(sid, start, refresh)
    if with_tesouro:
        try:
            out["TESOURO"] = tesouro(refresh)
        except requests.HTTPError as exc:
            # NTN-B stays pending; the run records why instead of guessing.
            out["TESOURO_ERROR"] = str(exc)
    meta = {"fetched_through": end.isoformat(),
            "rows": {k: int(len(v)) for k, v in out.items() if isinstance(v, pd.DataFrame)}}
    (RAW / "fetch_meta.json").write_text(json.dumps(meta, indent=2))
    return out
