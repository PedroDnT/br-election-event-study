# Evaluation (2026-10-27, before implementation)

The full page with the data inventory: https://claude.ai/artifact/4fNauuXJFYk9DG48ZeVDXK
(private to the owner). This file keeps the decisions and the points the code
follows.

## Decisions by the owner

- Separate repository; SILO-BZ pipelines stay unchanged. The study reads
  SILO-BZ through its public read SDK.
- NTN-B 2035 comes from Tesouro Direto (Tesouro Transparente CSV), labelled as
  such, never as ANBIMA.
- Main estimation ends 23/10 (spec); 30/09 (before the first round) is the
  robustness run.

## Data inventory (state on 2026-10-27)

| Series | Source | Last value | Status |
|---|---|---|---|
| DI1F29, DI1F35 | SILO-BZ, B3 Price Report, from 2018 (F35 from 2020) | 26/10 | ready |
| DOL / WDO | SILO-BZ, B3 Price Report, from 2018 | 26/10 | ready |
| Ibovespa | SILO-BZ, B3 index statistics | 26/10 (a 27/10 row exists before DI; the calendar rule leaves it out) | ready |
| PTAX | SILO-BZ, BACEN | 26/10 | midday fix, cross-check only |
| DPL real curve | SILO-BZ, B3 TaxaSwap | 26/10 | not NTN-B, not used |
| NTN-B 2035 | Tesouro Transparente | 26/10 | ready (morning rate) |
| UST 2Y, 10Y, S&P 500, VIX | FRED | 26/10 | ready |
| Brent | FRED (EIA) | 20/10 | D0 pending |
| Broad dollar (DXY proxy) | FRED (H.10, weekly release) | 23/10 | D0 pending |
| DXY, CDS Brazil 5Y, EWZ | none free and licensed | — | out of scope |

## Method points the code follows

1. The residual is a surprise against 23/10 prices, never an election effect.
2. A z-score saturates on this event, so the code reports the residual, the
   residual over the sd of one-step-ahead errors, and the rank against the
   full error history.
3. Factors are the UST 10Y level and the 10Y−2Y slope (not 2Y and 10Y
   together) plus the S&P 500. Measured VIF is 1.0 to 1.4.
4. FX is the DOL front settlement, not PTAX. A lag-1 factor run checks the
   clock gap.
5. Each daily change uses one contract on both days (DI fixed contracts; DOL
   rolled 3 sessions before expiry).
6. Treasury actions and other same-day news are logged in `event_log.md`.
7. Raw third-party data is not committed.

## Open extensions

D+1 to D+3 reversal (rerun when the sessions land), EM peer control (MXN,
ZAR), Brent and broad dollar when published, exporters versus domestic
equities.

## Status of the evaluation points (2026-10-30)

| Point | Status |
|---|---|
| Event date is not the information date | Done: 30/09 robustness run, residual called a surprise |
| z-score saturates | Done: sd multiple, multiple of the largest earlier error, history length |
| Collinear factors | Done: 10Y level + slope + S&P 500, VIF 1.0 to 1.4 |
| Closes are not synchronous | Done for FX and for NTN-B (lag-1 run, clock-matched 2-day check) |
| In-sample sd too small | Done: out-of-sample errors |
| Same-day confounders | Done: sourced `interventions.csv`, flags in the event table. Finding: the fiscal statement was 27/10, not D0 |
| No EM peer control | Open: MXN and ZAR wait for Fed H.10 (about 02/11) |
| Contract roll and ageing | Done: one contract per change, PRE 720 and 2520 vertices, roll tests |
| Data license | Done: S&P 500 and VIX not committed |
