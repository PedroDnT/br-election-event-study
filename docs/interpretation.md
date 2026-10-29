# Interpretation and limits

Runs of 2026-10-27 (D0) and 2026-10-29 (D+1, cross-section). Numbers are in
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

## Reversal (D+1 measured, D+2 and D+3 partial)

Run of 2026-10-29. The model needs US data, and FRED has UST yields only
through 27/10, so the modelled reversal covers D+1 only.

- **D+1 (27/10), core model:** rates gave back a small part. DI1F29 −43 bp
  residual (16% of the D0 residual), DI1F35 11%, NTN-B 11%, USD/BRL 14%.
  Ibovespa did not reverse: its residual grew by 6%.
- **28/10, observed only (no model yet):** DI1F29 +6 bp, DI1F35 +22 bp,
  USD/BRL +0.2%, Ibovespa −2.7%. The rate reversal stopped and equities kept
  falling.
- Treasury buybacks were reported for these days (`docs/event_log.md`). The
  D+1 fall in rates can come from the buybacks, not from a change of view.

## Exporters versus domestic stocks (no model)

From the 23/10 close to D0, B3's domestic indices fell about twice as much as
the Ibovespa: consumption −30.6%, real estate −34.4%, small caps −31.4%. The
4 exporters rose: Suzano +9.6%, Embraer +8.5%, Vale +3.9%, Klabin +3.2%. In
USD terms the exporters were roughly flat (−4.8% to +1.7%), so their BRL gain
is about the fall of the real. Banco do Brasil (−34.7%) fell with the domestic
group; Petrobras (−8.5%) fell less than the Ibovespa. Through 28/10 the split
widened: domestic indices −34% to −41%, Ibovespa −18.2%.

A reading consistent with this: the market priced a higher domestic risk and
rates path, not a fall of Brazilian assets in general. The groups are a stated
choice (`src/crosssection.py`), not a full sector study.

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
- **Small factor set.** Brent joined as a robustness factor on 29/10 and
  changes the σ multiples by less than 1. The broad dollar index is not yet
  published for D0. DXY, CDS and EWZ have no free licensed source. An
  emerging-market peer control (MXN, ZAR) is the next useful addition.
- **DI1F29 on 23/10:** the 23/10 row has a settlement rate of 12.642%, and
  B3's previous-rate field on the 26/10 row says 12.640%. The study uses the
  rows as published (difference 0.2 bp).
