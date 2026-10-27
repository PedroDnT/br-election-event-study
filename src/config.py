"""Fixed study parameters. Change them here only, and say so in the results."""
from datetime import date

PRE_EVENT = date(2026, 10, 23)    # last close before the 25/10 runoff
D0 = date(2026, 10, 26)           # first session after the result
POST_DAYS = 3                     # D+1 .. D+3 for the reversal test

# Estimation ends on the last pre-event close (spec) and, as a robustness
# run, before the first round of 04/10 (campaign weeks left out).
EST_ENDS = {"spec": PRE_EVENT, "pre_first_round": date(2026, 9, 30)}
WINDOWS = (252, 126, 63)
MAIN_WINDOW = 252
HAC_LAGS = 5

HISTORY_START = date(2018, 1, 2)  # B3 Price Report starts here

# Assets. kind "rate": change in bp; kind "price": log return.
ASSETS = {
    "DI1F29": {"kind": "rate", "label": "DI Jan-2029 (B3 settlement)"},
    "DI1F35": {"kind": "rate", "label": "DI Jan-2035 (B3 settlement)"},
    "USDBRL": {"kind": "price", "label": "USD/BRL, DOL front settlement"},
    "IBOV":   {"kind": "price", "label": "Ibovespa level"},
    "NTNB35": {"kind": "rate", "label": "NTN-B 2035, Tesouro Direto buy rate (morning)"},
}

# The DOL front contract rolls this many sessions before its expiry
# (the first business day of the contract month).
DOL_ROLL_SESSIONS = 3

# FRED series. Core factors enter every model; extras are robustness only.
FRED = {
    "UST2Y": "DGS2", "UST10Y": "DGS10", "SPX": "SP500",
    "VIX": "VIXCLS", "BRENT": "DCOILBRENTEU", "USD_BROAD": "DTWEXBGS",
}
CORE_FACTORS = ("d_ust10y_bp", "d_slope_bp", "r_spx")
EXTRA_FACTORS = ("d_vix", "r_brent", "r_usd_broad")

TESOURO_CSV = (
    "https://www.tesourotransparente.gov.br/ckan/dataset/"
    "df56aa42-484a-4a59-8184-7676580c81e3/resource/"
    "796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv"
)
NTNB_TITLE = "Tesouro IPCA+ com Juros Semestrais"
NTNB_MATURITY = date(2035, 5, 15)
