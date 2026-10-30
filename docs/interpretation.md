# Interpretation and limits

Runs of 2026-10-27 (D0), 2026-10-29 (D+1, cross-section) and 2026-10-30 (D+2, checks). Numbers are in
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
3. **Which asset deviated most depends on the yardstick.** In units of the
   out-of-sample sd, rates lead: DI F29 +19.2, DI F35 +19.0, B3 PRE 720 and
   2520 days +19.3 and +19.1, NTN-B 2035 +15.9, Ibovespa −13.6, USD/BRL
   +11.9. This order holds in all 6 estimation specifications and in the
   VIX, lag-1 and Brent runs. As a multiple of the largest earlier error since
   2021-02, equities lead: Ibovespa 2.2x, DI F29 2.1x, NTN-B 2.0x, DI F35
   1.9x, USD/BRL 1.4x. So there is no single "largest deviation": rates by σ,
   equities by the size of the earlier worst day. USD/BRL is the smallest
   under both. Constant-tenor PRE vertices give the same answer as the
   fixed DI contracts, so contract ageing is not driving the DI result.
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

## Reversal (D+1 and D+2 measured; D+3 pending)

Run of 2026-10-30, core model. SILO-BZ has 29/10, but FRED has UST and S&P 500
only through 28/10. A session needs every core input, so the model stops at
D+2. D+3 waits for FRED.

| Asset | D+1 residual | D+2 residual | Share of D0 residual reversed by D+2 |
|---|---|---|---|
| DI F29 | −42.7 bp | +9.9 bp | 12% |
| DI F35 | −28.7 bp | +25.3 bp | 1% |
| USD/BRL | −1.13% | +0.51% | 7% |
| Ibovespa | −0.94% | −2.99% | −25% (it fell further) |
| NTN-B 2035 | −14.6 bp | −4.8 bp | 15% |

- Rates gave back 11 to 17% on D+1 and some of it came back on D+2. The
  reversal is small and not stable.
- Ibovespa did not reverse at all; its cumulative residual grew from −15.5%
  to −19.4%.
- D+1 (27/10) is flagged: the Treasury cancelled the LFT auction and announced
  a new NTN-B buyback, and the Finance Minister announced the bill to target
  the centre of the fiscal goal (`docs/interventions.csv`). A fall in rates
  on that day has at least two possible causes besides a change of view.
- No intervention is recorded for 28/10, which means none was found, not that
  none happened.

## Exporters versus domestic stocks (no model)

From the 23/10 close to D0, B3's domestic indices fell about twice as much as
the Ibovespa: consumption −30.6%, real estate −34.4%, small caps −31.4%. The
4 exporters rose: Suzano +9.6%, Embraer +8.5%, Vale +3.9%, Klabin +3.2%. In
USD terms the exporters were roughly flat (−4.8% to +1.7%), so their BRL gain
is about the fall of the real. Banco do Brasil (−34.7%) fell with the domestic
group; Petrobras (−8.5%) fell less than the Ibovespa. Through 29/10 (D+3) the split
widened: domestic indices −37% to −45%, Ibovespa −19.2%. This table needs no
factor model, so it covers D+3 already.

A reading consistent with this: the market priced a higher domestic risk and
rates path, not a fall of Brazilian assets in general. The groups are a stated
choice (`src/crosssection.py`), not a full sector study.

## Limits

- **Surprise, not effect.** The residual is the move against the 23/10
  prices. Polls had priced part of the outcome already.
- **Same-day news.** D0 contains the B3 circuit breaker, the first Treasury
  buybacks (about R$ 14.8 bn) and the cancelled auctions. The fiscal
  statement is not in D0: it came on 27/10, in D+1. All dates are sourced in
  `docs/interventions.csv`. A flag marks a day that also contains the event,
  it does not measure it.
- **sd from a stressed window.** The window to 23/10 holds the first-round
  day (−116 bp). This raises the sd, so the spec run gives smaller σ multiples
  than the 30/09 run. Both are shown.
- **Different clocks.** DI and DOL settle in an afternoon window, Ibovespa
  closes about 17:00, the S&P 500 at 17:00 BRT, NTN-B (Tesouro Direto) is a
  morning rate. The lag-1 run changes nothing material.
- **NTN-B is Tesouro Direto,** a retail morning rate in steps of 1 bp. It is
  not the ANBIMA indicative rate. On 26/10 its morning rate already includes
  the opening shock but not the rest of the day. The clock-matched check
  measures every asset and factor from 23/10 to 27/10: NTN-B +112 bp
  (+10.5σ), DI F29 +212 bp (+11.5σ), DI F35 +216 bp (+12.4σ). The order
  rates above NTN-B holds on equal dates. The NTN-B move is about half the DI
  move. That span includes D+1, so it carries the buybacks and the fiscal
  statement.
- **Log returns.** Ibovespa fell 13.88% in simple terms on 26/10
  (Poder360) and −14.95% in log terms, which this repo reports. The
  intraday low was about −17% (Folha).
- **Small factor set.** Brent is a robustness factor and changes the σ
  multiples by less than 1. The broad dollar index is not yet
  published for D0. DXY, CDS and EWZ have no free licensed source. An
  emerging-market peer control (MXN, ZAR) is the next useful addition.
- **DI1F29 on 23/10:** the 23/10 row has a settlement rate of 12.642%, and
  B3's previous-rate field on the 26/10 row says 12.640%. The study uses the
  rows as published (difference 0.2 bp).
