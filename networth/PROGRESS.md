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

## Updated 2026-08-09 — Import now auto-consumes Portfolio Tracker's feed
The Import button's file handler used to unconditionally replace the entire
internal `data` object with whatever JSON was picked — fine for restoring
Net Worth's own backup, but it meant Portfolio Tracker's `{category, label,
value, asOf}[]` feed export (see `portfolio/PROGRESS.md`) could only be
hand-copied via the paste-ready-lines button, never auto-imported. Import
now branches on the parsed JSON's shape:
- **Array** (a feed, e.g. Portfolio's `portfolio-networth-feed-*.json`
  download): merged into `data.categories[row.category].rows`, not a full
  replace. Upserts by `label` (Portfolio's account labels are stable, e.g.
  "Axis Direct (Portfolio Tracker)"), so re-importing after Portfolio's
  numbers refresh updates the existing row instead of duplicating it. Rows
  are skipped (and counted separately in the result message) if: `_currency`
  is present and isn't `'INR'` (an unconverted foreign-currency number —
  `_currency` isn't part of the formal contract, Portfolio adds it
  specifically to flag this case, so a raw USD figure is never silently
  imported as rupees); `category` doesn't match one of this module's own
  category keys; or the row is otherwise malformed. A result alert reports
  added/updated/skipped counts, matching the add/skipped feedback pattern
  already used by the category-card paste handlers.
- **Object with a `categories` key** (Net Worth's own full export shape):
  unchanged — still a full replace, since that's a legitimate full-backup
  restore, not a feed merge.
- Anything else (unparseable, or valid JSON in an unrecognized shape):
  unchanged `alert()`-based error handling, now covering both cases.

Tested end-to-end in a real browser (Playwright/Chromium) against the
actual code in both `portfolio/index.html` and `networth/index.html`: a
real `buildNetWorthFeed()` export with an unconverted USD account correctly
imports only the INR row and reports the USD one as skipped; setting an FX
rate in Portfolio and re-exporting/re-importing then adds the
now-convertible row and leaves the first row's value updated in place
(no duplicate); a plain full-object Net Worth backup still restores exactly
as before.

## Updated 2026-08-11 — file upload widened to accept Excel
`file_${key}` (every category card's file upload, including Liabilities)
now accepts `.csv,.txt,.xlsx,.xls`, not just CSV/TXT. Vendored a module-own
copy of SheetJS (`lib/xlsx.core.min.js`, self-hosted, no CDN -- same pattern
as `itrgenie/` and `portfolio/`). `wireFileUpload` now converts an uploaded
`.xlsx`/`.xls` file's first sheet to CSV text via `XLSX.utils.sheet_to_csv`
before handing it to the same "Label, Value" row parser the paste box and
plain-CSV upload already use. Tested end-to-end (Playwright): an Excel file
with two Label/Value rows imports identically to the equivalent CSV into the
Investments category; CSV/TXT path re-verified unchanged.

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

## Updated 2026-08-11 — App-wide font-size/contrast/consistency pass
Part of an exhaustive, whole-app pass (every module touched the same day) responding to direct
user feedback that font sizing is hard to see and the color scheme needs improvement — not a
single-module concern.

**9 sub-13px `font-size` declarations raised to 13px** (full grep sweep of the `<style>` block,
not a spot-check): `.brand .sub` 11px→13px, `.panel-header .eyebrow` 11px→13px, `.field label`
11px→13px, `.btn` 12px→13px, `.btn.small` 11px→13px, `table.day-table th` 11.5px→13px,
`.result-box .helptext`/`.helptext` 12.5px→13px, `.breakdown-bar .seg` 10px→13px (the
percentage label inside each asset-allocation bar segment — verified with real sample data via
Playwright that segments too narrow for the text still degrade gracefully via the pre-existing
`overflow:hidden`, same as before, just at a different width threshold), `.legend .item` 12px→13px.

**Cross-module consistency**: `--bg/--panel/--panel-2/--line/--text/--muted/--gold/--gold-dim/
--green/--rust` hex values (both themes) diffed byte-for-byte against every other module —
already identical here, no drift found.

**Contrast**: `--muted` against `--bg`/`--panel`/`--panel-2` computed (not eyeballed) at
6.5–7.4:1 dark, 4.9–5.7:1 light — already passes WCAG AA (4.5:1) in both themes, no change needed.

**Tested with real headless-Chromium (Playwright)**: full DOM text-node sweep at 375px and 1280px,
both themes, on initial load and after populating a category row via the paste-and-parse flow
(`Axis Direct equity+MF, 850000` → Investments) — 0 nodes under 13px, 0 console errors. Functional
regression: paste-and-parse add flow re-verified working end-to-end (row renders, totals update) —
no JS logic touched, CSS values only.

## Updated 2026-08-11 — Category-card paste made tolerant of currency formatting and column order
Same app-wide pass as `itrgenie/` and `goals/` (see `itrgenie/PROGRESS.md`'s matching entry for
the full rationale). Every category card's paste box (`Label, Value[, OutstandingAsOf]` for
Liabilities), used via each card's own "Parse & add" button, was strictly positional and
currency-symbol-intolerant.

**What changed**: `parsePastedRows()` gained `protectThousandsCommas()` (a thousands-grouped
value like "₹4,50,000" no longer splits into fake extra columns when comma is the row separator —
detected by the absence of a space after an internal grouping comma, which a real field separator
always has). A new `parseLabelValueRow(cols)` replaced the old rigid `[label, value] = cols;
isNaN(+value)` check, applied to every asset category card and the Liabilities card alike: with
exactly 2 columns, whichever cell parses as a non-negative number (via `toNum()`, stripping
₹/$/commas/whitespace) is the Value, the other the Label — column order no longer matters for the
common 2-column case. Liabilities' optional 3rd column (`OutstandingAsOf`) keeps the original
strict first-column-is-Label assumption (now currency/comma-tolerant too) since reordering a
3-column row without a header would be a genuine guess, not a detection. A stray header row or
genuinely ambiguous line (both or neither cell numeric) is honestly skipped, not guessed at, same
as before but now correctly distinguishing "ambiguous" from "just has a ₹ symbol." Helptext
updated on the asset-category cards to say "either column order works, and ₹/commas in the amount
are fine."

**Verified with real headless-Chromium (Playwright), 7 checks**: regression — plain
`Axis Direct equity+MF, 850000` still adds correctly; tolerant — `HDFC FD, ₹4,50,000` parses to
₹4,50,000; tolerant — reversed order `275000, Liquid fund` parses to Liquid fund / ₹2,75,000;
honesty — a stray `Label, Value` header row skipped; tolerant — extra whitespace trimmed; the
Liabilities card exists and its own paste box works; tolerant — a Liabilities row with a currency
symbol and an OutstandingAsOf date (`Home loan (SBI), ₹32,00,000, 2026-08-01`) parses correctly.
0 console errors. `node --check` confirmed no syntax errors after the edit.
