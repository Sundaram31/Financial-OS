# ITRGenie — Progress & Roadmap
*(formerly "ITR Advisor" — renamed 2026-08-03, same tool)*

## What this is
Single-file, offline-first HTML app (`index.html` in this folder, served live at
the site root `/itrgenie/`). 26 plug-and-play modules, each self-contained
(`registerModule({...})`), rendered by a shared dashboard/rail. Generic across
taxpayer profiles — no hardcoded "seafarer" logic; profile-specific behavior
comes from what's entered, not from branching on who the user is.

## Built & working (26 modules)
Form Determination · Prior Years · Residency Calculator · Salary (Sch S) ·
HRA Exemption · Clubbing of Income (Sch SPI) · Capital Gains—Equity ·
Capital Gains—Mutual Funds · Virtual Digital Assets · Real Estate ·
Other Sources (Dividends+Interest) · Business & Professional Income ·
Foreign Assets & Income · House Property · Ch VI-A Deductions ·
Loss Set-off/Carry Forward (CYLA/BFLA/CFL) · Sch AL (Assets & Liabilities) ·
Old vs New Regime Comparison · Advance Tax & Interest (234A/B/C) ·
Year Rollover · Compliance Calendar · AIS Reconciliation ·
Tax Saving Advisor · Alternate Minimum Tax (AMT/AMTC, Sec 115JC/115JD) · What-If Tax Planner ·
Exempt Income (Sch EI) & 80GGA

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
