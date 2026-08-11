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
| ITRGenie | `/itrgenie/` | 27 modules, AIS auto-import + Prior Years fix | 2026-08-03 |
| Portfolio Tracker | `/portfolio/` | Live, guided form + paste/CSV/Excel entry + CAS (NSDL/CDSL) PDF import (dedup/refresh-safe, lazy-loaded libs) + live prices (Yahoo + Stooq no-setup, optional Twelve Data key) — holdings, allocation, performance across 4 accounts + sold-lot/realized-gains tracking (ST/LT classification, capital-gains feed export to ITRGenie) + "Simulate a sale" what-if tax calculator (Sec 111A/112A, pooled ₹1,25,000 LTCG exemption, MF/foreign-holding excluded with honest explanation) — closes roadmap item 4; mobile UX pass done; reorganized into Dashboard/Holdings/Realized Gains & What-If/Export & Settings tabs (pure UI reorganization, no logic changes) | 2026-08-11 |
| Net Worth Dashboard | `/networth/` | Live, manual entry | 2026-08-03 |
| Goals | `/goals/` | Live, manual entry + file upload — inflation-adjusted target calculator, risk-profile SIP presets (Debt/Balanced/Equity), annuity-due SIP math, second-pass reviewer fixes; Emergency fund adequacy calculator added (Life Confidence pillar item 1 — monthly-expenses + months-wanted inputs, recommended target, "months covered" stat with red/amber/green tiering) | 2026-08-10 |
| Debt & Loan Tracker | `/loans/` | Live, auto-detects from bank statement | 2026-08-07 |
| Insurance Tracker | `/insurance/` | Live, mis-selling checks | 2026-08-03 |
| Synthesis | `/synthesis/` | Live, read-only cross-module view (net worth, goals, portfolio, debt, insurance adequacy) — first pass; Goals card surfaces Emergency-fund months-covered figure; Financial independence card added (Life Confidence pillar item 2) — combined projection with an explicit assets-source picker (Portfolio vs Net Worth vs manual, never summed) and Emergency-fund-sourced expenses suggestion | 2026-08-11 |
| Retirement/Pension Planner | — | Not started | — |
| Estate Planning / Document Vault | — | Not started | — |
| GST/e-way bill tool | not yet moved here | Built elsewhere | — |

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
