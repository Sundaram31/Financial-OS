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
- 2026-08-03: Bundled SheetJS + PDF.js as self-hosted lib files (itrgenie/lib/, ~1.9MB) -- ITRGenie is now a small folder, not a single HTML file, since inlining libraries this size wasn't reliably possible. Excel and PDF-with-text-layer import now work with real parsing/extraction, not guessing. Photo/scanned-image OCR explicitly deferred pending user decision on size/accuracy tradeoffs.
- 2026-08-03: Added document-hierarchy guide to AIS Reconciliation, from a real case where a single-broker capital gains statement was incomplete because the user trades across 4 separate accounts. Guide ranks alternative documents per category and recommends cross-checking broker sums against AIS's own aggregate total to catch missing accounts.
- 2026-08-03: Added folder-upload alongside file-upload (Prior Years). Clarified architecture: local/folder/mobile upload buildable in-browser now; cloud Drive/email import needs real backend (same category as OCR), stays chat-mediated via Claude for now. Documented that direct chat upload is the reliable path for password-protected files, vs. fragile Drive-pull-then-paste.
- 2026-08-07: Major session — real FY2025-26 reconciliation against actual uploaded documents (AIS, CA computation, capital gains statements, full bank statements across 4 accounts). Key corrections made and retracted where wrong: GAV finding retracted (CA/AIS figure confirmed correct, bank-transaction-label search was the unreliable source); foreign income merge retracted after confirming NRI status (foreign income not taxable in India for NRI, Schedule FA not required). Verified capital gains built from real Axis Direct statements (Muthoot LTCG, Amara Raja/Syngene, Aptus loss, MF gains). Two root-cause fixes shipped to ITRGenie: House Property occupancy intake wizard (catches "relative living rent-free" misclassification), Foreign Assets residency gate (checks NRI/ROR status before asking for foreign income detail). Import upgraded to merge instead of replace, enabling safe "Claude reads document in chat, hands back JSON" workflow. File import upgraded: real Excel (SheetJS) and PDF-text (PDF.js) parsing bundled self-hosted, plus folder-upload. AIS Auto-Import module built (CSV parsing, review-before-commit). Document-hierarchy guide added to AIS Reconciliation (ranked alternative sources, e.g. PIS statement > broker statement for NRI capital gains) after real case of an incomplete single-broker statement (user trades via 4 accounts: Axis Direct, Tradejini, Angel One, Axis Vested-US).
- 2026-08-07: Built + validated a bank-statement transaction classifier using PARTICULARS/description text only (NOT relying on any pre-existing category column, since most real statements don't have one) -- 98.7% accuracy validated against ground truth on a real 394-transaction account. Real failure modes found and documented: fund-house name variants (KotakMutua vs Mutual) needed broadening the match pattern; self-transfers via own name at another bank needed name-matching; family/friend transfers need a one-time user-provided name registry (can't be inferred); false positives occur when a name appears in unrelated transaction memo text (a travel booking that happened to mention a spouse's name).
- 2026-08-07: Scoped the "Financial Events" vision precisely: FD/RD lifecycle, Loan EMI/prepayment, Investment cash-flow, and Insurance premium payments are ALL fully computable from bank statement data alone. Capital gains is NOT -- bank data shows money moved to a broker/AMC but never which security/quantity/price, so FIFO gain computation still needs the broker/CAMS source at least once; bank data's real value there is flagging that a sale event happened (so nothing gets missed), not replacing the source document. Next build: Debt & Loan Tracker (roadmap item, and the most bank-derivable piece of this vision) using the validated classifier. FD/RD tracker and Investment cash-flow ledger queued after.

## The Synthesis Layer — what Financial OS is actually for
Every module so far has been built to work standalone. The real value, stated
explicitly by the user 2026-08-07, is what emerges once they're joined:

**Not just tracking — answering, over a 2-3 year horizon:**
- Am I progressing toward each goal, and by how much (Goals + Net Worth + Portfolio)
- What's my net worth, right now and trending over time (Net Worth + all sources)
- Is my insurance actually sufficient for my family, not just "do I have a policy" (Insurance + income + dependents)
- How is my portfolio performing, and what's my real asset allocation (Portfolio + Net Worth)
- What-if: switching Fund A to Fund B — what's the tax cost of that switch specifically (Portfolio + ITRGenie's capital gains logic)
- How much capital gains tax is coming this year, and what's legally reducible within the rules (Portfolio + ITRGenie + What-If Planner)
- Overall: how can total tax be reduced, synthesized across everything, not just what ITRGenie sees in isolation

This is why every module writes to a shared, predictable data shape
(see Cross-module data contracts above) — the payoff isn't any one module,
it's this synthesis layer becoming buildable once enough modules exist with
real, consistent data flowing between them.

## Reprioritization, 2026-08-07
User's own framing: "the IT part... looks smaller in the whole picture."
ITRGenie is mature (27 modules) and correctly scoped to tax filing --
**Portfolio is the next major phase**, not incremental Financial Events
modules. Debt & Loan Tracker (just shipped) is the last "smaller" module
before this shift.

**Resource available for the Portfolio build**: user has 5+ years of
historical IT/financial data already in Google Drive -- to be used both
for building the Portfolio module's logic AND as real test data, same
approach that made ITRGenie's real-document reconciliation valuable rather
than theoretical. Next session should locate and inventory this historical
data before designing the Portfolio module's data model.

## Updated module sequence
1. ~~ITRGenie~~ -- done, mature, 27 modules
2. ~~Goals, Net Worth, Insurance, Debt & Loan~~ -- done, smaller modules
3. **Portfolio (next, major phase)** -- live prices, holdings across all
   4 broker/demat accounts (Axis Direct, Tradejini, Angel One, Vested-US),
   performance tracking, asset allocation view. Feeds Net Worth's Investments
   category and Goals' tagged-investments for the first time with real data
   instead of manual entry.
4. What-if fund-switch tax modeling -- needs Portfolio's holding-level data
   (cost basis, holding period) joined with ITRGenie's capital gains logic.
5. The Synthesis Layer itself -- a cross-module insights view, only
   buildable once Portfolio exists and the data contracts are proven with
   real data across at least 3-4 modules.
