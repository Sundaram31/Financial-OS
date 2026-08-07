# Insurance Tracker — Progress

## What this is
Standalone tool (index.html), same design system as the rest of Financial OS.
Not just a policy inventory — every policy is checked against real
mis-selling patterns and flagged in plain language, per the "financial
adviser" persona (protect from mis-sold insurance, not just record it).

## Built (2026-08-03)
- Policy CRUD: type, insurer, premium, cover amount, rider awareness,
  commission awareness.
- Automatic flags per policy:
  - ULIP/Endowment: investment-insurance bundling warning
  - Term Life: cover-vs-income adequacy check (10x floor heuristic)
  - Unknown riders: flagged for the user to check the actual document
  - Commission unawareness: flagged as a mis-selling risk signal, not a verdict
- Coverage summary: total term cover vs income multiple.
- Export/Import JSON, own storage key (insurance_data_v1), shared theme
  key with rest of Financial OS.

## Why this got built now
A real Max Life Insurance premium (Rs 38,500, March 2026) was found in the
user's bank statement during AIS reconciliation and never followed up —
this module exists so a payment like that gets evaluated, not just logged.

## Known gaps
- No integration with 80C/80D deduction modules in ITRGenie yet (premium
  paid here should inform those, not be re-entered).
- Health insurance coverage-adequacy check not built yet (only term life
  has a real adequacy heuristic so far).
- No claim-ratio / insurer-reputation data source (would need external
  IRDAI data, out of scope for offline tool).
