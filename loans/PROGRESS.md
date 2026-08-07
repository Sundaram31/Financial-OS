# Debt & Loan Tracker — Progress

## What this is
Standalone tool (index.html), same design system as rest of Financial OS.
First real implementation of the "Financial Events extraction" vision --
scoped to loans specifically because EMI/prepayment is 100% derivable from
bank statement data alone (unlike capital gains, which needs broker/CAMS
source data for security-level detail).

## Built (2026-08-07)
- Loan CRUD: lender, type, principal, rate, EMI.
- Bank-statement paste/file-upload with pattern-based EMI/prepayment
  detection -- reuses the validated classifier approach from AIS
  Reconciliation session work (98.7% accuracy on real data, description-text
  only, no reliance on a pre-existing category column).
- Amortization-based payoff projection from outstanding balance + EMI.
- Export/Import JSON, own storage key (loans_data_v1), shared theme.

## Known limitations, stated plainly in the UI
- Payoff projection doesn't re-amortize after each prepayment -- directional
  estimate, not exact.
- For Sec 24(b) interest deduction, use the actual bank interest certificate,
  not this tool's estimate.
- EMI vs prepayment classification during bulk-paste is heuristic (smaller
  recurring figure = EMI, larger lump sum = prepayment) -- always shown for
  review, never auto-committed without the user seeing the detected list.

## Queued next (Financial Events vision, remaining pieces)
1. FD/RD lifecycle tracker (open, contributions, maturity date/amount) --
   also 100% bank-derivable, same classifier pattern.
2. Investment cash-flow ledger (SIP totals by fund house/broker) -- feeds
   Net Worth Dashboard's Investments category instead of manual entry.
3. Insurance premium ledger -- premiums from bank data, maturity/lapse date
   needs one-time policy document capture (not derivable from bank alone).
4. Capital gains explicitly stays OUT of self-computation -- bank data can
   only flag that a sale event happened, not compute the gain (no security/
   quantity/price in bank transaction descriptions).
