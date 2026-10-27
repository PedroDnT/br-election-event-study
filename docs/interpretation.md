# Interpretation and limits

Run of 2026-10-27, data through 26/10 (D0). Numbers are in
`results/RESULTS.md`. This page does not claim a cause.

## What the data shows

1. **Global factors explain almost nothing of D0.** US yields barely moved
   (ΔUST10Y 0 bp) and the S&P 500 rose 0.7%. The predicted moves are a few bp
   or tenths of a percent. The residual is therefore almost the whole move for
   every asset.
2. **Every D0 residual is the largest of its history.** For every asset,
   window and estimation end, no earlier one-step-ahead error is as large
   (histories start between 2020-04 and 2021-02). The rank alone does not
   separate the assets.
3. **Testable statement.** In units of the out-of-sample sd, the ranking is
   DI (F29 +19.2, F35 +19.0) > NTN-B 2035 (+15.9) > Ibovespa (−13.6) > USD/BRL
   (+11.9) in the main run. Rates > NTN-B > equity > FX holds in all 8
   specifications. Only the order of F29 and F35 changes.
4. **D0 undid the first-round move and went further.** On 05/10, the first
   session after the first round, every asset moved the other way: DI1F29
   −116 bp, Ibovespa +7.4%, USD/BRL −4.5%. That day is the largest or second largest
   earlier residual for each asset. From 05/10 to 23/10 the assets held
   that move. D0 then reversed it with 1.6 to 2.3 times its size. A reading
   consistent with this: the market priced one outcome after the first round
   and the runoff gave the other. The data alone does not prove this reading.
5. **Most of the shock was in the price at the open.** DI1F29 opened +239 bp
   and settled +258 bp. USD/BRL opened +8.1% and settled +7.9%. BOVA11 opened
   −17.7% and closed −15.7%. The first trades are not synchronized prices, so
   treat this as description.

## Reversal (pending)

D+1 to D+3 (27/10 to 29/10) are not loaded yet. Rerun `python run.py --refresh`
when they are. Before you read a reversal, check `docs/event_log.md`: Treasury
buybacks on those days push rates down for a reason other than a change of
view.

## Limits

- **Surprise, not effect.** The residual is the move against the 23/10
  prices. Polls had priced part of the outcome already.
- **Same-day news.** The fiscal statement and the Treasury actions are inside
  the D0 residual.
- **sd from a stressed window.** The window to 23/10 holds the first-round
  day (−116 bp). This raises the sd, so the spec run gives smaller σ multiples
  than the 30/09 run. Both are shown.
- **Different clocks.** DI and DOL settle in an afternoon window, Ibovespa
  closes about 17:00, the S&P 500 at 17:00 BRT, NTN-B (Tesouro Direto) is a
  morning rate. The lag-1 run changes nothing material.
- **NTN-B is Tesouro Direto,** a retail morning rate in steps of 1 bp. It is
  not the ANBIMA indicative rate. On 26/10 its morning rate already includes
  the shock.
- **Small factor set.** Brent and the broad dollar index are not yet
  published for D0. DXY, CDS and EWZ have no free licensed source. An
  emerging-market peer control (MXN, ZAR) is the next useful addition.
- **DI1F29 on 23/10:** the 23/10 row has a settlement rate of 12.642%, and
  B3's previous-rate field on the 26/10 row says 12.640%. The study uses the
  rows as published (difference 0.2 bp).
