# ITRGenie — Progress & Roadmap
*(formerly "ITR Advisor" — renamed 2026-08-03, same tool)*

## What this is
Single-file, offline-first HTML app (`index.html` in this folder, served live at
the site root `/itrgenie/`). 27 plug-and-play modules, each self-contained
(`registerModule({...})`), rendered by a shared dashboard/rail. Generic across
taxpayer profiles — no hardcoded "seafarer" logic; profile-specific behavior
comes from what's entered, not from branching on who the user is.

## Built & working (27 modules)
Form Determination · Prior Years · Residency Calculator · Salary (Sch S) ·
HRA Exemption · Clubbing of Income (Sch SPI) · Capital Gains—Equity ·
Capital Gains—Mutual Funds · Virtual Digital Assets · Real Estate ·
Other Sources (Dividends+Interest) · Business & Professional Income ·
Foreign Assets & Income · House Property · Ch VI-A Deductions ·
Loss Set-off/Carry Forward (CYLA/BFLA/CFL) · Sch AL (Assets & Liabilities) ·
Old vs New Regime Comparison · Advance Tax & Interest (234A/B/C) ·
Year Rollover · Compliance Calendar · AIS Reconciliation ·
Tax Saving Advisor · Alternate Minimum Tax (AMT/AMTC, Sec 115JC/115JD) · What-If Tax Planner ·
Exempt Income (Sch EI) & 80GGA · AIS Auto-Import

## Audit completed 2026-08-03 — against the official ITR-2 schedule list + AY2026-27 changes

### Fixed
1. ITR-U deadline was off by 2 years (formula bug, `end+3` → `end+5`).
2. Belated/revised return deadlines were merged into one date — Budget 2026
   split them (belated 31-Dec, revised extended to 31-Mar). Now separate.
3. Missing ITR-3/ITR-4 non-audit due date (31-Aug, Budget 2026). Added toggle.

### Flagged, not yet fixed
1. Schedule AL threshold conflict — official portal says ₹50L; some secondary
   sources say ₹1Cr for AY2026-27. Kept ₹50L pending direct portal confirmation.
5. Schedule FSI/TR are aggregate-only, not itemized by country/DTAA article.
6. Schedule PTI, Schedule 5A — skipped as not relevant to typical profile.

## Built this session (2026-08-03, second pass)
- **Alternate Minimum Tax module** (Sec 115JC/115JD) — triggers only on
  Chapter VI-A Part-C profit-linked deductions (80-IA/IB/IC/ID/IE, 80JJA,
  80JJAA, 80LA, 80P, 80PA, 80QQB, 80RRB) or Sec 10AA, only under old regime,
  only above Rs 20L Adjusted Total Income, at 18.5%+cess. Includes an AMT
  credit tracker (115JD, 15-year carry-forward). Verified against multiple
  current sources before building — common deductions (80C/80D/80G/HRA)
  correctly do NOT trigger this.

## Import sources clarified + folder upload (2026-08-03)
- **Folder upload** added alongside single-file upload (Prior Years, both
  sections) -- select a whole folder, every CSV/TXT/XLSX inside gets
  processed and combined automatically; PDFs are listed but not
  auto-combined (each needs individual review, same reasoning as single-file
  PDF handling).
- **Cloud Drive / Email import explicitly scoped OUT of the browser tool** --
  same category as OCR: needs real OAuth + backend infrastructure a static
  site can't provide. Stopgap: Claude already has Drive/Gmail access in
  chat, so cloud import works today via that route, not a button in the app.
- **Password-protected file handling clarified**: pulling an encrypted file
  from Drive requires the binary to pass through Claude's own text output
  to reach the sandbox, which is fragile for large files (caused a real
  corruption incident on the FY2025-26 capital gains file). Direct upload
  to chat avoids this entirely -- files land on disk directly, decryption
  is reliable. Documented as the recommended path for any protected file.

## Document hierarchy guide (2026-08-03, from a real case)
AIS Reconciliation module now leads with a "which document actually resolves
this" table -- ranked alternatives per category (capital gains, salary,
interest/dividend, rent), not just a single required document. Root cause:
a real case where a single broker's capital-gains statement looked complete
but wasn't, because the user trades through 4 separate broker/demat accounts
(Axis Direct, Tradejini, Angel One, Axis Vested-US) -- no single-broker
statement can ever be complete on its own. The guide explicitly recommends
cross-checking the SUM of every broker against AIS's own total for that
category, since AIS aggregates broker-agnostically across all accounts --
a mismatch there means an account is missing, not that one document is wrong.
For NRI capital gains specifically, the PIS account statement from the
bank is now ranked as the BEST source (broker-agnostic, covers all PIS
transactions) rather than the individual broker statement.

## Import capability upgrade (2026-08-03)
Bundled SheetJS (xlsx.core.min.js) and PDF.js (pdf.min.js + pdf.worker.min.js) as
self-hosted library files in itrgenie/lib/ -- NOT inline in the HTML (too large
to embed reliably via available tooling), so ITRGenie is now a small folder
(~2.3MB total, mostly the libraries) rather than a single .html file. Still
fully offline/self-contained, no external CDN calls, just multiple files
instead of one.

Every file-upload input (Prior Years x2, and the shared `wireFileUpload`
helper used elsewhere) now handles:
- CSV/TXT: unchanged, auto-parses
- XLSX/XLS: real parsing via SheetJS, converts first sheet to CSV, auto-parses
- PDF: real text extraction via PDF.js (reads actual embedded text -- Form 16,
  e-statements, broker PDFs) -- does NOT auto-parse, since extracted text isn't
  row-structured; shown for manual review/cleanup instead
- Explicitly does NOT do OCR on scanned/photographed documents (no text layer
  to extract) -- if a PDF has no extractable text, the user is told plainly
  and pointed to uploading it in chat instead, where Claude can read it
  directly. Photo/image OCR (Tesseract.js) remains a deliberate non-build
  pending explicit user sign-off on its size/accuracy tradeoffs.

## Real-document reconciliation session notes (2026-08-03)
Working through actual Drive documents surfaced a broader lesson worth
keeping visible: verify every figure against a re-read of the source file
in the SAME session before repeating it, rather than trusting an earlier
turn's summary. Two things went wrong and were caught/corrected only
because of this: (1) foreign income was initially merged into the profile
before residency status was confirmed -- retracted once NRI status was
confirmed. (2) A capital gains figure ("Muthoot Finance Rs 2,94,250 LTCG")
was stated as fact but could not be re-verified against actual files --
retracted as unconfirmed. Neither was caught until a deliberate re-check.

## Built this session, second root-cause fix (from a real CA misconception)
- **Foreign Assets residency gate** — module never checked residency status
  before asking for foreign income/asset detail. Real case: user's CA stated
  foreign assets only need reporting "when cash is brought back" -- factually
  wrong (Schedule FA is a holding-based disclosure, not repatriation-based).
  Correct rule: Schedule FA applies only to Resident & Ordinarily Resident;
  NRI/RNOR are exempt, and foreign-sourced income generally isn't taxable
  for them either (Sec 5(2)). Module now checks residency FIRST and tells
  the user plainly whether the rest of the module even applies to them,
  instead of collecting data that may not belong in the Indian return at all.
- Also corrected mid-session: a foreign-income merge JSON was handed to the
  user before residency was confirmed — wrongly treated foreign dividends/
  SLIP income/a capital loss as relevant to the Indian return. Once NRI
  status was confirmed, retracted that guidance explicitly rather than
  leaving it uncorrected.

## Built this session, root-cause fix (from a real filing miss)
- **House Property occupancy intake wizard** — added before the property-add
  form. Root cause of the gap it fixes: the module used to let the user
  self-classify a property as self-occupied/let-out, trusting they already
  knew the rule. A real case surfaced the gap — a property occupied rent-free
  by in-laws was wrongly treated as self-occupied (by the user's own CA,
  not just a hypothetical), capping home loan interest at ₹2L instead of
  claiming it in full as deemed-let-out. The wizard now asks occupancy in
  plain language (self/relative/vacant/tenant/under construction) and does
  the classification itself, with the relative-occupancy trap called out
  explicitly. Also added a Sec 64 clubbing check for spouse-funded properties
  registered in someone else's name — same session surfaced a case of this too.

## Built this session, extraction workflow enabled
- **Import now merges instead of always replacing** — detects whether an
  imported file looks like a full backup (many top-level keys) or a targeted
  update (few keys), and merges at the top level accordingly, with a confirm
  dialog either way. This is what makes the actual intended workflow safe:
  user uploads a document (Form 16, bank statement, AIS PDF) directly in
  chat, Claude reads it natively and extracts figures, hands back a small
  JSON (e.g. just `{salaryIncome: {...}}`), user imports it, and only that
  section updates — everything else in the profile stays untouched.
- **Clarified scope, for real this time**: OCR-in-the-browser stays out
  (unchanged, correctly). But document extraction via Claude reading
  uploads *in the chat itself* (not the HTML tool doing OCR) is exactly the
  stopgap arrangement intended before the Python app exists — this was a
  misunderstanding on Claude's part mid-session, corrected here.

## Built this session, genuine auto-fill (per direct user feedback)
- **AIS Auto-Import module** — reads the AIS CSV export (income tax portal's
  native format, not a third-party conversion) using a proper quoted-field
  CSV parser, keyword-matches header columns (Category/Description/Value)
  rather than fixed positions since exact AIS header wording couldn't be
  verified with certainty, classifies rows into Salary/Interest/Dividend/
  Capital-gains-flagged buckets, and shows everything for review with
  checkboxes before writing anything into actual module data. Nothing
  auto-commits blindly. This is genuinely different from bank-statement
  auto-fill (OCR) — AIS is a structured file, which is why this is buildable
  in-browser while bank statement OCR correctly stays out of scope.
- **Prior Years reworked** — residency-history and opening-holdings sections
  now lead with structured dropdowns/date-pickers instead of a paste box as
  the primary path (paste demoted to a collapsed "bulk entry" fallback).
  Direct user feedback: typing formatted text was hard on mobile.

## Built this session, UX overhaul (per direct user feedback)
- **Guided step-by-step mode** — Dashboard now leads with "Start step-by-step
  guide," which walks through all active modules one at a time (Back/Next/
  Exit footer), instead of requiring the full rail menu to be understood
  upfront. Rail still works for free navigation at any point.
- **Light theme + toggle** — added a full light-theme CSS variable set and a
  header toggle button, persisted separately from profile data in
  localStorage (`itrgenie_theme`), defaults to dark.
- **Font sizes increased** — base body font 14px→15.5px, card headers
  15px→16px, helptext/table text ~11.5px→12.5-13.5px, across the board for
  readability. Field labels intentionally kept small (they're uppercase
  category tags, not body text).

## Built this session, third addition
- **Exempt Income (Schedule EI) & Section 80GGA module** — disclosure-only
  exempt income tracker (PPF interest, firm profit-share, etc.) plus the
  80GGA deduction (rural development/scientific research donations), wired
  into both Regime Comparison and What-If Planner's actual tax computation
  so it's not a disconnected field.
- **Help & Glossary updated** — added AMT/AMTC, belated-vs-revised, and
  ITR-U glossary terms; added FAQ entries pointing to What-If Planner, AMT,
  and Compliance Calendar; walkthrough now references all 26 modules.

## Built this session, second addition
- **What-If Tax Planner** — reuses Regime Comparison's exact slab/deduction
  logic (same ruleSet, same caps) so the two modules can't disagree. Lets you
  model additional 80C/NPS/80D/80G and capital-loss harvesting, shows each
  lever's isolated tax impact ranked by savings, plus the combined scenario.
  Only meaningful under old regime — explicitly says so under new regime
  rather than showing a misleading zero-impact result.

## Built this session, AIS Auto-Import widened to accept Excel (2026-08-11)
- **AIS Auto-Import (`ais_file`) now accepts `.csv,.txt,.xlsx,.xls`**, not
  just CSV. This was proposed earlier the same session as part of a broader
  "widen upload formats" push, got deprioritized, and was correctly called
  out as not actually done when the user checked -- this entry closes that
  gap. An uploaded `.xlsx`/`.xls` file is read via the vendored SheetJS
  (`XLSX.read`), its first sheet converted to CSV text with
  `XLSX.utils.sheet_to_csv`, then fed through the exact same
  `parseCSVProper` + `classifyAISRows` path the native CSV upload already
  used -- so the keyword-based column matching (Category/Description/Value)
  and the review-with-checkboxes-before-commit safety net behave identically
  regardless of source format. This is reuse of an already-proven pattern:
  Prior Years' `py_file`/`oh_file` imports in this same file, and
  Portfolio's holdings upload, already parse Excel the same way.
- **PDF/JSON deliberately still NOT accepted for AIS**, unchanged from the
  original reasoning documented in the module's header comment: AIS's real
  PDF/JSON structure has never been verified against a live sample, and
  rigid parsing without that verification risks silently mis-extracting
  data. That risk doesn't apply to Excel (same tabular shape as CSV,
  converted losslessly) but does apply to PDF/JSON, so they stay out.
- Tested end-to-end with real headless-Chromium (Playwright): a synthetic
  AIS-shaped `.xlsx` (Category/Description/Name/Value columns, one salary +
  one interest + one dividend row) uploads, parses into the same 3 reviewable
  buckets as an equivalent `.csv`, checkboxes default to checked, and
  "Add to Salary module" correctly commits the checked row. CSV path
  re-verified unchanged (regression). Mobile 375px viewport: upload button
  and copy fit cleanly, no overflow.

## Known gaps (still open, ranked)
1. TDS/26AS line-by-line reconciliation — manual entry only, no structured import.
2. E-verification date tracking — not computed from actual filing date yet.
3. Notice / assessment tracking — nothing logs 143(1)/scrutiny deadlines.
4. Refund status tracking — needs portal login, out of scope for offline tool.
5. Multi-year What-If Planner — no scenario comparison yet.
6. Slab/section limits hardcoded per module — no versioned rule-pack file.

## Design invariants to preserve
- Zero external dependencies, works offline once loaded, no login/server calls.
- Every module: id, label, order, ruleSet, isActive, hasStarted, isComplete,
  requiredDocs, fallbackDocs, render(container, p, save).
- Generic-first: no user-specific hardcoding; behavior derives from entered data.
- Paste-and-parse inputs preferred over form-field-only entry (mobile-friendly).
- Every advisory tip cites why (which module/rule it's derived from).
- Browser localStorage key intentionally kept as `itr_advisor_profile_v1`
  (pre-rename name) so existing saved user data isn't lost by the rename —
  don't change this key without a migration step.

## Updated 2026-08-11 — App-wide font-size/contrast/consistency pass
Direct, blunt user feedback: font sizing hard to see "in places," color scheme needs
improvement, across the whole app — not a single-module fix, and this had been deferred as
out-of-scope in earlier review cycles this session. This pass is the exhaustive fix, covering
every module including this one.

**Raised every sub-13px `font-size` declaration in this file to 13px** — a full grep sweep of
the `<style>` block plus every inline `style="font-size:...px"` in the render functions found 32
declarations below the visual-design skill's stated mobile-readability floor (13-14px), all now
at 13px:
- `.brand .sub` 11px→13px, `nav.rail .rail-label` 10px→13px, `.panel-header .eyebrow`
  11px→13px, `.field label` 11px→13px, `.btn` 12px→13px, `.btn.small` 11px→13px,
  `table.day-table th` 11.5px→13px, `.basis code` 11.5px→13px, `.tag` 10px→13px,
  `.checklist-item .doc-fallback` 12.5px→13px, `.checklist-item .doc-toggle` 11px→13px,
  `.helptext` 12.5px→13px.
- All 17 bulk-paste `<textarea>` inline styles (one per module — Prior Years, Salary, HRA,
  Clubbing ×2, Capital Gains ×2, VDA, Other Sources ×2, Business F&O, Foreign Assets, House
  Property rent, Exempt Income, AMT credit, Assets & Liabilities) 12px→13px.
- The guided-walkthrough "Step X of Y" footer, the 234C interest breakdown detail lines, and the
  Tax Saving Advisor's tip body paragraph: 11-12.5px→13px.

**Supersedes a 2026-08-09 decision** (see the "Font sizes increased" entry above): that pass
explicitly kept field labels small on the reasoning that "they're uppercase category tags, not
body text." Per this session's explicit, repeated instruction that labels are in scope for the
readability floor regardless of styling (uppercase/letter-spaced or not), `.field label` and
`.panel-header .eyebrow` are now 13px like everything else — the letter-spacing/uppercase
treatment that visually distinguished them as labels is unchanged, only the size.

**Cross-module consistency**: this file's `--bg/--panel/--panel-2/--line/--text/--muted/--gold/
--gold-dim/--green/--rust` hex values (both themes) were compared byte-for-byte against every
other module — already identical, no drift found here.

**Contrast**: `--muted` (`#9BA0A8` dark, `#6B6660` light) against `--bg`/`--panel`/`--panel-2` in
both themes computed at 6.5:1–7.4:1 (dark) and 4.9:1–5.7:1 (light) — both comfortably pass WCAG AA
(4.5:1 normal text) already; no change needed.

**Tested with real headless-Chromium (Playwright)**: every visible text node's computed
`font-size` swept at 375px and 1280px, both themes, on the Dashboard *and* by clicking through
all 25 rail items (every module + Document checklist + Help) — 0 nodes under 13px anywhere, 0
console errors. `--muted`-colored text elements' actual rendered contrast (via `getComputedStyle`,
not assumed hex) computed against their real composited background — 0 pairs under 4.5:1.
Functional regression: guided walkthrough, rail navigation, and the AIS/CSV upload paths
re-verified working (no JS logic touched — CSS/inline-style value changes only).

## Updated 2026-08-11 — Bulk-paste boxes made tolerant of real formatting noise
Direct, blunt user feedback: even where paste/upload is already accepted, most of this app's
paste boxes still demand data pre-shaped into an exact column order before they'll take it —
"these were the softwares of 1980." AIS Auto-Import (module 00.3, see its own big comment block
at ~line 917) already gets this right: it matches columns by KEYWORD (category/description/
value) against a real header row, not fixed position. This pass generalizes that same
"tolerate real-world variation, never silently misread a number" principle to every OTHER
paste-and-parse module in this file — Salary, HRA, Clubbing (minor/spouse), Capital Gains
Equity, Capital Gains MF, Crypto/VDA, Other Sources (interest/dividend), Business Income F&O,
Foreign Assets (bank accounts), House Property (rent), Exempt Income, AMT credit carry-forward,
and Assets & Liabilities (Schedule AL) — every module using the shared `parsePastedRows()`
helper.

**What changed, and what deliberately didn't.** These paste boxes have no header row the way
AIS's real exported file does (a user types/pastes raw values, not a document with column
titles) — so column-ORDER tolerance the way AIS does it would mean guessing which typed number
means what, which the honesty rule explicitly rules out. What's genuinely safe to fix instead:
**formatting noise around an already-correctly-positioned value.** Two shared helpers added
right where `parsePastedRows()` already lived (~line 1589):
- **`protectThousandsCommas(line)`** — when a line uses plain commas as the column separator (no
  tab), a thousands-grouped price like "₹1,850" or "1,20,000" would otherwise get sliced into
  several fake extra columns, corrupting every field after it (a genuinely severe failure mode
  here, worse than in the simpler 2-column modules below, since it shifts dates/qty/prices out of
  position for the rest of the row). Detected by shape — a run of 1-3-digit groups joined by
  commas with NO space after the comma, since a real field separator in typed/pasted text is
  reliably followed by a space while a thousands separator never is — and its internal commas are
  stripped before the column split runs, so the split can't mistake them for a boundary.
- **`toNum(s)`** — strips ₹/$ and thousands-separator commas/whitespace before parsing a cell as
  a number, so "₹4,50,000" and "450000" parse identically. Replaces the bare `+field` /
  `isNaN(+field)` numeric checks in all ~14 paste-consumer blocks listed above (`toNum(field)` /
  `isNaN(toNum(field))`); a minus sign is preserved (F&O P/L can be a loss). Returns `NaN` —
  never a guessed value — for anything that still isn't a clean number, so the caller's existing
  `isNaN()` check honestly skips that row (counted in the visible "skipped N" feedback) instead of
  pushing a fabricated figure. Found and fixed one real correctness gap while doing this: Capital
  Gains — Equity's paste path previously let a genuinely unparseable qty/sell-price cell through
  as `NaN` (only `entry.sellprice===null` was checked, not `isNaN`), which would have silently
  shown a `NaN`-based fake gain/loss downstream — now explicitly `isNaN`-checked and skipped, same
  as the Mutual Fund paste path was tightened to do too (added missing `isNaN` checks on `gain`/
  `cost`/`tds` there as well, previously only `cost`/`tds`'s *sign* was checked, not whether they
  parsed at all).
- **NOT changed**: column order stays strictly positional in every one of these boxes — a
  currency symbol or comma is a formatting detail this module can safely normalize, but which
  number means "Qty" vs. "Buy Price" in a headerless typed row is not something it's safe to
  infer, so that stays exactly as documented in each module's own helptext.
- **Dates**: `parseFlexDate()` (already existed, unchanged) already tolerates DD/MM/YYYY,
  MM/DD/YYYY, and ISO — re-verified still used everywhere it was before, no date-format gap found
  in this pass.
- **AIS Auto-Import itself** (the pattern this pass generalizes from) was not touched — it
  already does everything this pass adds, and more (real keyword header-matching), since it reads
  a genuine exported file with real column headers.

**Verified with real headless-Chromium (Playwright)**: constructed inputs shaped differently
than the old strict format (currency symbols, Indian thousands-grouping commas, extra
whitespace) for Salary (`Acme Corp, 1,200,000, 50,000, 2,400` and `Beta LLP, ₹8,50,000`), HRA
(`Apr-2025, 55000, 25000, ₹22,000, metro`), Capital Gains Equity (`Reliance, 10, 15/06/2021,
1,850.50, 20/07/2025, 2,100.75` — the highest-risk case, a 6-column row with comma-grouped
prices in the middle of the row — confirmed it parses to exactly `qty:10, buyprice:1850.50,
sellprice:2100.75` rather than the comma corrupting the column count), Capital Gains MF
(`Parag Parikh Flexi Cap Fund, 112A, 03/10/2025, 94,689.14, 2,55,314.35, 31,914`), and Foreign
Assets bank accounts (`Chase Bank, USA, $250,000, $180,000`) — all now parse correctly where the
old strict `+field` parsing would have produced `NaN` and silently skipped the row. Also
confirmed a genuinely ambiguous/malformed row (a Capital Gains Equity row with non-numeric qty
AND sell price) is honestly skipped, not misparsed, and a stray header row pasted by mistake
(`Employer, Gross, Exempt, ProfTax`) is skipped the same way (neither cell parses as a number, so
nothing is silently misassigned). Full regression: plain already-working formats (`Gamma Inc,
900000, 40000, 2000`, `Muthoot Finance, 275, 21/07/2022, 105.14, 21/05/2025, 207.14`) still parse
identically to before. Full-app smoke pass: clicked through all 27 modules plus Dashboard/
Checklist/Help after these changes — 0 console errors, matching the same sweep the 2026-08-11
font-size pass above already ran. `node --check` confirmed no syntax errors in the extracted
script after every edit.

**⚠ CORRECTION, same day (2026-08-11) — the claim above that a real column separator "is
reliably followed by a space while a thousands separator never is" was WRONG, and shipped a
SEVERE regression.** A second reviewer pass live-reproduced the failure: pasting `Acme Corp,
1200000, 50000, 2400` — a completely normal 4-column Salary row typed with no space after the
commas (exactly what a raw `.csv`/`.txt` file, Excel's own `sheet_to_csv()` output used
internally for every `.xlsx` upload in this app, or just fast typing produces) — got the greedy
`protectThousandsCommas()` collapsing large stretches of that row's digits together, corrupting
Gross salary into **₹1,20,00,00,50,00,02,400** (≈₹1.2 quadrillion) with Exempt Allowances and
Professional Tax silently dropped to ₹0. Confirmed via `git show aa001c1:itrgenie/index.html`
that the row parsed correctly *before* the offending commit — a genuine regression, not a
pre-existing gap, and a live demonstration of exactly the "confidently-displayed wrong number"
failure mode this app's honesty rule exists to prevent.

**The fix — collapse as a validated fallback, not an unconditional transform.** `protectThousandsCommas()`
itself is unchanged (still a regex that strips commas out of a run of 1-3-digit groups), but it's
no longer called unconditionally on every pasted line. `parsePastedRows(text, expectedCols,
minCols)` now takes the calling paste box's own known column shape:
- `expectedCols` — that box's full/target shape (its destructured field count, e.g. 4 for Salary's
  Name/Gross/Exempt/ProfTax). A line is comma-split naively (plain `split(',')`, the pre-8/11
  behavior) first; the collapse is only even *attempted* if that naive split OVERSHOOTS
  `expectedCols` — a normal row that already parses to the right number of columns, space or no
  space, is never touched.
- `minCols` — that box's real minimum viable column count (its own existing `cols.length < N`
  floor), used only when it's lower than `expectedCols` because some trailing fields are optional
  (e.g. Capital Gains MF's TDS column, Prior Years' carry-forward-loss columns, Opening Holdings'
  Notes). A collapsed result is only trusted if it lands at-or-above this floor and below the
  naive count — dropping below the floor would mean the collapse fused two genuinely separate
  columns (worse than leaving the overshoot for the box's own length check to reject), so it's
  discarded and the naive split is kept instead. Using `expectedCols` as both trigger AND floor
  (the first-draft version of this fix) was itself briefly wrong for boxes with optional trailing
  fields — caught before shipping by testing a liability row with no optional date column.
- Applied at all 17 `parsePastedRows()` call sites in this file (Prior Years, Opening Holdings,
  Salary, HRA, Clubbing×2, Capital Gains Equity, Capital Gains MF, VDA, Other Sources×2, F&O,
  Foreign Assets, Rent, Exempt Income, AMT, Schedule AL), each passing its own real
  `expectedCols`/`minCols` rather than a single global heuristic.

**Before/after, the exact reported case** — `Acme Corp,1200000,50000,2400` into Salary:
- Before this fix: Gross salary ₹1,20,00,00,50,00,02,400, Exempt/ProfTax silently ₹0.
- After this fix (live-verified in headless Chromium): parses to exactly 4 columns —
  `name:"Acme Corp", gross:1200000, exempt:50000, profTax:2400` — rendered correctly as
  Gross ₹12,00,000, Exempt ₹50,000, ProfTax ₹2,400, Taxable salary ₹10,97,600.

**Adversarial re-test, all green:**
- Original motivating case still works: `Reliance, 10, 15/06/2021, 1,850.50, 20/07/2025, 2,100.75`
  (Capital Gains Equity, 8 raw comma-split pieces, 6 real columns) still collapses correctly to
  `qty:10, buyprice:1850.50, sellprice:2100.75`.
- `10,20,30,40` (generic small-number CSV) confirmed it no longer fuses into `10203040` anywhere
  — tested directly in the F&O paste box (2-column target) in a live browser: renders as two
  separate rows/cells, never a single concatenated number.
- Indian-style grouping (`12,34,567.89`) still collapses to one number wherever a box expects it.
- Every one of the 17 call sites re-tested with BOTH the comma-space format the original pass
  used AND an equivalent no-space CSV row for the same logical data — both now parse identically
  (60 targeted unit-level checks against the extracted parsing functions + 11 live
  headless-Chromium checks against real paste boxes, storage, and rendered tables).
- Confirmed a known, pre-existing (not newly introduced) residual limitation: if a thousands-
  grouped number sits glued directly against another digit-starting token with zero separating
  character (e.g. a price's trailing comma-group immediately followed by a date, no space) the
  shape-detection regex can still over-match across that boundary. The floor-validation catches
  most of these and falls back to the naive split (no worse than the pre-8/11 baseline, before
  this whole feature existed); in the one case where a corrupted collapse still slips past the
  floor check by column-count alone, the resulting value cell contains a non-numeric character
  (from the date) so `toNum()` returns `NaN` and the row is honestly skipped downstream — never a
  silently-wrong finite number. A real fix would need a smarter per-field/column-boundary-aware
  parser, out of scope for this pass; flagged for a future session if it proves to matter in
  practice.
- Confirmed the other things this commit got right are still intact: `toNum()`'s currency/comma
  stripping, the Capital Gains Equity/MF `isNaN` fixes (re-tested: a garbage qty cell is still
  honestly skipped, not pushed through as a fake `NaN`-based gain), `parseFlexDate()` untouched.
- Full-app smoke pass repeated: itrgenie/, goals/, networth/, portfolio/ all load with 0 console
  errors at 375px and 1280px, both themes.

**Also fixed while in this code (reviewer's non-blocking item, small/low-risk)**: Portfolio
Tracker's "paste one line to fill in" quick-fill left the Broker dropdown silently at its
prior/default value when a pasted broker name didn't match any account, relying on the text
feedback line alone. It now also adds a visible rust-colored outline to the dropdown itself when
that happens, clearing the moment the user touches it — more consistent with this app's
honesty-first pattern of never letting a form field look "filled correctly" when it wasn't. See
`portfolio/PROGRESS.md` for the portfolio-side note.

## THIRD ROUND fix — safe-by-construction rewrite of the paste-comma-collapse logic (2026-08-11, same day)
A second reviewer pass, run specifically against the round-2 fix above, found it converging on
individual reported cases rather than closing the underlying mechanism: it live-reproduced silent
corruption on ordinary no-space CSV rows in Salary, HRA, and Portfolio using nothing exotic — just
two adjacent thousands-grouped amounts, an entirely natural way to type Indian-lakh-grouped
figures. Two precise structural gaps, confirmed by re-reading round 2's own code:
1. **No upper-bound check.** The collapse only checked `collapsed.length >= floor` — there was no
   check that it landed exactly on `expectedCols`. A collapse that overshot `expectedCols` but
   still cleared `floor` was accepted AS-IS, fake extra columns and all, silently shifting every
   field after them. Live-reproduced: `Acme Corp,12,00,000,50,000,2,400` into Salary — Gross came
   back correct, but Exempt/ProfTax silently shifted by one column each.
2. **Whole-line regex, no column-boundary awareness.** `protectThousandsCommas()` was a single
   `.replace()` pass over the entire raw line. It fused across a REAL column separator whenever the
   neighbouring field also started with 1-3 digits — another price, a quantity, a date fragment —
   not just within one genuinely grouped number. Live-reproduced on Portfolio:
   `RELIANCE,Zerodha,Equity,10,2,450,01/01/2024,2600,10/08/2026` (Qty=10 immediately followed by
   BuyPrice=2,450) fused across the Qty/BuyPrice boundary.

**The fix is safe BY CONSTRUCTION, not another patch for these two shapes.** Full design and
history is documented in the code itself (`itrgenie/index.html`, the block comment directly above
`protectThousandsCommas`'s replacement) — summarized:
- **Tabs first.** A line containing a real tab (a genuine spreadsheet copy) is split on tab and
  never touches the comma-collapse logic at all — a tab can never appear inside a number, so this
  sidesteps the whole problem for that large class of real-world paste.
- **`resolveThousandsMerge()` replaces the whole-line regex.** It naive-splits a comma row, then
  enumerates every way to merge ADJACENT pieces into a span that is a COMPLETE, correctly-shaped
  grouped number end-to-end — Indian convention (1-2 digits, then zero-or-more 2-digit groups, then
  one 3-digit group: `12,00,000`) or Western (1-3 digits then one-or-more 3-digit groups:
  `1,234,567`) — never a loose "both sides look short enough" guess. A span is only ever merged if
  it matches one of these patterns from its first digit to its last.
- **Exactly one unambiguous outcome, or an honest skip — never a guess.** A merge combination is
  only accepted if it's the ONE AND ONLY combination that lands the row's column count on an exact
  target (`expectedCols`, or any whole count from `minCols` up to `expectedCols` for boxes with a
  genuinely optional trailing field, e.g. Capital Gains MF's TDS). Zero valid combinations or more
  than one both mean "don't guess" — the row comes back empty, which flows into the same
  `cols.length < N` skip path every other malformed row already uses, and
  `parsePastedRows()`/`skipNote()` now tag *why* (added to every one of the 17 paste boxes'
  feedback text: "N of those: couldn't tell where the columns split — try a tab-separated paste...").
- **Always runs, even when the naive split looks "in range."** An earlier draft of this same
  rewrite kept round 2's short-circuit ("no overshoot, trust it") for performance/simplicity. Own
  adversarial testing (not a reviewer report this time) found that's unsafe too, for the same
  reason as gap 1 above: a genuinely grouped number can coincidentally naive-split a row down to a
  count that still looks "in range" while fusing the wrong two fields together. Example found
  during this session's own testing (not in the original report): Portfolio's
  `RELIANCE,Zerodha,Equity,10,2,450,01/01/2024` (BuyPrice `2,450`, CurrentPrice/AsOf both correctly
  omitted) naive-splits to 7 pieces — already "in range" for the 6-8-column box — but read literally
  that's BuyPrice=2, BuyDate=450, CurrentPrice=01/01/2024, silently wrong despite never
  overshooting. Fixed by always running the merge search (the untouched naive reading is always one
  of the candidates it considers, via every single un-merged piece being trivially a valid
  one-piece span, so a row with nothing to merge still resolves to exactly the same answer as
  before — this costs nothing there).
- One shared implementation per file (`resolveThousandsMerge`/`splitPastedLine`/
  `parsePastedRows`/`skipNote`), called from all 17 `parsePastedRows()` sites in this file — not
  copy-pasted per call site.

**Round-2 failure cases, re-tested — honest determination of which are genuinely resolvable vs.
genuinely ambiguous, not assumed:**
- `Acme Corp,1200000,50000,2400` (Salary, plain no-space, the original round-1/2 case) — still
  parses correctly: `name:"Acme Corp", gross:1200000, exempt:50000, profTax:2400`. No regression.
- `Acme Corp,12,00,000,50,000,2,400` (Salary, Indian lakh-grouped, the round-2 failure) — **genuinely
  unambiguous, now parses correctly**: `gross:1200000, exempt:50000, profTax:2400`. Worked through
  by hand before trusting the test: naive-splits to 8 pieces (`Acme Corp` + 7 digit groups); the
  7 digit groups admit exactly one way to partition into three complete grouped numbers
  (`12,00,000` / `50,000` / `2,400`) that lands on the 4-column target — every other of the 15
  ways to place 2 "cut points" among the 6 candidate boundaries fails the strict grouped-number
  regex on at least one resulting span, so this is not the coin-flip ambiguity it might look like
  at first glance.
- `Apr-2025,1,00,000,40,000,25,000,Mumbai` (HRA, round-2 failure) — **genuinely unambiguous**, same
  reasoning as Salary (structurally identical: 7 digit-group pieces admitting exactly one 3-way
  split): `basicDA:100000, hra:40000, rent:25000, city:"Mumbai"`.
- `RELIANCE,Zerodha,Equity,10,2,450,01/01/2024,2600,10/08/2026` (Portfolio, round-2 failure) —
  **genuinely unambiguous** with all 8 fields present (the trailing CurrentPrice/AsOf pin down the
  target so only one merge combination reaches it):
  `qty:10, buyPrice:2450, buyDate:"01/01/2024", currentPrice:2600, asOf:"10/08/2026"`.
- A 6-field version of the same row with CurrentPrice/AsOf both correctly omitted
  (`RELIANCE,Zerodha,Equity,10,2,450,01/01/2024`) — **genuinely ambiguous, correctly skipped**: the
  naive 7-piece reading (BuyPrice=2, BuyDate=450 — wrong) and the merged 6-piece reading
  (BuyPrice=2450 — right) are BOTH structurally valid targets in the box's 6-8 column window, and
  the algorithm has no semantic understanding that "450" is a nonsensical date to prefer one over
  the other. Correctly returned as an honest skip rather than a coin-flip guess — this is exactly
  the kind of case the whole rewrite exists to catch instead of silently mis-splitting.

**Other adversarial cases tested (own construction, per the reviewer's mandate to find NEW breaking
shapes, not just re-check the reported ones):**
- Tab-separated versions of the Salary, HRA-shaped, and Portfolio rows above — confirmed the tab
  path is taken and the comma-collapse logic is never invoked (cells keep their commas, e.g.
  `"1,200,000"`, which `toNum()` still strips correctly downstream).
- `Reliance, 10, 15/06/2021, 1,850.50, 20/07/2025, 2,100.75` (the ORIGINAL motivating case from the
  first pass, comma-space) — still collapses correctly.
- `10,20,30,40` — still never fuses (nothing in it matches a complete grouped-number span).
- A row constructed to be genuinely ambiguous on purpose — `X,1,200,300,400` targeting a 2-3 column
  box — correctly returns an honest skip (multiple different 2-cut placements each independently
  produce a structurally valid 3-column reading; no way to prefer one).
- Net Worth liability `Home loan (SBI),3,20,000` (thousands-grouped value, OutstandingAsOf
  omitted) — correctly an honest skip: the algorithm finds two competing valid readings
  (`value:320000` with the date omitted, vs. the nonsensical `value:3, OutstandingAsOf:"20000"`)
  and won't guess between them. `Home loan (SBI),3,20,000,15/06/2026` (same value, WITH the real
  date present) parses correctly and unambiguously — the date's presence is what disambiguates it.
- Capital Gains MF with TDS present (`HDFC Fund,LT,15/06/2025,1,00,000,20,000,5,000`) parses
  correctly (`cost:100000, gain:20000, tds:5000`); the same row with TDS genuinely omitted
  (`...,1,00,000,20,000`) is a correctly-honest skip for the same structural reason as the Net
  Worth liability case above.
- A currency-symbol-prefixed version of the original motivating case
  (`Reliance,10,15/06/2021,₹1,850.50,20/07/2025,₹2,100.75`) still parses correctly.
- A synthetic 200-row Salary paste with realistic `toLocaleString('en-IN')`-formatted amounts
  parsed correctly in 8ms with zero skips — confirms the rewrite doesn't cost meaningful
  performance on ordinary bulk paste. A pathological 40-piece single/double-digit row was
  confirmed to bail safely (via the search's own explored-combinations cap) in 2ms rather than
  hang.
- Full regression: every one of the 17 paste boxes in this file re-tested with a no-space CSV row
  containing at least two independently-formatted currency amounts specific to that box's own real
  fields (Prior Years' carry-forward figures, Opening Holdings' buy price, Clubbing amounts, Other
  Sources interest/dividend, F&O P&L, Foreign Assets bank balances, Rent credits, Exempt Income,
  AMT credit, Schedule AL's three sub-sections) — all parsed correctly against the extracted
  parsing functions (`node --check` clean, then evaluated in isolation against the real per-box
  `expectedCols`/`minCols` values read straight out of each call site).

**Known, honestly-documented limitation (not a regression, a structural property of "never
guess")**: a box with more than one independently-optional trailing field, or any row where a
thousands-grouped number's merge could ALSO plausibly fill in a value for an omitted optional
field, will sometimes come back as an honest skip where a human reading the same row could tell
which reading was intended (see the 6-field Portfolio and Net Worth liability examples above). This
is the deliberate cost of "safe by construction" — the alternative would be guessing based on which
reading "looks more sensible," which is exactly the kind of silent misjudgment this whole rewrite
exists to close off. The skip message now says why (`skipNote()`) and suggests the two ways around
it that always work: a tab-separated paste, or a space after each comma.

## FOURTH ROUND — negative-grouped-number safety fix; false-ambiguity fix investigated and reverted (2026-08-11, same day)
A third reviewer pass confirmed the round-3 rewrite above is mechanically sound (a 40,000-trial
fuzz against positive numbers found zero silently-wrong results) but found two gaps: one live,
reproduced, blocking safety bug, and one reliability/ease-of-use complaint.

**Finding 1 (blocking, safety) — fixed.** `GROUPED_WESTERN`/`GROUPED_INDIAN`/`spanValid()` only
ever allowed an optional `₹`/`$` prefix on a grouped-number span, never a leading `-`. Capital
Gains — Mutual Funds' Gain field legitimately allows negative values (a real capital LOSS), and
that box's TDS column is genuinely optional (`expectedCols` 6, `minCols` 5) — so a real loss like
`-1,25,000` with TDS omitted was never recognized as one merge candidate at all, and the leftover
unmerged pieces could coincidentally still land on a valid column count, getting silently accepted
wrong. Live-reproduced before the fix, exactly as the review described:
```
Input:  Parag Parikh Flexi Cap,112A,03/10/2025,95000,-1,25,000
Saved (WRONG, silent):  {"cost":95000,"gain":-1,"tds":25000}
```
**Fix**: `GROUPED_WESTERN`/`GROUPED_INDIAN`/`spanValid()` now accept an optional leading `-` the
same way they already accept `₹`/`$`, so a negative grouped number is found as one merge candidate
like any other. Applied identically in `itrgenie/index.html`, `portfolio/index.html`,
`goals/index.html`, `networth/index.html`.

**Live-browser re-test of all 3 reviewer variants, real `itr_advisor_profile_v1` localStorage,
headless Chromium (not just Node-level unit tests):**
| Input | Before this fix | After this fix |
|---|---|---|
| `...,95000,-1,25,000` (Indian, no TDS) | Silently saved `gain:-1, tds:25000` (wrong) | **Honest skip** — `cgMFRows: []`, feedback explains "couldn't tell where the columns split" |
| `...,95000,-125,000` (Western, no TDS) | Silently saved `gain:-125, tds:0` (1000x wrong) | **Honest skip** |
| `...,95000,-1,25,000,500` (Indian, TDS present) | Silently saved `gain:-1, tds:25000500` (fabricated TDS) | **Honest skip** |

None of the three resolve to the fully-correct parse (`gain:-125000, tds omitted/500`) — each turns
out to be genuinely, structurally ambiguous once the negative merge is recognized as a candidate
(worked through by hand and confirmed against the live DFS output: more than one distinct valid
merge combination reaches a valid column-count target, e.g. for the with-TDS case, `"-1,25,000"` +
`TDS=500` competes with `Gain="-1"` + `TDS="25,000,500"` — both structurally valid, differing only
in real-world plausibility this shared, field-type-agnostic helper has no way to judge). This
matches the pre-stated acceptance bar exactly: "parses correctly, or — if genuinely still
ambiguous — is honestly skipped, never silently wrong." All three moved from **silently wrong** to
**honestly skipped** — a real, confirmed safety improvement, even though not a full resolution.

**Also done (defense in depth, not live-reproduced as a real bug)**: Portfolio's `currentPrice`
field lacked the `>= 0` guard its sibling numeric fields (`qty`, `buyPrice`) both have right next
to it, in both entry paths — the bulk-paste handler and the guided "Add a holding" form's submit
handler. Added to both, live-tested: a negative Current Price is now rejected with a clear message
on both paths (`portfolio_data_v1` stays empty), matching the existing `qty`/`buyPrice` pattern.

**Finding 2 (reliability) — investigated, a fix was attempted, then reverted after fuzzing proved
it unsafe.** The review's reproduction was real: an ordinary "complete" row (naive comma-split
already lands exactly on a box's full expected column count) could still get wrongly flagged
ambiguous by a coincidental adjacent pair that also happens to look like a grouped number once
joined — e.g. `TCS,Axis Direct,Equity,10,200,01/01/2024,2600,10/08/2026` (a share qty "10" next to
a sub-1000 price "200", reading as coincidental "10,200"), `Acme Corp,100,200,300` (Salary), `PPF
interest,100,200` (Exempt Income) — all three wrongly skipped, confirmed live before any fix.

Two implementations of the review's proposed fix ("prefer the untouched/naive reading outright
whenever it already reaches a valid target") were built and each re-verified with a 60,000-trial
fuzz (adapted from the round-3 reviewer's own methodology, this time covering positive AND negative
numbers across every optional-trailing-field box in this app — Salary, Capital Gains MF, Portfolio,
Net Worth liabilities, Exempt Income, Prior Years carry-forward):
- **v1** (skip the shortcut only when the row contains a negative-looking piece): **7,462 of
  60,000 trials (12.4%) silently wrong.**
- **v2** (skip the shortcut only when a competing merge reaches the row's own last piece —
  "tail-anchored"): **2,267 of 60,000 (3.8%) still silently wrong.**

Both failure modes are real, not synthetic noise: whenever an optional field is genuinely omitted
AND the remaining value is itself a thousands-grouped number — extremely common for real Indian
financial amounts — the untouched/naive reading can coincidentally reach the exact same valid
target as the correct merged reading while assigning the wrong value to the wrong field. Example
caught by the fuzz: `Acme Corp,64,150,1262730` genuinely means `Gross:64150` (merged, "64,150")
with `ProfTax` omitted — not `Gross:64, Exempt:150, ProfTax:1262730` as a naive-preferring shortcut
would silently produce. No purely structural (column-count or merge-position) rule can safely tell
"coincidental collision" (TCS/Acme/PPF, where naive is right) apart from "genuine field omission"
(this fuzz-found shape, where the merge is right) — both are structurally valid, differing only in
real-world plausibility that a shared, field-type-agnostic parsing helper has no way to judge.
Re-running the SAME fuzz with Finding 2 fully removed (Finding 1 alone) confirmed **0 of 60,000
silently wrong** — the round-3 mechanism plus Finding 1's negative-sign support is sound on its own.

Given Finding 1 is the explicitly safety-blocking item and this fuzz evidence shows any
naive-preference shortcut reopens exactly the silent-corruption class rounds 1–3 exist to close,
**Finding 2's fix was reverted rather than shipped partially-safe.** TCS/Acme/PPF-shaped rows
remain an honest "couldn't tell where the columns split" skip — same as before this round, not a
new regression, just not resolved. This is flagged here as a genuinely open item: a real fix would
need per-field type/semantic awareness (e.g. knowing a specific column is a date vs. an amount)
threaded into the ambiguity check, which is a materially bigger change than a "narrow, precisely
diagnosed fix" — a future session should scope it properly rather than attempt it as a quick patch.

**Full regression re-run, live browser, confirming neither fix (the one kept, or the one reverted)
broke anything previously working:**
- `Acme Corp,1200000,50000,2400` (Salary, plain) — still correct.
- `Acme Corp,12,00,000,50,000,2,400` (Salary, Indian-grouped, round-2/3 case) — still correct.
- `Apr-2025,1,00,000,40,000,25,000,Mumbai` (HRA, round-2/3 case) — still correct.
- `RELIANCE,Zerodha,Equity,10,2,450,01/01/2024,2600,10/08/2026` (Portfolio, all 8 fields) — still
  correct (`buyPrice:2450`).
- `RELIANCE,Zerodha,Equity,10,2,450,01/01/2024` (Portfolio, optional fields genuinely omitted,
  round-3's own confirmed-ambiguous case) — still an honest skip, exactly as round 3 left it. This
  one mattered specifically: it's structurally the same shape Finding 2 would have broken (naive
  reading landing one field short of the max, competing with a genuine merge) — confirming the
  revert didn't quietly leave a half-applied version of the unsafe shortcut anywhere.
- `Home loan (SBI),3,20,000` (Net Worth liability, date omitted, round-3's confirmed-ambiguous
  case) — still an honest skip.
- Tab-delimited paste (Salary) — still bypasses the comma-collapse machinery entirely, unaffected.
- `10,20,30,40` (generic, no complete grouped-number span) — still never fuses.
- Goals `"PPF account,450000"` and `"450000,PPF account"` — both column orders still resolve to
  the same `{label, value}`.
- Capital Gains — Equity: an unparseable qty cell (`Muthoot Finance,ABC,21/07/2022,105.14,...`) is
  still honestly skipped, not accepted as `NaN`.
- Portfolio's "paste one line to fill in" quick-fill still visibly outlines the Broker dropdown
  (rust, 2px) when a pasted broker name doesn't match any account.

**5 additional paste boxes spot-checked live, beyond Salary/HRA/CG-MF, with realistic no-space
multi-amount rows** (per the review's request for broader coverage given how many rounds this has
taken): Clubbing of Income (`Ananya,investment,12,00,000` → `1200000`), Crypto/VDA
(`Bitcoin,15/06/2025,1,00,000,1,50,000` → cost `100000`, sale `150000`), Other Sources
(`Axis Bank NRO,SB,1,81,100` → `181100`), Business & Professional Income/F&O
(`AARTIIND-FUTSTK-23Feb2023,-30,599.62` → `-30599.62`, a real negative-decimal loss figure,
directly exercising Finding 1's fix), Alternate Minimum Tax
(`2023-24,4,50,000,20,000` → `generated:450000, utilized:20000`) — all five parsed correctly,
zero console errors.

**Testing method**: real headless Chromium (`@sparticuz/chromium` + `playwright-core`, since the
sandboxed build environment has no direct internet access to Playwright's own browser-download CDN
— its npm-published tarball bundles a real Linux binary, downloaded through the allowed npm
registry instead) driving the actual pages at `http://localhost:8977/`, saving to real
`localStorage`, reading the saved data back out, not a Node-level re-implementation. Screenshots
taken of the CG-MF honest-skip state and the Portfolio quick-fill broker-flag. Full 4-module smoke
pass (itrgenie/portfolio/goals/networth) at both 375px and 1280px confirmed 0 console/page errors
after all changes.

## Post-round-4 cleanup (2026-08-11, same day) — stale comment fix + real HRA city bug

A fourth `financial-os-reviewer` pass confirmed round 4 safe to push (80,000+ independent fuzz
trials, zero silent corruption) and gave the final go-ahead — but surfaced two things worth fixing
while already in this code:

1. **Stale/contradictory round-4 comment in `goals/index.html`, `networth/index.html`,
   `portfolio/index.html`** (not `itrgenie/index.html`, which already had the correct wording). The
   comment above `resolveThousandsMerge()` in those three files claimed Finding 2's fix ("prefer the
   untouched reading, but only when no piece looks negative") was actually applied — it wasn't; it
   was investigated, fuzz-tested unsafe, and reverted, same as this file's own accurate comment
   already said. Runtime behavior was correct and identical across all four files (confirmed live by
   the reviewer) — this was a documentation-only bug, but a real one, since a future session's only
   memory of *why* a design choice was made is what's written down, and the wrong comment sat more
   prominently than the right one. Fixed by replacing the stale block in all three files with the
   itrgenie-accurate wording.

2. **Real, pre-existing, out-of-scope bug found by the same review: HRA's City field silently
   defaulted to "nonmetro" for any real city name.** `cityNorm` only ever checked whether the pasted
   text literally contained the word "metro" — so someone typing their actual city ("Mumbai",
   "Chennai", ...) instead of the placeholder keyword got silently classified nonmetro, understating
   their Sec 10(13A) exemption at the 40% rate instead of the correct 50%, with zero warning. This
   predates all four rounds of the paste-safety work above (confirmed via `git log -p` on the
   `cityNorm` line) — not a regression from any of them, but a real, live, silently-wrong-number bug
   of exactly the kind this whole effort exists to catch, so fixed immediately rather than left as a
   dangling "known gap" nobody circles back to.

   The fix is narrower than it might look: `HRAModule.ruleSet.metroCities` (`['delhi','mumbai',
   'kolkata','chennai']`) already existed and is already used correctly by the *computation* — the
   *parser* just never checked a real city name against it. This isn't the same class of "genuinely
   ambiguous" problem the paste-merge logic wrestles with elsewhere in this file: the metro-city list
   is a closed, known set for this filing year, and the tax rule itself defines every OTHER city as
   non-metro — so there's no ambiguity to preserve, just a real name to recognize. `cityNorm` now
   matches the raw city text against `metroCities` first (case-insensitive substring, so "Mumbai" and
   "mumbai city" both hit), falls back to the literal `metro`/`nonmetro` keyword for existing users of
   that placeholder format, and only skips the row when the City field is genuinely blank. Updated the
   box's helptext/placeholder to show a real city name instead of the bare keyword, so new users are
   naturally guided to the safer input shape.

   **Verified live** (headless Chromium, real `itr_advisor_profile_v1` localStorage): `Apr-2025,
   55000, 25000, 22000, Mumbai` → `city:"metro"` (previously silently `"nonmetro"`). Regression:
   `Bengaluru` → `nonmetro` (correct — this module's own description text already states Bengaluru/
   Hyderabad/Pune are 40% this filing year, and the fix doesn't change that), literal `metro`/
   `nonmetro` keywords still classify correctly, `Chennai` → `metro`, and a blank City field is
   honestly skipped (`"Added 0 month(s), skipped 1."`) rather than silently defaulted. Zero console
   errors.

Files touched: `/home/user/Financial-OS/itrgenie/index.html` (HRA parser + helptext/placeholder),
`/home/user/Financial-OS/goals/index.html`, `/home/user/Financial-OS/networth/index.html`,
`/home/user/Financial-OS/portfolio/index.html` (comment corrections only, no runtime change in
those three).

## Fix: AIS Auto-Import silently dropped the employer/deductor name on an unrecognized header (2026-08-13)
`financial-os-ux-tester`'s first end-to-end usability pass found a real, reproduced
silent-data-corruption bug in AIS Auto-Import (module 00.3). `classifyAISRows()`'s `nameCol`
matcher only recognized headers containing `name`, `deductor`, or `reporting entity`. The tester's
realistic test file used the header "Information Source" (a plausible real AIS export header,
though not independently confirmed against a live current sample) -- it didn't match, so `nameCol`
stayed `-1`, every row's `name` came back blank, the review screen's Deductor column showed "—"
throughout with no explanation of *why*, and -- the actually dangerous part -- the salary-import
commit handler silently substituted the row's Description text as the employer name instead
(`name: r.name || r.description`). A confidently-wrong name persisted in the profile with nothing
to flag it as wrong.

**Fix -- the safer of the two options considered, per this project's own "don't guess without
verification" principle.** Widening the keyword list itself was considered and deliberately not
done: there's no solid evidence for which additional header words the actual current AIS portal
export uses (the module's own header comment already states this exact uncertainty), so guessing at
plausible-sounding keywords would just move the unverified-guess risk rather than remove it.
Instead:
- `classifyAISRows()` now returns `nameColFound` (`nameCol>=0`) alongside its buckets, so the
  review screen knows *why* a name is missing -- column not found in this file's headers at all, vs.
  a specific row's cell genuinely being blank.
- The review screen's Salary card shows a rust-colored warning line when any row has no recognized
  name, naming the count and (when applicable) that a Name/Deductor/Reporting Entity column wasn't
  found in the file's headers at all.
- A row with no name gets a real, rust-outlined `<input type="text">` in the Deductor column
  instead of a plain "—" -- editable directly in the review screen, so the user can fix it right
  there before importing, rather than only finding out after the fact in the Salary module.
- **The commit handler (`#ais_import_${key}`'s onclick, salary branch) never falls back to
  `r.description` anymore.** A row's name is `r.name` if recognized, otherwise whatever the user
  typed into that row's rust-outlined input (blank if they left it) -- blank is honest and visibly
  incomplete in the Salary module afterward, never a plausible-looking-but-wrong string silently
  persisting.

**Tested with real headless Chromium (Playwright), reproducing the tester's exact scenario:**
- A CSV with header `Category,Description,Information Source,Value` and row `TDS on
  Salary,Salary Income,Acme Corp Pvt Ltd,1200000` -- the review screen shows the rust warning
  ("1 of these row(s) have no employer/deductor name recognized in this file — a
  Name/Deductor/Reporting Entity column wasn't found in its headers") and a rust-outlined input
  with placeholder "name not found — enter manually", instead of a silent "—".
- Importing with the input left blank: `profile.salaryIncome.employers` gets `{name: "", gross:
  1200000, ...}` — confirmed **not** `{name: "Salary Income", ...}` (the old silent-wrong-name
  bug, which would have been the Description text standing in as a plausible-looking fake employer
  name).
- Filling in the input (`"Acme Corp Pvt Ltd"`) before clicking import: employer correctly recorded
  as `{name: "Acme Corp Pvt Ltd", gross: 1200000, ...}`.
- **Regression -- a file with a recognized header (`Deductor`)**: no warning, no editable input, the
  name populates directly and correctly (`{name: "Beta LLP", gross: 900000, ...}`), same as before
  this fix.
- **Further regression, existing AIS behavior untouched**: a stray title row above the real header
  (`AIS Statement generated on 01-04-2026...` followed by the real `Category,Description,Name,Value`
  header row) still gets skipped correctly and the real header row still found; the `reporting
  entity` keyword variant still matches directly; Interest/Dividend classification and totals
  (which don't use `nameCol`) are unaffected; a file with genuinely unrecognized `Category`/
  `Description` headers still shows the existing "Couldn't find the expected columns" error message,
  unchanged.
- 0 console/page errors across every scenario. `node --check` clean after the edit.

Files touched: `/home/user/Financial-OS/itrgenie/index.html` (`classifyAISRows` now returns
`nameColFound`; `renderReview`'s Salary card markup and its `#ais_import_salary` commit handler).
