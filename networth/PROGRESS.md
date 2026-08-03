# Net Worth Dashboard — Progress

## What this is
Standalone single-file tool (`index.html`), same visual design system as
ITRGenie (shared CSS variables, same theme toggle — deliberately reads/writes
the same `itrgenie_theme` localStorage key so theme choice is consistent
across the whole Financial OS rather than per-tool).

## Built (2026-08-03)
- Five asset categories (Investments, Foreign Assets, Property, Business,
  Other) + Liabilities — paste-import rows, same pattern as ITRGenie modules.
- Live net worth summary with a category breakdown bar.
- Snapshot history — manually saved date-stamped totals, with a hand-drawn
  SVG sparkline trend (no chart library, keeps zero-dependency rule).
- Export/Import JSON for backup, independent of ITRGenie's own export.

## Updated 2026-08-03
- Added CSV/TXT file-upload as a second input mode alongside paste, on every
  category card — reuses the same parser, not a separate code path.
- Reprioritized per user feedback: Goals module now exists and is meant to
  be filled in *before* finalizing Net Worth's Investments category, since
  goal-tagged investments are a more meaningful unit than a flat total.

## Known gap — the actual point of this module isn't finished
This currently requires manual entry for Investments, same as everything
else. The real value unlocks once **Portfolio Tracker** is migrated into
this repo and can feed the Investments category automatically — per
`MASTER_ROADMAP.md`'s data contract: `{category, label, value, asOf}[]`.

There's ambiguity to resolve first: earlier project notes referenced a
"dark-terminal, Twelve Data, technical indicators" Portfolio Tracker, but
this couldn't be re-confirmed against actual past-chat search results — the
only Portfolio-related build found was the Portfolio Ledger tab inside the
combined ITR+Portfolio "gap app" (965KB HTML). Get the actual current
Portfolio Tracker file before wiring up the auto-import, rather than
guessing which one it is.

## Design invariants (same as ITRGenie)
- Zero external dependencies, works offline once loaded.
- Paste-and-parse inputs, not form-field-only.
- Shared theme key with ITRGenie: `itrgenie_theme`.
- Own data storage key: `networth_data_v1` (separate from ITRGenie's profile,
  since net worth spans across all financial pillars, not just tax).
