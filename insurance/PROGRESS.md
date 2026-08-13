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

## Updated 2026-08-11 — App-wide font-size/contrast/consistency pass
Part of an exhaustive, whole-app pass (every module touched the same day) responding to direct
user feedback that font sizing is hard to see and the color scheme needs improvement everywhere.
This module's own income-adequacy `.tag` was one of two specific instances `synthesis/PROGRESS.md`
had already flagged as a known, unfixed sub-13px gap (the other being the Debt & Loan card's tag)
— both close out with this pass.

**8 sub-13px `font-size` declarations raised to 13px**: `.brand .sub` 11px->13px,
`.panel-header .eyebrow` 11px->13px, `.field label` 11px->13px, `.btn` 12px->13px,
`.btn.small` 11px->13px, `table.day-table th` 11.5px->13px, `.helptext` 12.5px->13px,
`.tag` (the income-adequacy pill on term-life policies, and the mis-selling flag tags) 10px->13px.

**Cross-module consistency**: `--bg/--panel/--panel-2/--line/--text/--muted/--gold/--gold-dim/
--green/--rust` hex values (both themes) diffed byte-for-byte against every other module —
already identical, no drift found.

**Contrast**: `--muted` against `--bg`/`--panel`/`--panel-2` computed at 6.5–7.4:1 dark, 4.9–5.7:1
light — already passes WCAG AA (4.5:1) in both themes.

**Tested with real headless-Chromium (Playwright)**: full DOM text-node sweep at 375px and 1280px,
both themes — 0 nodes under 13px, 0 console errors. Functional regression: "+ Add a policy" flow
re-verified (new policy card renders with editable fields) — no JS logic touched, CSS values only.
