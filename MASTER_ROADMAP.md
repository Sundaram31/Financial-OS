# Personal Financial OS — Master Roadmap

## Purpose
Single reference file any session (this chat or Claude Code) reads first to know:
what exists, what's missing, and how modules must talk to each other.

## The complete-solution frame
A full personal financial system covers 8 pillars. Mapping yours against them:

| Pillar | Your module | Status |
|---|---|---|
| Tax compliance & optimization | ITRGenie | Built, 27 modules, AIS auto-import |
| Investments | Portfolio Tracker | Built elsewhere, not yet moved here |
| Goals | Goals module | Live, manual entry + file upload
| Business compliance | GST/e-way bill tool | Built elsewhere |
| Net worth | Net Worth Dashboard | Live, manual entry — awaiting Portfolio Tracker migration for auto-feed |
| Cash flow / budgeting | — | Gap |
| Debt & loans | — | Gap |
| Insurance | — | Gap |
| Estate planning / document vault | — | Gap (Jagoinvestor Master Document spreadsheet exists in Drive — candidate to digitize) |
| Retirement / pension | — | Gap (seafarer PF/pension has specific rules) |
| Operations (non-financial but yours) | Maritime noon-report platform | Built, separate track |

## Recommended module additions, ranked by leverage
1. **Net Worth Dashboard** — aggregates figures already computed by other modules.
2. **Goal Tracker** (extends Portfolio Tracker) — target corpus/date per goal.
3. **Debt & Loan Tracker** — generalizes ITRGenie's home loan interest tracking.
4. **Insurance Tracker** — policy inventory, coverage-vs-need gap check.
5. **Retirement/Pension Planner** — seafarer PF/pension rules need real research.
6. **Estate Planning / Document Vault** — digitize the existing Jagoinvestor sheet.
7. **Cash Flow / Budget tracker** — lowest priority given irregular income sources.

## Cross-module data contracts
- **Capital gains**: Portfolio Tracker → ITRGenie.
  Shape: `{symbol, buydate, selldate, buyprice, sellprice, qty, assetType}[]`
- **Net worth inputs**: each module exports `{category, label, value, asOf}[]`
  → Net Worth Dashboard aggregates.
- **Loan/interest data**: ITRGenie House Property module ↔ Debt Tracker,
  shared identifier = property address or loan ID.

## Status log
- 2026-08-03: Roadmap created. ITR Advisor (23 modules) built.
- 2026-08-03: Renamed "ITR Advisor" → "ITRGenie".
- 2026-08-03: Full audit against official ITR-2 schedule list — 3 bugs fixed
  (ITR-U date, belated/revised split, ITR-3/4 due date), 6 gaps flagged.
- 2026-08-03: Migrated from Google Drive to GitHub (Sundaram31/Financial-OS)
  + GitHub Pages for a live site — eliminates manual upload/delete cycle.

## How to run a session against this roadmap
1. Say "check the Financial-OS repo" — Claude reads this file directly from
   GitHub, no upload needed.
2. Say which numbered item above to build, or "audit [module]" to find gaps.
3. Updates land as commits automatically — this file's status log gets
   updated as part of that commit.
- 2026-08-03: Added Alternate Minimum Tax module (Sec 115JC/115JD) — 24th module.
- 2026-08-03: Added What-If Tax Planner module — 25th module.
- 2026-08-03: Added Schedule EI + 80GGA module — 26th module. Help/Glossary updated to match all new modules.
- 2026-08-03: UX overhaul — guided step-by-step mode, light/dark theme toggle, larger fonts. Addressed direct feedback that the module-menu UI was confusing on first open.
- 2026-08-03: Built Net Worth Dashboard (/networth/) — 5 asset categories + liabilities, snapshot trend with SVG sparkline. Manual entry only; Portfolio Tracker auto-feed pending — couldn't confirm which past Portfolio Tracker file is current, flagged rather than guessed.
- 2026-08-03: Built Goals module (/goals/) — per-goal target/date, tagged investments, monthly contribution, on-track projection. Added CSV/TXT file-upload as second input mode to ITRGenie's Prior Years module and Net Worth Dashboard's category cards (reuses existing paste-parser, no new dependency). Data source question (Yahoo/NSE/Google) researched: all CORS-blocked from browser, Twelve Data-style dedicated API remains the only viable client-side option.
- 2026-08-03: Added AIS Auto-Import module (CSV parsing, keyword classification, review-before-commit) — 27th module. Reworked Prior Years to use structured dropdowns/date-pickers instead of paste-first, per direct user feedback that typing was difficult on mobile.
- 2026-08-03: Fixed Import to merge at top level instead of always replacing — enables the actual intended workflow (Claude reads uploaded documents in chat, hands back targeted JSON, user merge-imports without losing existing data). Clarified: OCR-in-browser stays out per original plan; Claude-reads-in-chat is the correct stopgap, not browser OCR.
- 2026-08-03: Resolved cross-chat continuity gap — a new chat inside the Project didn't inherit context from sibling chats (only Project Knowledge files auto-attach, not chat history). Setting up INDEX.md, MASTER_ROADMAP.md, and itrgenie/PROGRESS.md as Project Knowledge files to fix this properly.
- 2026-08-03: Root-cause fix — House Property module now asks occupancy status via a plain-language wizard instead of trusting user self-classification, after a real case where a relative-occupied property was wrongly filed as self-occupied. Added Sec 64 clubbing warning for spouse-funded properties.
- 2026-08-03: Second root-cause fix — Foreign Assets module now gates on residency status first. Real case: CA incorrectly stated foreign assets only need reporting upon repatriation; correct rule is Schedule FA applies only to Resident & Ordinarily Resident, and NRI foreign income generally isn't taxable in India at all. A previously-issued foreign-income merge file was retracted after residency confirmation.
- 2026-08-03: Status sync after real-document reconciliation session. CONFIRMED: FY2025-26 rent income (Rs 2,90,999, 13 bank credits), residency NRI (matches CA), Vested foreign income correctly excluded from Indian return (NRI), Schedule FA correctly not required (NRI). CORRECTED/RETRACTED: an earlier claim of "Muthoot Finance Rs 2,94,250 LTCG" from Axis Direct could not be verified against actual files and is retracted -- only FY2024-25 capital gains data confirmed so far (both own account and, separately, spouse's account -- do not conflate). BLOCKED: FY2025-26 capital gains statement is password-protected, password pattern unconfirmed -- not guessing at it. Axis flat municipal tax/annual value still pending user's receipt search. ICICI commercial property clubbing question still needs CA consult.
- 2026-08-03: Built Insurance Tracker (/insurance/) — policy CRUD with automatic mis-selling flags (ULIP/endowment bundling, term-cover-vs-income adequacy, unexplained riders, commission-awareness), per financial-adviser persona.
