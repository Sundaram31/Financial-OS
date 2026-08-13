# INDEX — Start here every time

Open this file first, in any new chat, on any device. It tells you (and Claude)
where every module actually stands. Don't hunt through old chats — if a decision
or status isn't in here or in a module's own PROGRESS.md, treat it as not decided.

## How to start a new chat about this project
Just say: **"Check the Financial-OS GitHub repo (Sundaram31/Financial-OS),
here's what I want to do: ___"** — Claude reads this file + the relevant
module's PROGRESS.md directly from the repo. No uploads, no manual file juggling.

## Live site
https://sundaram31.github.io/Financial-OS/ — always reflects the latest push.

## Module status at a glance
| Module | Path | Status | Last touched |
|---|---|---|---|
| ITRGenie | `/itrgenie/` | 27 modules, AIS auto-import (now accepts CSV or Excel) + Prior Years fix; app-wide font-size/contrast pass (2026-08-11); bulk-paste boxes (Salary/HRA/Capital Gains/MF/VDA/Other Sources/F&O/Foreign Assets/Rent/Exempt Income/AMT/Schedule AL) made tolerant of currency symbols, thousands commas, and stray header rows (2026-08-11); paste-parsing rewritten safe-by-construction after a third round found live corruption on ordinary two-amount CSV rows (2026-08-11); fourth round fixed a live negative-thousands-grouped-number safety bug (Capital Gains MF losses) and investigated-then-reverted a false-ambiguity fix after fuzzing proved it unsafe (2026-08-11) | 2026-08-11 |
| Portfolio Tracker | `/portfolio/` | Live, guided form + paste/CSV/Excel entry + CAS (NSDL/CDSL) PDF import (dedup/refresh-safe, lazy-loaded libs) + live prices (Yahoo + Stooq no-setup, optional Twelve Data key) — holdings, allocation, performance across 4 accounts + sold-lot/realized-gains tracking (ST/LT classification, capital-gains feed export to ITRGenie) + "Simulate a sale" what-if tax calculator (Sec 111A/112A, pooled ₹1,25,000 LTCG exemption, MF/foreign-holding excluded with honest explanation) — closes roadmap item 4; mobile UX pass done; reorganized into Dashboard/Holdings/Gains & What-If/Accounts & Settings tabs; Dashboard adds a Top Gainers & Losers widget and a plain-language concentration/diversification flag (both honesty-gated, no fabricated numbers), sold-lots table collapses to 10 most recent past a threshold, Accounts/FX/Live-price settings rebalanced onto the Accounts & Settings tab; app-wide font-size/contrast pass (2026-08-11) closed out the remaining sub-13px stragglers this module's own 2026-08-09 UX pass missed; bulk paste made currency-tolerant + guided "Add a holding" form gained a "paste one line to fill in" quick-fill option (2026-08-11); paste-parsing rewritten safe-by-construction, third round (2026-08-11); fourth round added a negative-grouped-number safety fix and a `currentPrice >= 0` guard on both entry paths (2026-08-11) | 2026-08-11 |
| Net Worth Dashboard | `/networth/` | Live, guided "add one item" form (Label + Value) on all 6 category cards + paste/CSV/Excel file upload (collapsed "advanced" option) + inline row editing (2026-08-13, closes the last paste-only gap in the app); app-wide font-size/contrast pass (2026-08-11); category-card paste tolerant of currency symbols, commas, and either column order (2026-08-11); paste-parsing rewritten safe-by-construction, third round (2026-08-11); fourth round added the same negative-grouped-number safety fix (2026-08-11) | 2026-08-13 |
| Goals | `/goals/` | Live, manual entry + paste/CSV/Excel file upload — inflation-adjusted target calculator, risk-profile SIP presets (Debt/Balanced/Equity), annuity-due SIP math, second-pass reviewer fixes; Emergency fund adequacy calculator added (Life Confidence pillar item 1 — monthly-expenses + months-wanted inputs, recommended target, "months covered" stat with red/amber/green tiering); app-wide font-size/contrast pass (2026-08-11); tagged-investments paste tolerant of currency symbols, commas, and either column order (2026-08-11); paste-parsing rewritten safe-by-construction, third round (2026-08-11); fourth round added the same negative-grouped-number safety fix (2026-08-11) | 2026-08-11 |
| Debt & Loan Tracker | `/loans/` | Live, auto-detects from bank statement, paste/CSV/Excel file upload; app-wide font-size/contrast pass (2026-08-11) also fixed a missing `.btn.primary:hover` state this module had drifted from the rest of the app; statement paste now also detects month-name dates (e.g. "01-Jan-2026"), and a real amount-misread bug (a date's own year digits could be picked up as a payment amount) found and fixed (2026-08-11) | 2026-08-11 |
| Insurance Tracker | `/insurance/` | Live, mis-selling checks; app-wide font-size/contrast pass (2026-08-11) | 2026-08-11 |
| Synthesis | `/synthesis/` | Live, read-only cross-module view (net worth, goals, portfolio, debt, insurance adequacy) — first pass; Goals card surfaces Emergency-fund months-covered figure; Financial independence card added (Life Confidence pillar item 2) — combined projection with an explicit assets-source picker (Portfolio vs Net Worth vs manual, never summed) and Emergency-fund-sourced expenses suggestion; reviewer-found negative-expected-return bug in the FI date math fixed same day; app-wide font-size/contrast pass (2026-08-11) closed out this module's own twice-flagged `.tag` known gap; Concentration check card added (2026-08-11, same day) — whole-net-worth category-dominance flag (≥70% in one category, reasoned distinctly from Portfolio's own 50% top-2-holdings threshold) plus a descriptive liquid-vs-illiquid category mix framed as an upper bound, never summed against Portfolio's tracked value | 2026-08-11 |
| Retirement/Pension Planner | — | Not started | — |
| Estate Planning / Document Vault | — | Not started | — |
| GST/e-way bill tool | not yet moved here | Built elsewhere | — |

## App-wide pass: font-size, contrast, cross-module consistency (2026-08-11)
Direct, blunt user feedback: font sizing is hard to see "in places," and the color scheme needs
improvement — across the whole app, not one module. This had been flagged repeatedly across this
session's earlier review cycles and kept getting deferred as "future cleanup." This pass fixed it
exhaustively, everywhere: `itrgenie/`, `networth/`, `goals/`, `loans/`, `insurance/`,
`portfolio/`, `synthesis/`, and the root landing page (`index.html`, which has no `PROGRESS.md` of
its own — see this entry and the git history for what changed there).

- **Font sizes**: a fresh grep sweep of every `<style>` block and every inline `style="font-size"`
  (not just previously-flagged spots) found ~140 declarations under the visual-design skill's
  13-14px mobile-readability floor, spread across every module. All raised to at least 13px —
  labels, table cells, helptext, buttons, badges/tags, and (in ITRGenie) all 17 bulk-paste
  textareas. Two of these were pre-existing, explicitly documented known gaps closing out with
  this pass: `synthesis/PROGRESS.md`'s twice-flagged sub-13px `.tag` element, and
  `portfolio/PROGRESS.md`'s 2026-08-09 UX pass leaving several desktop-base and mobile-override
  sizes un-fixed. See each module's own `PROGRESS.md` for its exact before→after list.
- **Colors**: `--muted` (secondary/helptext color) contrast against `--bg`/`--panel`/`--panel-2`
  was computed (WCAG relative-luminance formula, not eyeballed) for both themes in every module —
  already passes AA (4.5:1) everywhere, 4.9:1–7.4:1 depending on theme/module, no change needed.
  The root landing page's `--muted` had drifted to a different hex (`#8A8F98` vs. every module's
  `#9BA0A8`) — same AA pass/fail outcome either way, but fixed for consistency; it was also
  missing the `--panel-2`/`--rust` tokens every module defines (added, unused for now). One real
  cross-module drift found and fixed: `loans/index.html` was missing the `.btn.primary:hover`
  rule every other module has.
- **Not changed, flagged instead**: `--rust` used as *text* (not just border/background) for
  warning/error copy computes to 3.93:1 against the dark theme's `--bg` — below AA's 4.5:1
  normal-text threshold (passes the 3:1 large-text threshold). This is shared across every module
  that uses `--rust` for inline warnings, and fixing it means choosing a new accessible-but-still-
  "rust" hex for a color also used for borders/icons/tags — a real design decision, not guessed at
  here. Also not changed: `portfolio/index.html`'s `.match-tag.isin` uses a one-off blue
  (`#7EA8C9`) outside the gold/rust/green accent system (pre-existing, not a `--variable` drift).
  Both flagged in `portfolio/PROGRESS.md` for a future session.
- **Root landing page has no light theme** — every module supports the shared dark/light toggle
  (`itrgenie_theme` in localStorage) but `index.html` only ever renders one (dark-only) palette.
  Not added here — it's a real feature gap, not a sizing/contrast/consistency fix, and adding a
  toggle plus a light-theme variable block to a page with no `PROGRESS.md` felt like the wrong
  place to make that call silently. Flagged for whoever next touches the root page.
- **Tested with real headless-Chromium (Playwright)**: full DOM text-node sweep (not a sample) at
  375px and 1280px, both themes, for every module — including clicking through all 25 items in
  ITRGenie's rail, all 4 tabs in Portfolio with every `<details>` expanded, and after populating
  real data via each module's guided-entry form (add a holding, add a goal, add a loan, add a
  policy, parse-and-add a Net Worth row) — 0 text nodes under 13px anywhere, 0 console errors.
  `--muted` contrast checked via actual rendered `getComputedStyle` colors, not assumed hex.
  Screenshotted every module in both themes at both viewports for visual review.

## App-wide pass: paste/upload tolerance for real-world formatting (2026-08-11, same day)
Direct, blunt user feedback: even where paste/upload is already accepted, most parsers still
require the data pre-shaped into an exact column order/count before they'll take it — "these were
the softwares of 1980... programme will handle everything" was the stated bar. `itrgenie/`'s AIS
Auto-Import already met that bar (matches columns by KEYWORD against a real header row, not fixed
position) — this pass generalized that same "tolerate real variation, never silently misread a
number" principle everywhere else it was honestly safe to apply. Touched `itrgenie/`, `goals/`,
`networth/`, `loans/`, `portfolio/`.

- **Currency-symbol/thousands-comma tolerance**: every `parsePastedRows()`-based paste box across
  all 5 modules now strips ₹/$ symbols and thousands-grouping commas before parsing a numeric
  cell (`toNum()`/`parseNumericCell()`), and a shared `protectThousandsCommas()` fix stops a
  comma-grouped value like "₹4,50,000" from being sliced into fake extra columns when comma is
  the row separator. **⚠ Corrected same day, see the entry directly below** — the original
  version of this fix (described as detecting a thousands separator "by shape — no space after an
  internal grouping comma, unlike a real field separator, which always has one" — that claim was
  wrong) shipped a severe regression on plain no-space CSV, live-reproduced and fixed the same
  day.
- **Column-order tolerance where it's actually safe**: `goals/` and `networth/`'s 2-column
  `Label, Value` paste boxes now accept either order (`450000, PPF account` works the same as
  `PPF account, 450000`), since with only 2 columns, which one "looks like a number" reliably
  identifies the Value column. ITRGenie's other paste boxes (Salary, Capital Gains, HRA, etc.)
  deliberately keep strict column order — they have no header row to key off of the way AIS's
  real exported file does, so reordering there would be guessing which typed number means what,
  not detecting it. `loans/`' statement parser was found to already be column-order-agnostic (it
  scans raw description text, not fixed columns) — widened instead to recognize more real-world
  DATE formats (month-name dates like "01-Jan-2026", not just numeric).
- **A "paste one line to fill in" quick-entry option** added to Portfolio Tracker's guided "Add a
  holding" form (6+ separate typed fields for one record) — fills the existing form fields from
  one pasted line, still requiring the explicit "Add holding" click before anything is saved, so
  every value stays reviewable. "Record a sale" was audited and left unchanged — already only 3
  typed fields plus a dropdown, not the multi-field pattern the complaint described.
- **Two real correctness bugs found and fixed during this same audit** (not the pass's original
  goal, found while reading the code closely): ITRGenie's Capital Gains — Equity paste path could
  let an unparseable qty/sell-price cell through as `NaN` instead of being skipped (now
  `isNaN`-checked); `loans/`' amount-extraction regex could pick up a transaction date's own year
  digits as a candidate payment amount, which could silently win as the recorded EMI figure on
  certain real statement layouts (fixed by excluding the matched date substring before scanning
  for amounts).
- **Deliberately NOT done**: no OCR or PDF-to-structured-data parsing was added anywhere — this
  pass is about tolerating variation WITHIN already-supported structured formats (CSV/Excel/
  pasted text), not new document types, per the same reasoning AIS Auto-Import's own author
  already applied when scoping that module to CSV/Excel only.
- **Tested with real headless-Chromium (Playwright)**: 51 targeted checks across the 5 touched
  modules (currency symbols, Indian thousands-grouping, reversed columns, stray header rows,
  genuinely ambiguous both-numeric rows, extra whitespace, month-name dates), each confirming both
  the new tolerant behavior AND that every existing already-working input format still parses
  identically. Full regression smoke pass: all 27 ITRGenie modules + Dashboard/Checklist/Help
  clicked through with 0 console errors; all 5 touched modules loaded at 375px and 1280px with 0
  console errors. See each module's own `PROGRESS.md` for its exact before→after examples.

## Fix: severe paste-parsing regression from the pass above (2026-08-11, same day)
A second reviewer pass live-reproduced a SEVERE bug in the `protectThousandsCommas()` fix
described just above: pasting a completely normal, plain no-space-after-comma row — e.g.
`Acme Corp,1200000,50000,2400` into ITRGenie's Salary paste box, exactly what a raw `.csv`/`.txt`
file or Excel's own `sheet_to_csv()` output (used internally for every `.xlsx` upload in this
app) produces — got its digits silently fused into a corrupted ≈₹1.2 quadrillion Gross salary
figure, with Exempt Allowances/Professional Tax dropped to ₹0. Root cause: the fix's own
"a real separator always has a trailing space" premise was false, so it collapsed ANY comma-joined
run of short digit groups unconditionally, not just genuine thousands-grouped numbers. Confirmed a
genuine regression (not pre-existing) via `git show` against the commit before the offending
change.

**Fix**: the collapse is now a validated fallback, not an unconditional transform — a line is
comma-split naively first, and the thousands-comma collapse is only even attempted when that
naive split overshoots the specific paste box's own known column count, and only trusted if the
collapsed result doesn't fall below that box's real minimum viable column count. Applied at all
~20 `parsePastedRows()` call sites across `itrgenie/` (17), `goals/` (1), `networth/` (1), and
`portfolio/` (2 — bulk paste and guided-form quick-fill), each passing its own real column-count
knowledge (already present in every site's existing `cols.length` check) rather than one global
heuristic. Re-verified: the exact reported failure case now parses correctly; the ORIGINAL
motivating case (a genuinely thousands-grouped price mid-row, e.g. Capital Gains Equity's
`Reliance, 10, 15/06/2021, 1,850.50, 20/07/2025, 2,100.75`) still collapses correctly; a generic
`10,20,30,40` no longer risks fusing into one number; every paste box across the 4 files re-tested
with both comma-space and no-space CSV for the same logical data. Also added a small,
non-blocking fix flagged by the same review: Portfolio's "paste one line to fill in" quick-fill
now visibly flags (outline) the Broker dropdown when a pasted broker name doesn't match any
account, instead of relying on text feedback alone. `loans/` and `insurance/` were never affected
— they don't use `protectThousandsCommas()`. See each touched module's own `PROGRESS.md` for the
full before/after and adversarial test results.

## Third-round fix: paste-parsing rewritten safe-by-construction (2026-08-11, same day)
A second reviewer pass on the fix directly above found it was still converging on individual
reported cases rather than closing the underlying mechanism — it live-reproduced fresh data
corruption in Salary, HRA, and Portfolio Tracker's bulk-add using entirely ordinary no-space CSV
rows containing two adjacent thousands-grouped amounts (e.g.
`Acme Corp,12,00,000,50,000,2,400` — a completely natural way to type three Indian-lakh-grouped
figures). Two precise structural gaps: (1) the prior fix had no UPPER-bound check, so a naive
split that overshot the expected column count but still cleared the minimum was accepted AS-IS,
fake extra columns and all, silently shifting every field after them; (2)
`protectThousandsCommas()`'s regex was a single whole-line pass with no concept of column
boundaries, so it could fuse across a REAL separator whenever the neighbouring field also started
with 1-3 digits (another price, a quantity, a date fragment).

**Fix, safe by construction rather than another patch**: a shared `resolveThousandsMerge()`
replaces the whole-line regex in all 4 touched files. It naive-splits a comma row, then enumerates
every way to merge ADJACENT pieces into a span that is a COMPLETE, correctly-shaped grouped number
end-to-end (Indian: 1-2 digits then 2-digit groups then one 3-digit group — `12,00,000`; Western:
1-3 digits then 3-digit groups — `1,234,567`) — never a loose "both sides look short" guess. A
merge is only ever applied if it's the ONE AND ONLY combination that lands the row's column count
on an exact target (the box's full shape, or any count in between down to its real minimum for
boxes with a genuinely optional trailing field); zero valid combinations or more than one both
mean "don't guess" — the row is honestly skipped (folded into the same "skipped N" count every
paste box already reports, now with a reason attached: "couldn't tell where the columns split —
try a tab-separated paste..."). Tab-delimited paste (a real spreadsheet copy) is detected first and
never touches this logic at all, since a tab can never appear inside a number. Applied at all ~21
`parsePastedRows()` call sites (17 in `itrgenie/`, 1 each in `goals/`/`networth/`, 2 in
`portfolio/`) via one shared per-file implementation, not copy-pasted per site.

**Round-2 failure cases re-tested, honestly**: `Acme Corp,12,00,000,50,000,2,400` (Salary) and
`Apr-2025,1,00,000,40,000,25,000,Mumbai` (HRA) both turned out to be genuinely UNAMBIGUOUS once
verified by hand — the strict grouped-number shape check leaves exactly one valid way to partition
each row, so both now parse correctly instead of corrupting.
`RELIANCE,Zerodha,Equity,10,2,450,01/01/2024,2600,10/08/2026` (Portfolio, all 8 fields present)
is likewise unambiguous and parses correctly. A related shape found during this round's own
adversarial testing — the same Portfolio row with its two optional trailing fields correctly
omitted (`RELIANCE,Zerodha,Equity,10,2,450,01/01/2024`) — is genuinely ambiguous (two structurally
valid readings, one of them nonsensical to a human but structurally indistinguishable to a generic
parser) and now correctly comes back as an honest skip rather than a guess; the same is true for a
Net Worth liability row with its optional date omitted
(`Home loan (SBI),3,20,000`) — which the round-2 entry above had reported as working, but which a
by-hand re-check under the new stricter algorithm shows was only an accident of round 2's
particular search order, not a provably safe result. Both modules' own `PROGRESS.md` document this
correction. See each of the 4 touched modules' own `PROGRESS.md` for the full adversarial test
matrix (tab-separated variants, the original motivating case, a constructed genuinely-ambiguous
row, and a per-box regression sweep with two independently-formatted currency amounts in every
paste box across all 4 files).

## Fourth-round fix: negative-grouped-number safety bug fixed; a second proposed fix investigated and reverted (2026-08-11, same day)
A fourth reviewer pass on the paste-parsing safety work above confirmed the round-3 rewrite's core
mechanism is sound (its own 40,000-trial fuzz against positive numbers found zero silently-wrong
results) but found one live, reproduced, blocking safety bug and one reliability complaint.

**Fixed**: `GROUPED_WESTERN`/`GROUPED_INDIAN`/`spanValid()` only ever allowed an optional `₹`/`$`
prefix on a grouped-number span, never a leading `-`. Capital Gains — Mutual Funds' Gain field
legitimately allows negative values (a real capital LOSS), and that box's TDS column is genuinely
optional — so a real loss like `-1,25,000` with TDS omitted was never recognized as a merge
candidate at all, and the leftover pieces could coincidentally still land on a valid column count,
getting silently saved wrong (e.g. `-1,25,000` saved as `gain:-1, tds:25000` instead of
`gain:-125000`). Fixed by accepting an optional leading `-` the same way `₹`/`$` already are,
applied identically across `itrgenie/`, `portfolio/`, `goals/`, `networth/`. Live-re-tested all 3
reviewer variants (Indian/Western grouping, with/without TDS present): all three moved from
**silently wrong** to an **honest skip** — a confirmed safety improvement, though not all three
resolve to a fully-correct parse (two of the three turned out to be genuinely, structurally
ambiguous once the negative merge is recognized — worked through by hand and confirmed against the
live DFS output, not assumed).

**Investigated, a fix was built, then reverted**: the same review also found ordinary "complete"
rows (e.g. `TCS,Axis Direct,Equity,10,200,01/01/2024,2600,10/08/2026`, `Acme Corp,100,200,300`,
`PPF interest,100,200`) wrongly flagged ambiguous by a coincidental adjacent pair that also looks
like a grouped number. Two implementations of the review's proposed fix ("prefer the untouched
reading whenever it already reaches a valid target") were built and each re-verified with a
60,000-trial fuzz covering positive AND negative numbers across every optional-trailing-field box
in the app — both produced real silently-wrong results (7,462/60,000 and 2,267/60,000
respectively, not rare edge cases: e.g. `Acme Corp,64,150,1262730` genuinely means `Gross:64150`
with `ProfTax` omitted, which a naive-preferring shortcut would silently misread as
`Gross:64, Exempt:150, ProfTax:1262730`). No purely structural rule can safely tell "coincidental
collision" apart from "genuine field omission" — both are structurally valid, differing only in
real-world plausibility a shared, field-type-agnostic helper has no way to judge. Re-running the
same fuzz with this fix fully removed confirmed 0/60,000 silently wrong. Given the negative-number
fix above is the safety-blocking item and this fuzz evidence shows any naive-preference shortcut
reopens exactly the silent-corruption class rounds 1–3 exist to close, **the fix was reverted
rather than shipped partially-safe** — TCS/Acme/PPF-shaped rows remain an honest skip, same as
before this round. Flagged as a genuinely open item needing a properly-scoped future fix (per-field
type/semantic awareness threaded into the ambiguity check — a materially bigger change than a
narrow patch).

Also added, defense in depth: Portfolio's `currentPrice` field now has the same `>= 0` guard its
sibling fields (`qty`, `buyPrice`) already had, on both entry paths.

**Tested with real headless Chromium** (`@sparticuz/chromium` + `playwright-core` — the sandboxed
build environment has no direct route to Playwright's own browser-download CDN, so the browser
binary came via an npm-published package instead, over the already-allowed npm registry route),
driving the actual pages, saving to real `localStorage`, reading it back — not Node-level
unit tests alone. Full regression re-run of every case from rounds 1–3 confirmed none regressed;
5 additional ITRGenie paste boxes beyond Salary/HRA/CG-MF spot-checked live with realistic
no-space multi-amount rows (Clubbing, Crypto/VDA, Other Sources, F&O — including a real
negative-decimal loss figure, AMT), all parsing correctly. See each touched module's own
`PROGRESS.md` for the full before/after tables and fuzz breakdown.

## Current phase: Synthesis Layer, first pass (built 2026-08-09)
`/synthesis/` is live — a read-only page joining Net Worth, Goals, Portfolio,
Debt & Loan, and Insurance data into one view: net worth + trend, per-goal
progress, portfolio value/gain/allocation, debt outstanding + projected
debt-free date, and insurance cover-vs-income adequacy. It never writes to
another module's storage key. Scoped deliberately to the "annual financial
health report card" item from the roadmap's Life Confidence pillar, not the
full Synthesis Layer wishlist — capital-gains/what-if tax modeling is still
out, since it needs Portfolio's not-yet-built sold-position tracking. See
`synthesis/PROGRESS.md` for full scope and the income-figure design
decision (own manual field, one-time prefill from Insurance's own entry,
never parsed out of ITRGenie's profile).

## Previous phase: Portfolio (built 2026-08-09, UX pass same day, gaps remain)
ITRGenie/tax and the smaller Financial OS modules (Goals, Net Worth, Insurance,
Debt & Loan) are done. Portfolio Tracker (`/portfolio/`) is live: holdings
across all 4 broker/demat accounts, performance vs cost basis, asset
allocation, a Net Worth feed export, and a three-tier live price feed —
Yahoo Finance and Stooq with zero setup, plus an optional bring-your-own-key
Twelve Data integration for Stock/Equity/ETF holdings. Real phone usage
surfaced blunt feedback the same day the module was built (live feed
actually failed, mobile fonts too small, entry too hard, layout too
text-heavy) — all four addressed in a same-day UX pass: Stooq added as a
second no-key attempt with failure messages that link straight to Twelve
Data setup, mobile font/layout overhaul (holdings table becomes a stacked
card list under 760px, no horizontal scroll), a guided "Add a holding" form
as the primary entry path (bulk paste/CSV kept as a collapsed "advanced"
option), and a reordered page (bold summary + holdings table first,
everything else collapsed/pushed down). What's still open: neither Yahoo nor
Stooq has been exercised against the real internet from this build
environment (its sandbox blocks outbound network to arbitrary hosts) — Yahoo
is now confirmed broken in at least one real browser, Stooq's real behavior
(especially for NSE symbols) is completely untested; Twelve Data remains the
one tier with real-world provenance. Also still open: no reconciliation yet
against the user's 5+ years of historical data in Drive (this repo had no
Drive access when Portfolio was built — see `portfolio/PROGRESS.md`'s Known
gaps). See MASTER_ROADMAP.md's "Synthesis Layer" section for why this
matters more than it might look -- it's the piece that unlocks cross-module
insights (goal progress, true net worth trend, what-if tax modeling), not
just another standalone tracker.

## Rule going forward
Every session that touches a module updates:
1. That module's `PROGRESS.md`
2. This table's "Last touched" date
3. `MASTER_ROADMAP.md`'s status log, if it's a roadmap-level change

Updates land as git commits directly — no manual upload/delete cycle needed
anymore now that this lives on GitHub instead of Drive.
