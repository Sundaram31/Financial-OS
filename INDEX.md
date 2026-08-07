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
| Portfolio Tracker | not yet moved here | Built elsewhere | — |
| Net Worth Dashboard | `/networth/` | Live, manual entry | 2026-08-03 |
| Goals | `/goals/` | Live, manual entry + file upload | 2026-08-03 |
| Debt & Loan Tracker | `/loans/` | Live, auto-detects from bank statement | 2026-08-07 |
| Insurance Tracker | `/insurance/` | Live, mis-selling checks | 2026-08-03 |
| Retirement/Pension Planner | — | Not started | — |
| Estate Planning / Document Vault | — | Not started | — |
| GST/e-way bill tool | not yet moved here | Built elsewhere | — |

## Current phase: Portfolio (major, next)
ITRGenie/tax and the smaller Financial OS modules (Goals, Net Worth, Insurance,
Debt & Loan) are done. Next real phase: Portfolio module -- holdings across
all 4 broker/demat accounts, performance, asset allocation. User has 5+ years
of historical data in Drive to build/test against. See MASTER_ROADMAP.md's
"Synthesis Layer" section for why this matters more than it might look --
it's the piece that unlocks cross-module insights (goal progress, true net
worth trend, what-if tax modeling), not just another standalone tracker.

## Rule going forward
Every session that touches a module updates:
1. That module's `PROGRESS.md`
2. This table's "Last touched" date
3. `MASTER_ROADMAP.md`'s status log, if it's a roadmap-level change

Updates land as git commits directly — no manual upload/delete cycle needed
anymore now that this lives on GitHub instead of Drive.
