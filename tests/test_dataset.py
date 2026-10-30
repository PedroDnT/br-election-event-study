"""Offline tests: DOL roll, interval alignment, no look-ahead. No network."""
from datetime import date

import numpy as np
import pandas as pd
import pytest

from src import config, dataset, model


def _sessions(start, end):
    days = pd.bdate_range(start, end)
    return days[[(d.month, d.day) not in dataset.FIXED_HOLIDAYS for d in days]]


def _dol_frame(sessions, tickers_months, level=5000.0):
    rows = []
    for ticker, month in tickers_months:
        for i, d in enumerate(sessions):
            rows.append({"trade_date": d.date().isoformat(), "ticker": ticker,
                         "contract_month": month, "settlement_price": level + i + len(rows) % 7})
    return pd.DataFrame(rows)


CONTRACTS = [("DOLX26", "2026-11-01"), ("DOLZ26", "2026-12-01"), ("DOLF27", "2027-01-01")]


def test_front_does_not_change_when_later_sessions_load():
    """The roll date must not move when more sessions are appended (the EMBR3-era bug)."""
    short = _sessions("2026-10-01", "2026-10-30")   # before the first business day of November
    long = _sessions("2026-10-01", "2026-11-05")    # after it
    a = dataset._dol_front(_dol_frame(long, CONTRACTS), short)
    b = dataset._dol_front(_dol_frame(long, CONTRACTS), long)
    common = a.index.intersection(b.index)
    assert (a.loc[common, "front"] == b.loc[common, "front"]).all()


def test_roll_happens_three_sessions_before_first_business_day():
    s = _sessions("2026-10-01", "2026-11-10")
    f = dataset._dol_front(_dol_frame(s, CONTRACTS), s)["front"]
    first_bday = pd.Timestamp("2026-11-03")  # 01/11 Sunday, 02/11 holiday
    expiry_idx = s.searchsorted(first_bday)
    last_x = f[f == "DOLX26"].index.max()
    assert s.get_loc(last_x) == expiry_idx - config.DOL_ROLL_SESSIONS - 1
    assert f.iloc[-1] == "DOLZ26"


def test_roll_day_return_uses_one_contract_on_both_days():
    s = _sessions("2026-10-01", "2026-11-10")
    df = _dol_frame(s, CONTRACTS)
    f = dataset._dol_front(df, s)
    roll_day = f.index[f["front"] != f["front"].shift(1)][1]
    px = df.assign(trade_date=pd.to_datetime(df["trade_date"])).pivot_table(
        index="trade_date", columns="ticker", values="settlement_price")
    prev = s[s.get_loc(roll_day) - 1]
    assert f.at[roll_day, "prev_same"] == px.at[prev, f.at[roll_day, "front"]]


def _fake_raw(drop_factor_day=None):
    s = _sessions("2026-06-01", "2026-10-02")
    n = len(s)
    rng = np.random.default_rng(1)

    def di(level):
        return pd.DataFrame({"trade_date": s.strftime("%Y-%m-%d"), "settlement_rate": level + rng.normal(0, .05, n).cumsum(),
                             "open_px": level, "close_px": level})

    def fred(level):
        d = pd.DataFrame({"date": s.strftime("%Y-%m-%d"), "value": level + rng.normal(0, .05, n).cumsum()})
        return d.drop(index=drop_factor_day) if drop_factor_day is not None else d

    dol = _dol_frame(s, [("DOLX26", "2026-11-01"), ("DOLZ26", "2026-12-01")])
    ibov = pd.DataFrame({"trade_date": s.strftime("%Y-%m-%d"), "level": 100000 + rng.normal(0, 300, n).cumsum()})
    raw = {"DI1F29": di(12.0), "DI1F35": di(12.5), "DOL": dol, "IBOV": ibov,
           "UST2Y": fred(4.5), "UST10Y": fred(4.9), "SPX": fred(7000.0),
           "VIX": fred(18.0), "BRENT": fred(100.0), "USD_BROAD": fred(120.0)}
    return raw, s


def test_a_missing_factor_day_drops_the_session_for_every_series():
    raw, s = _fake_raw()
    all_m, _ = dataset.build(raw)
    raw2, _ = _fake_raw(drop_factor_day=40)
    gap_m, _ = dataset.build(raw2)
    missing = s[40]
    assert missing in all_m.index and missing not in gap_m.index
    # the change after the gap spans both days for assets and factors alike
    after = gap_m.index[gap_m.index.searchsorted(missing)]
    prev = s[s.get_loc(after) - 2]
    assert gap_m.at[after, "gap_days"] == (after - prev).days


def test_estimation_uses_nothing_after_the_end_date():
    raw, s = _fake_raw()
    m, _ = dataset.build(raw)
    end = s[70]
    res1, _ = model.fit(m, "DI1F29", config.CORE_FACTORS, end, 40)
    m2 = m.copy()
    m2.loc[m2.index > end, "DI1F29"] += 1000.0  # shock the future
    res2, _ = model.fit(m2, "DI1F29", config.CORE_FACTORS, end, 40)
    assert np.allclose(res1.params.values, res2.params.values)


def test_too_few_sessions_raises_instead_of_fitting():
    raw, _ = _fake_raw()
    m, _ = dataset.build(raw)
    with pytest.raises(ValueError):
        model.fit(m, "DI1F29", config.CORE_FACTORS, date(2026, 6, 15), 252)
