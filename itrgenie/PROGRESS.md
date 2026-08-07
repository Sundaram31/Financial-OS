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
