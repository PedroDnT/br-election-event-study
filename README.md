# Brazil 2026 runoff: event study

A reproducible study of how Brazilian assets moved around the result of the
25/10/2026 presidential runoff. Last pre-event close: 23/10. First session
after the result (D0): 26/10.

**The residual is not a causal effect of the election.** It is the part of a
move that a small set of global factors does not account for. Other news on
the same days (the Finance Minister's fiscal statement, Treasury auction
cancellations and buybacks) is inside it too. See `docs/interpretation.md`.

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run.py --refresh          # downloads every input, then runs
python run.py                    # reuses data/raw/ (git-ignored)
```

Outputs go to `results/`: `RESULTS.md` (the tables), `event_table.csv`,
`coefficients.csv`, `stability.csv`, `opening_gap.csv`,
`largest_prior_residuals.csv`, `cross_section.csv` (exporters versus
domestic stocks, no model), `inputs_moves.csv` (the aligned daily moves the
model used) and one chart per asset in `results/charts/`.

## Method in one screen

- Assets: DI1F29, DI1F35 (B3 settlement rate, bp), USD/BRL (DOL front
  settlement, log return, rolled 3 sessions before expiry, both days from one
  contract), Ibovespa (log return), NTN-B 2035 (Tesouro Direto morning buy
  rate, bp).
- Factors (FRED): ΔUST10Y and Δ(UST10Y − UST2Y) in bp, S&P 500 log return.
  VIX, Brent and lag-1 factors are robustness runs. The broad dollar index
  joins when its D0 value is published.
- A session is kept only when every core input has a value, so asset and factor
  changes cover the same interval.
- OLS with intercept and HAC (5 lags) errors, fitted only on data up to the
  estimation end: 23/10 (spec) and 30/09 (before the first round, robustness),
  on 252, 126 and 63 sessions.
- Scale of a residual: sd of one-step-ahead forecast errors over the window,
  and the rank of its absolute value among all one-step-ahead errors since
  2021-02.
- D+1 to D+3: same frozen betas; reversal share = minus the cumulative
  post-D0 residual over the D0 residual.

## Sources and licenses

| Data | Source | Note |
|---|---|---|
| DI1, DOL futures, Ibovespa, BOVA11 | SILO-BZ read API (B3 public files) | Check B3 terms before you republish raw values |
| NTN-B 2035 | Tesouro Transparente, Tesouro Direto prices and rates | Public data. Retail morning rates, not ANBIMA indicative rates |
| UST 2Y, 10Y, Brent, broad dollar | FRED (Fed H.15, EIA, Fed H.10) | Public domain |
| S&P 500, VIX | FRED | Copyright S&P DJI and Cboe: do not publish raw values |

Raw files stay in `data/raw/`, which git ignores. `results/inputs_moves.csv`
holds daily changes only, and leaves out the S&P 500 and VIX columns because
this repository is public. `python run.py --refresh` rebuilds them.

All times are Brasília (UTC-3).
