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
| ITRGenie | `/itrgenie/` | 27 modules, AIS auto-import (now accepts CSV or Excel) + Prior Years fix; app-wide font-size/contrast pass (2026-08-11); bulk-paste boxes (Salary/HRA/Capital Gains/MF/VDA/Other Sources/F&O/Foreign Assets/Rent/Exempt Income/AMT/Schedule AL) made tolerant of currency symbols, thousands commas, and stray header rows (2026-08-11) | 2026-08-11 |
| Portfolio Tracker | `/portfolio/` | Live, guided form + paste/CSV/Excel entry + CAS (NSDL/CDSL) PDF import (dedup/refresh-safe, lazy-loaded libs) + live prices (Yahoo + Stooq no-setup, optional Twelve Data key) — holdings, allocation, performance across 4 accounts + sold-lot/realized-gains tracking (ST/LT classification, capital-gains feed export to ITRGenie) + "Simulate a sale" what-if tax calculator (Sec 111A/112A, pooled ₹1,25,000 LTCG exemption, MF/foreign-holding excluded with honest explanation) — closes roadmap item 4; mobile UX pass done; reorganized into Dashboard/Holdings/Gains & What-If/Accounts & Settings tabs; Dashboard adds a Top Gainers & Losers widget and a plain-language concentration/diversification flag (both honesty-gated, no fabricated numbers), sold-lots table collapses to 10 most recent past a threshold, Accounts/FX/Live-price settings rebalanced onto the Accounts & Settings tab; app-wide font-size/contrast pass (2026-08-11) closed out the remaining sub-13px stragglers this module's own 2026-08-09 UX pass missed; bulk paste made currency-tolerant + guided "Add a holding" form gained a "paste one line to fill in" quick-fill option (2026-08-11) | 2026-08-11 |
| Net Worth Dashboard | `/networth/` | Live, manual entry + paste/CSV/Excel file upload; app-wide font-size/contrast pass (2026-08-11); category-card paste tolerant of currency symbols, commas, and either column order (2026-08-11) | 2026-08-11 |
| Goals | `/goals/` | Live, manual entry + paste/CSV/Excel file upload — inflation-adjusted target calculator, risk-profile SIP presets (Debt/Balanced/Equity), annuity-due SIP math, second-pass reviewer fixes; Emergency fund adequacy calculator added (Life Confidence pillar item 1 — monthly-expenses + months-wanted inputs, recommended target, "months covered" stat with red/amber/green tiering); app-wide font-size/contrast pass (2026-08-11); tagged-investments paste tolerant of currency symbols, commas, and either column order (2026-08-11) | 2026-08-11 |
| Debt & Loan Tracker | `/loans/` | Live, auto-detects from bank statement, paste/CSV/Excel file upload; app-wide font-size/contrast pass (2026-08-11) also fixed a missing `.btn.primary:hover` state this module had drifted from the rest of the app; statement paste now also detects month-name dates (e.g. "01-Jan-2026"), and a real amount-misread bug (a date's own year digits could be picked up as a payment amount) found and fixed (2026-08-11) | 2026-08-11 |
| Insurance Tracker | `/insurance/` | Live, mis-selling checks; app-wide font-size/contrast pass (2026-08-11) | 2026-08-11 |
| Synthesis | `/synthesis/` | Live, read-only cross-module view (net worth, goals, portfolio, debt, insurance adequacy) — first pass; Goals card surfaces Emergency-fund months-covered figure; Financial independence card added (Life Confidence pillar item 2) — combined projection with an explicit assets-source picker (Portfolio vs Net Worth vs manual, never summed) and Emergency-fund-sourced expenses suggestion; reviewer-found negative-expected-return bug in the FI date math fixed same day; app-wide font-size/contrast pass (2026-08-11) closed out this module's own twice-flagged `.tag` known gap | 2026-08-11 |
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
