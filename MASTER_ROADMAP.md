# Personal Financial OS — Master Roadmap

## Purpose
Single reference file any session (this chat or Claude Code) reads first to know:
what exists, what's missing, and how modules must talk to each other.

## The complete-solution frame
A full personal financial system covers 8 pillars. Mapping yours against them:

| Pillar | Your module | Status |
|---|---|---|
| Tax compliance & optimization | ITRGenie | Built, 26 modules, audited |
| Investments | Portfolio Tracker | Built elsewhere, not yet moved here |
| Goals | (planned extension to Portfolio Tracker) | Idea only |
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
