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
- **Guided single-item form (Label + Value + Add) alongside paste-and-parse and
  file upload — not paste-only.** This line used to read "Paste-and-parse
  inputs, not form-field-only," a decision made 2026-08-03 before Goals'/
  Portfolio's later mobile-UX passes established the "guided form as the
  default-visible primary path, bulk paste/CSV as a collapsed advanced
  option" pattern (see `portfolio/PROGRESS.md`'s 2026-08-09 UX pass). This
  module never got that same treatment until 2026-08-13 — see the dated
  entry below — and the invariant is corrected here so it stops
  contradicting the actual code, per this repo's own rule against stale
  design-invariant text (see `itrgenie/PROGRESS.md` for a prior instance of
  the same stale-comment issue being caught and fixed).
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

**⚠ CORRECTION, same day (2026-08-11) — the claim above that a real field separator "always has
[a space]" was wrong and shipped a severe regression, caught by a second reviewer pass before it
went further.** See `itrgenie/PROGRESS.md`'s matching correction entry for the full
live-reproduced failure case and root cause. **Fix applied here**: `protectThousandsCommas()` is
unchanged, but `parsePastedRows(text, expectedCols, minCols)` no longer calls it
unconditionally — the collapse is only attempted when a line's naive comma-split overshoots the
column count this card expects (2 for asset categories, 3 for Liabilities to allow its optional
trailing `OutstandingAsOf`), and only trusted if it doesn't drop the result below the card's real
floor of 2 (Label, Value are always required; using the 3-column Liabilities *target* as the
floor too — the first-draft version of this fix — wrongly rejected a valid collapse on a
liability row missing the optional date, caught before shipping and fixed by passing 2 as an
explicit floor separate from the 3-column target). Category card call site now passes
`parsePastedRows(raw, isLiability ? 3 : 2, 2)`. Re-tested live in headless Chromium: plain
`Axis Direct equity+MF,850000` (no space) parses correctly, reversed order still works, a
liability row with Indian-grouped value and no date (`Home loan (SBI),3,20,000`) still correctly
collapses to Value=320000, and the same row WITH a trailing date
(`Home loan (SBI),3,20,000,15/06/2025`) also parses correctly. 0 console errors.

## THIRD ROUND fix — safe-by-construction rewrite (2026-08-11, same day)
A second reviewer pass found the round-2 fix above still converged on the specific reported case
rather than the underlying mechanism, and live-reproduced silent corruption on two adjacent
thousands-grouped liability figures — see `itrgenie/PROGRESS.md`'s matching entry for the full
writeup (both structural gaps: no upper-bound check on the collapse, and a whole-line regex with
no concept of column boundaries) and the new design. This module's own `parsePastedLine`/
`parsePastedRows`/`resolveThousandsMerge`/`skipNote` were replaced with the same shared-shape
implementation used in every other module. The category-card feedback line now also appends
`skipNote(rows)`'s reason when some skips were specifically unresolvable comma-splits.

**Honest correction to the round-2 entry directly above**: it reported
`Home loan (SBI),3,20,000` (Indian-grouped value, `OutstandingAsOf` genuinely omitted) as
correctly collapsing to `Value=320000`. Re-analyzed under round 3's per-boundary structural check,
**this specific row is genuinely ambiguous, not safely resolvable, and now correctly comes back as
an honest skip instead.** Round 2's whole-line regex got the right answer here, but only because
its search space happened not to contain a competing reading in this one case — it wasn't proof of
correctness, and gap 2 (documented in `itrgenie/PROGRESS.md`) shows the same mechanism silently
picking the WRONG reading elsewhere. Under round 3's exhaustive per-boundary search, this row has
TWO structurally valid 3-column readings that both match the box's Label/Value/OutstandingAsOf
shape: `{Value: 320000}` (the sensible one, date omitted) and `{Value: 3, OutstandingAsOf: "20000"}`
(nonsensical — a date field can't be "20000" — but structurally indistinguishable from the sensible
one without semantic/type knowledge the generic merge resolver doesn't have). With two competing
readings, the honest choice is to skip rather than silently pick the one that "looks more
sensible" to a human — which is exactly the failure mode this whole rewrite exists to close. The
SAME row WITH its optional date present (`Home loan (SBI),3,20,000,15/06/2025`) still parses
correctly and unambiguously, since the date's presence is what disambiguates it (the other reading
is now stuck trying to fit "15/06/2025" into a bare-number slot, which fails cleanly). This
trade-off — a small number of "a human could tell, but the generic parser correctly won't guess"
rows now becoming honest skips where round 2 got lucky — is deliberate and documented, not a
regression to silently accept.

**Re-verified**: plain 2-column assets rows (`Axis Direct equity+MF,850000`, reversed order,
currency-symbol/comma-tolerant) all still parse identically to the round-2 baseline — none of them
have the multi-optional-field structure that produces the ambiguity above. A synthetic
two-independently-grouped-amount liability row with the date present
(`Home loan (SBI),32,00,000,15/06/2026`) parses correctly. `10,20`-shaped plain rows still never
fuse. 0 console errors after the edit (`node --check` clean).

## FOURTH ROUND — negative-grouped-number safety fix (2026-08-11, same day)
See `itrgenie/PROGRESS.md`'s matching entry for the full writeup, live-browser results, and fuzz
evidence — this module shares the exact same `resolveThousandsMerge`/`spanValid` code shape.

- **`GROUPED_WESTERN`/`GROUPED_INDIAN`/`spanValid()` now accept an optional leading `-`**, same as
  the existing `₹`/`$` prefix support. This module's liabilities box (`Label, Value, OutstandingAsOf`,
  expectedCols 3, minCols 2) is exactly the shape of box the review's vulnerability needs (an
  optional trailing field) but none of its own fields are legitimately negative (a loan/liability
  Value is validated `>= 0` already), so it was never at live risk the way Capital Gains MF's Gain
  field was — applied for shared-code consistency, re-verified with the same 60,000-trial fuzz
  (0/60,000 silently wrong).
- **A "prefer the naive/untouched reading over a coincidental merge" fix was attempted and
  reverted.** This module's own liabilities box is directly in the risk class the fuzz found real
  corruption in (optional trailing field + thousands-grouped required amount): a synthetic case
  like `X,15,297` (Value=15297 with OutstandingAsOf genuinely omitted, Western-grouped) would have
  been silently misread as `Value:15, OutstandingAsOf:"297"` under the attempted shortcut — "297"
  isn't even a valid date, but the shared parser has no per-field type awareness to catch that.
  Reverted for safety; see `itrgenie/PROGRESS.md` for the full fuzz numbers.
- **Full regression, live browser**: `Home loan (SBI),3,20,000` (date genuinely omitted,
  round-3's own confirmed-ambiguous case) still comes back as the same honest skip, not reopened by
  either fix; `Home loan (SBI),3,20,000,15/06/2026` (date present) still parses correctly and
  unambiguously.

## Updated 2026-08-13 — Guided "add one item" form on every category card; inline row editing
A real end-to-end usability pass (`financial-os-ux-tester`) found this was the one place in the
app where the *original* driving complaint of this session — "enter data in different fields only
by one [paste box, remembering exact field order]" — was still literally true. Goals and Portfolio
had both already gotten a guided-form treatment during earlier mobile-UX passes; Net Worth's six
category cards (five asset categories + Liabilities) never had. Fixed.

**What changed**: every category card now shows a small guided form — a **Label** text input, a
**Value (₹)** number input (`min="0"`), and an **Add** button in a `<form>` (Enter submits it) —
as the default-visible, primary way to add one item, directly under the card heading. The existing
bulk paste-and-parse textarea + "Choose file (CSV/TXT/Excel)" upload is **kept, not replaced**, but
now sits behind a collapsed `<details class="bulk-entry">Or paste/upload several at once</details>`
— the same "guided form primary, bulk paste tucked behind an advanced disclosure" pattern
Portfolio Tracker's 2026-08-09 UX pass established for its own "Add a holding" form. Per-category
placeholder examples (`CATEGORY_EXAMPLES`) replaced a single generic "Axis Direct equity+MF"
example that had previously been shown on every asset card regardless of category (Foreign Assets,
Property, Business, Other all showed an equity/MF example that didn't fit).

**One source of truth for validation, not two divergent paths**: a new shared
`addLabelValueRow(cat, rawLabel, rawValue)` is the only place a row is actually pushed onto
`cat.rows` — trims the label, runs the value through the existing `toNum()`, and requires a
non-empty label and a value that's a non-negative number. The guided form calls it directly with
its two typed fields. The bulk-paste handler still uses `parseLabelValueRow(cols)` first (that part
is genuinely paste-specific — it's what decides *which* pasted column is Label vs Value when
column order is ambiguous) but then hands the result to the same `addLabelValueRow()` to actually
add it, instead of pushing to `cat.rows` directly as it did before. A row added via either path is
identically shaped: `{label, value}`.

**Inline row editing added too** (the tester's secondary finding — fixing a mistake used to mean
delete-the-row-then-re-paste-the-whole-line, with no way to correct just one field). Each rendered
row's Label and Value cells are now live `<input>` fields (`table.day-table input[type="text"|
"number"]`, styled to match the rest of the app rather than left as unstyled default form
controls), the same click-into-cell pattern Portfolio's Holdings table already uses for Avg
Price/Current Price/As Of. An invalid edit (blank label, or a Value that doesn't parse to a number
≥ 0) reverts the input to the last good value instead of silently saving something wrong — confirmed
this actually addresses the tester's stated concern, not just assumed: editing a single row's
Value or Label is now a one-field change, not a delete-and-retype.

**Design invariant corrected**: this module's "Paste-and-parse inputs, not form-field-only" line
(2026-08-03) predated Goals'/Portfolio's later guided-form work and was never revisited — updated
above to state the actual current behavior (guided form + paste/upload, not paste-only) instead of
continuing to contradict the code.

**Tested with real headless-Chromium** (`@sparticuz/chromium` + `playwright-core`, same route used
by this session's earlier paste-parsing safety work — no direct route to Playwright's own browser
CDN from this build environment), 26 checks, all passing:
- Guided form adds a correctly-shaped `{label, value}` row to all 6 category cards (verified in
  both `localStorage` and the rendered list), and rejects an empty label / a negative value with an
  inline error instead of silently doing nothing.
- Bulk paste/CSV regression: plain rows, currency-symbol rows, reversed-column-order rows, and
  Liabilities' optional trailing `OutstandingAsOf` column all still parse exactly as before.
- **Shape parity, directly asserted**: a guided-form-added row and a paste-added row have
  byte-identical key shapes (`{label, value}`) — no divergence between the two entry paths.
- Inline edit: changing an existing row's Value or Label saves correctly and the summary net worth
  figure updates; a blank-label edit reverts instead of saving.
- Mobile (375×812), both themes: guided form works, and a full DOM text-node sweep (not a sample)
  found 0 text nodes under 13px, including the new form/table inputs.
- Import/Export JSON (full-backup shape) round-trips a guided-form-added row correctly.
- `mergeNetWorthFeed` (the cross-module feed-merge function this module actually has — see the
  2026-08-09 entry above; the task brief referred to a `mergeCrossModuleFeed`, which doesn't exist
  in this codebase under that name, so `mergeNetWorthFeed` was tested instead): correctly updates a
  guided-form-added row in place by label, adds a new row from an array-shaped feed import, and
  still skips a non-INR `_currency` row.
- Synthesis (`synthesis/index.html`) loads a guided-form-populated `networth_data_v1` and renders
  the correct net worth figure with 0 console errors — its read-only Net Worth card and
  Concentration check are unaffected by this change (this module's on-disk data shape,
  `{categories: {key: {label, rows: [{label, value}]}}, liabilities, snapshots}`, is unchanged;
  only *how* a row gets added changed, not what a row looks like once added).

**Known gap, flagged, not fixed here (pre-existing, found while reading this code)**: Liabilities'
bulk-paste box has always accepted an optional third `OutstandingAsOf` column (used to disambiguate
column-splitting) but `parseLabelValueRow()` has only ever returned `{label, value}` — the date is
parsed then silently discarded, never actually stored on the row. This predates this session's
change and is unrelated to it (the guided form for Liabilities deliberately mirrors this — Label +
Value only, no date field — rather than adding a field whose value the existing storage layer would
just throw away). Worth a real fix in a future session if `OutstandingAsOf` is meant to be kept.

### Fix (2026-08-13, same day) — reviewer-found mobile zoom bug on the inline-edit inputs
`financial-os-reviewer` independently re-verified this build (shape parity, single-source-of-truth
validation, inline-edit revert-on-invalid, bulk-paste regression, downstream Synthesis/Concentration
reads, XSS-safe label escaping) and confirmed it all correct — but found the mobile fix was
incomplete. The `@media (max-width:760px)` block this same commit added correctly bumped the guided
form's own inputs to 16px (with an explicit comment noting 16px is the real iOS Safari zoom-on-focus
threshold), but the inline-edit table inputs — the OTHER half of this build's stated purpose,
turning a correction into "click the wrong field and retype" instead of delete-and-re-paste — were
left at 14px, still under that threshold. Confirmed live at a real 375px viewport: tapping an
inline-edit field would still trigger the exact iOS zoom-jump this build otherwise fixed, directly
undercutting the feature's own point on the platform this whole session has centered on. One-line
fix: raised `table.day-table input[type="text"], table.day-table input[type="number"]` to 16px
inside the same mobile media query. Verified live: both the guided-form inputs and the inline-edit
inputs now measure 16px via `getComputedStyle` at 375px.
