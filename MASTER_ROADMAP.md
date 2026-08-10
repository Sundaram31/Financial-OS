# Personal Financial OS — Master Roadmap

## Purpose
Single reference file any session (this chat or Claude Code) reads first to know:
what exists, what's missing, and how modules must talk to each other.

## The complete-solution frame
A full personal financial system covers 8 pillars. Mapping yours against them:

| Pillar | Your module | Status |
|---|---|---|
| Tax compliance & optimization | ITRGenie | Built, 27 modules, AIS auto-import |
| Investments | Portfolio Tracker | Live (`/portfolio/`), guided form + paste/CSV entry + live prices (Yahoo + Stooq no-setup, optional Twelve Data key, 2026-08-09) — holdings/allocation/performance across all 4 accounts; mobile UX pass done same day (2026-08-09) after real phone-use feedback; Yahoo confirmed broken in a real browser, Stooq unverified, Drive-data reconciliation still open |
| Goals | Goals module | Live, manual entry + file upload
| Business compliance | GST/e-way bill tool | Built elsewhere |
| Net worth | Net Worth Dashboard | Live, manual entry — Portfolio Tracker now exports a feed for it (JSON + paste-ready lines), not yet auto-imported |
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
- 2026-08-09: Built Portfolio Tracker (`/portfolio/`) -- the "next major phase" item and the last unbuilt piece of the original 8-pillar list. Holdings across all 4 broker/demat accounts (Axis Direct, Tradejini, Angel One, Vested-US), performance tracking (cost basis vs current value, per holding and aggregate), asset allocation view (by asset type and by account), manual USD->INR rate for folding Vested-US into INR aggregates, and a Net Worth Investments-feed export (`{category,label,value,asOf}[]` contract, plus a paste-ready-lines button since Net Worth's own Import doesn't yet consume this generic shape). Three things deliberately NOT resolved by guessing, per explicit instruction: (1) live price data -- Yahoo/NSE/Google Finance still CORS-blocked from a zero-backend browser, a paid Twelve Data-style API is still the only viable option and the user hasn't picked/paid for one, so Current Price stays user-entered only; (2) the earlier "dark-terminal, Twelve Data, technical indicators" Portfolio Tracker referenced in past notes remains unlocated (same ambiguity `networth/PROGRESS.md` already flagged) -- built fresh against this repo's real light/dark toggle design instead of imitating an unseen file; (3) the user's 5+ years of historical portfolio data in Google Drive has not been reconciled against this data model -- this session had no Drive access, so the accounts/holdings/fx shape is a first design based on the roadmap's stated scope, not yet validated against real trade history. See `portfolio/PROGRESS.md` for full detail on all three gaps and what's deliberately deferred (capital-gains export, holding-period tax classification, corporate actions).
- 2026-08-09: Closed Portfolio Tracker's live-price gap (item 1 above) per explicit user direction to build two layered tiers rather than pick one. **Tier 1 (no setup)**: `fetchQuoteYahoo(symbol)` calls Yahoo Finance's public chart endpoint (`query1.finance.yahoo.com`, falling back to `query2`) directly from the browser, reading `chart.result[0].meta.regularMarketPrice`. **Tier 2 (optional, bring-your-own-key)**: `fetchQuoteTwelveData(symbol, exchange, apiKey)` reuses the exact safe request/parse pattern from the earlier Portfolio Tracker prototype located in the user's Drive this session; key stored in its own localStorage key (`portfolio_livekey_v1`), never in the exported JSON, never hardcoded. Both are small isolated per-provider functions behind one `fetchLivePrice(h)` orchestrator so a future third provider (explicitly anticipated by the user) is a contained addition. Scoped to Stock/Equity/ETF holdings only -- Mutual Fund and other types stay manual, visibly marked rather than silently skipped, since fund NAVs need AMFI scheme codes this session had no basis to guess at. INR holdings get a `.NS` Yahoo suffix / `exchange=NSE` Twelve Data param; Vested-US holdings use the plain ticker; a failed fetch of any kind (CORS, HTTP error, malformed/negative/missing price) never overwrites the existing manually-entered price, and always shows a clear per-row status rather than failing silently. Refresh-all is staggered ~350ms apart. **What's confirmed vs. not**: Tier 2, the scoping/symbol logic, the fallback order, staggering, the never-overwrite-on-failure guarantee, and the UI were all verified with a real headless-Chromium (Playwright) test suite (34 checks) with `fetch` mocked at the network boundary, plus a visual check in both themes. Tier 1's actual behavior against Yahoo's live endpoint in a real browser is **still unverified by anyone** -- this build environment's own sandbox proxy blocks outbound network to arbitrary hosts (confirmed via a failed `curl` to `query1.finance.yahoo.com` returning a 403 from the sandbox, not from Yahoo), so real-world CORS/rate-limit behavior can only be confirmed once the user tries it on the live deployed site. See `portfolio/PROGRESS.md`'s 2026-08-09 "Live price feed built" entry for full detail.
- 2026-08-09: Built the Synthesis Layer's **first pass** (`/synthesis/`) -- roadmap item 5 above, moved from "not started" to a real first build. Confirmed the key architecture fact first (same-origin GitHub Pages deploy means every module's localStorage key is already directly readable from any page on the site -- no export/import handshake needed for a read-only view), then read each source module's actual current data shape from its own file rather than trusting a paraphrase (Net Worth's `{categories:{...}, liabilities:{...}, snapshots:[...]}`, Goals' `{goals:[...]}` with a `projectGoal()` function copied verbatim to stay in lockstep, Portfolio's `{accounts, holdings, fx}` with its own `computeHoldingMetrics`/`toINR` logic reused, Loans' `{loans:[...]}` -- confirmed it does NOT store a debt-free date field, only enough to derive one via its own `amortizationSummary()` amortization formula, reused verbatim -- and Insurance's `{policies:[...], annualIncome, dependents, existingLoans}`). Scoped deliberately to what's genuinely computable today rather than the full aspirational wishlist in this file's "Synthesis Layer" section: net worth + trend, per-goal progress/on-track status, portfolio value/gain/allocation, debt outstanding + EMI + projected debt-free date, and insurance cover-vs-income adequacy -- this maps directly onto the Life Confidence pillar's item 8 ("annual financial health report card"). Explicitly left out, and why: what-if fund-switch/capital-gains tax modeling (needs Portfolio's sold-position/realized-gains tracking, which doesn't exist -- Portfolio only tracks open holdings), and the overall tax-reduction synthesis across ITRGenie + Portfolio + What-If Planner (same blocker). The insurance-adequacy income figure was deliberately NOT reverse-engineered from ITRGenie's `itr_advisor_profile_v1` (scattered per-tax-module, not a single clean number) -- Synthesis instead has its own manual income input stored in its own `synthesis_data_v1` key, with a one-time convenience prefill from Insurance Tracker's own already-real `annualIncome` field if set (never re-read after that, `insurance_data_v1` itself never written). Verified strictly read-only against every source module with a real headless-Chromium (Playwright) suite (29 checks): byte-for-byte before/after comparison of every source module's localStorage value confirmed no writes ever happen to `networth_data_v1`/`goals_data_v1`/`portfolio_data_v1`/`loans_data_v1`/`insurance_data_v1`, even immediately after the income-prefill read; partial-data (3 of 5 modules seeded), full-data, and fully-empty scenarios all rendered correctly with clear per-section "no data yet, add it in [Module]" guidance rather than a crash or a misleading zero; mobile (375px) and desktop (1280px), both themes, verified no sub-13px text and no horizontal scroll (two CSS-specificity bugs found and fixed during this pass, where a mobile media-query override was silently losing to a more specific base-CSS selector). See `synthesis/PROGRESS.md` for full detail.
- 2026-08-10: Fixed Portfolio Tracker's document import per real user feedback naming it the weakest part of the app. (1) Real Excel (.xlsx/.xls) import via self-hosted SheetJS with fuzzy column detection (header aliasing + ISIN-pattern fallback) and a mapping-preview-before-commit UI -- the old file upload silently mis-read binary broker exports as plain text. (2) New capability: password-protected CAS (NSDL/CDSL demat statement) PDF import via self-hosted PDF.js, real inline password-unlock UI (PDF.js's actual `onPassword` callback, not a stub), ISIN-anchored text parsing kept in one isolated/easy-to-revise function since it's UNVERIFIED against a real CAS (no real file/password was available this session -- password mechanics and Excel fuzzy-matching WERE verified for real, against a genuinely encrypted test PDF and a realistic messy-header test spreadsheet). Because a CAS has no cost-basis data, imported holdings get Buy Price left genuinely blank rather than a `marketValue/qty` figure mislabeled as buy price -- surfaced directly in the import UI, not just docs. Found and fixed a related real correctness bug while building this: the gain/loss math previously treated a missing buy price as a cost basis of 0, which would have shown a CAS-imported holding's full current value as fake "gain" -- now `null`-aware throughout (`computeHoldingMetrics`, `computePortfolio`, the top stat tile, the by-account table), with holdings missing a Buy Price explicitly flagged and excluded from Invested/Gain-Loss totals rather than silently miscounted. See `portfolio/PROGRESS.md`'s 2026-08-10 entry for the full verified/unverified breakdown.

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
3. **Portfolio -- built 2026-08-09 (`/portfolio/`), gaps still open.**
   Holdings across all 4 broker/demat accounts (Axis Direct, Tradejini,
   Angel One, Vested-US), performance tracking (gain/loss vs cost basis, per
   holding and aggregate), asset allocation view (by asset type and by
   account), and a Net Worth Investments-category feed export
   (`{category,label,value,asOf}[]` + a paste-ready-lines convenience
   button). As of 2026-08-09, also a two-tier live price feed for
   Stock/Equity/ETF holdings -- Yahoo Finance with zero setup (Tier 1,
   real-browser CORS behavior still unverified from this build environment)
   plus an optional bring-your-own-key Twelve Data integration (Tier 2,
   verified with a mocked-fetch headless-browser test suite); Mutual Fund
   stays manual-only. **Still not done, deliberately**: reconciliation
   against the user's 5+ years of historical Drive data (this build had no
   Drive access -- see `portfolio/PROGRESS.md`); Goals' tagged-investments
   still isn't pulling from here. The old "dark-terminal, Twelve Data,
   technical indicators" Portfolio Tracker referenced in past notes remains
   unlocated -- this module was built fresh against this repo's real design
   system instead of guessing at that file.
4. What-if fund-switch tax modeling -- needs Portfolio's holding-level data
   (cost basis, holding period) joined with ITRGenie's capital gains logic.
   Portfolio currently has no sell/capital-gains workflow (only open
   holdings) -- that would need to be built as part of this item, not
   assumed to already exist.
5. **The Synthesis Layer -- first pass built 2026-08-09 (`/synthesis/`).**
   Read-only cross-module view: net worth + trend, per-goal progress,
   portfolio value/gain/allocation, debt outstanding + projected debt-free
   date, insurance cover-vs-income adequacy. Scoped to the "annual
   financial health report card" (Life Confidence pillar item 8 below), the
   part of this wishlist genuinely computable from data that already
   exists -- not the full list below. **Still not done, deliberately**:
   what-if fund-switch/capital-gains tax modeling and the overall
   tax-reduction synthesis (both need Portfolio's sold-position/realized-
   gains tracking, which doesn't exist -- Portfolio only tracks open
   holdings, so item 4 above still needs to happen first). See
   `synthesis/PROGRESS.md` for full scope and the income-figure design
   decision.

## Life Confidence — a 9th pillar (added 2026-08-07)
Everything so far tracks and computes. This pillar exists for a different
purpose: answering "will I actually be okay," which is what turns a pile of
correct numbers into peace of mind. Ranked by leverage, same convention as
the original 8-pillar list.

1. **Emergency fund adequacy check** — 6-12 months of true liquid expenses,
   not "some savings somewhere." Simple, high-confidence-per-effort.
2. **Financial independence date** — one combined projection across debts,
   investments, and goals: the date work becomes optional. The single number
   most likely to change how someone feels about their plan, not just informs it.
3. **Income-shock stress test** — for contract-based income (seafarer
   specifically): "next contract delayed 3 months" modeled against fixed
   obligations (EMI, SIPs, premiums). Turns a vague worry into a concrete,
   answerable question.
4. **Retirement/pension corpus projection** — "at current savings rate,
   retiring at age X, will I have enough." Seafarer PF/pension rules are
   specific, not generic EPF -- needs real research before building (same
   flag as in the original 8-pillar Retirement item).
5. **Family resilience / estate planning** — nominee correctness across every
   account (easy to miss during months at sea), will status, and a single
   "what would my family need to know" reference. The existing Jagoinvestor
   Master Document in Drive is a real starting point to digitize, not a
   from-scratch build.
6. **Children's education cost projection** — inflation-adjusted specifically
   (education costs outpace general CPI); a goal that doesn't account for
   this quietly falls short without anyone noticing until too late.
7. **NRI/FEMA compliance tracking** — repatriation limits, PIS account
   rules; easy to unknowingly breach, expensive to fix after the fact.
8. **Annual financial health report card** — a once-a-year small set of
   indicators (net worth trend, goal progress %, insurance adequacy,
   debt-free date) so progress is *felt*, not just theoretically trackable
   in modules that otherwise go unopened.
9. **Household view (optional)** — combined view with spouse's separate
   investments/PAN, with her own consent, for a truer picture than an
   artificially narrower single-person one.

Sequencing note: none of these block Portfolio (the current next phase) --
they're the layer that comes after Portfolio + Synthesis Layer exist, since
several (financial independence date, health report card) need real
cross-module data flowing before they can compute anything meaningful rather
than show a placeholder.

## Desktop/Python app started (2026-08-07)
User has Python installed on Mac, ready to begin the installable-app phase.
Architecture decided: core-logic/UI separation FIRST, before any wrapper --
`desktop/core/` is pure Python with zero UI dependency, so cloud deployment
later means wrapping the same functions in an API, not rewriting them.

**Cross-platform reality check, decided:**
- Windows + Mac: `pywebview` wraps the EXISTING itrgenie HTML/JS almost
  unchanged (renders via native WebKit/WebView2), Python only handles what
  JS can't (file system, OCR, encrypted-file decrypt). Reuses ~90% of what's
  already built. Packaged via PyInstaller into .exe / .app.
- Android/iPhone: staying on the GitHub Pages web version (already works),
  optionally add a PWA manifest for home-screen install feel. True native
  mobile packaging (Buildozer for Android, App Store for iOS) is a distinct,
  much larger future project -- iOS specifically has no sideload path,
  requires Apple Developer Program + review. Not started, not blocking.
- AI-agent access: clarified as two separate things -- Claude continuing to
  build the codebase (already happening via chat+GitHub) vs. an in-app AI
  feature (separate, optional, future, needs network + API key toggle).
- Cloud: deferred, but the core/UI separation done now is specifically what
  makes it non-disruptive later.

**Built this session:**
- `desktop/core/models.py` -- dataclasses mirroring the JS profile object
- `desktop/core/residency.py` -- first ported module (residency calculator,
  RNOR logic, holding-period-days helper with the 365-day boundary fix
  preserved from JS source comments)
- `desktop/tests/test_residency.py` -- 4 tests, verified against REAL data
  from this session (the actual FY2025-26 voyage: 160 days in India, NRI)
- `desktop/README.md` -- documents the porting convention for future sessions

**Next**: continue porting remaining 26 modules in JS order sequence, then
SQLite storage layer, then the pywebview wrapper itself.

## Portfolio Tracker UX overhaul in response to real usage (2026-08-09)
Real phone-use feedback came in the same day Portfolio Tracker was built, and
it was blunt: the "no-setup" live feed (Yahoo, Tier 1) actually failed for
the user, mobile fonts were uncomfortably small, adding a holding via a
single comma-separated paste line was genuinely hard on a phone keyboard,
and the page led with paragraphs instead of the holdings/P&L a portfolio
tracker exists to show. All four fixed in one pass (see
`portfolio/PROGRESS.md`'s matching dated entry for the full breakdown):
Stooq added as a second free/no-key live-price attempt with failure messages
that now link directly to the confirmed-working fix (Twelve Data) instead of
leaving an opaque error; a real mobile font/layout baseline added (tables
become stacked cards under 760px, verified via Playwright at a 375×812
viewport — no horizontal scroll, no sub-13px text); a guided "Add a holding"
form built as the primary entry path (producing the identical holding object
shape the existing paste-parser produces, so nothing downstream changed),
with the original paste/CSV flow kept but collapsed as "bulk add/advanced";
and the page reordered to lead with a bold value/gain-loss summary and the
holdings table, pushing Accounts/FX/Live-settings/Known-gaps down or into
collapsed `<details>`. No data model or cross-module contract changed — this
is flagged here (rather than left to the module's own PROGRESS.md alone)
because it's a concrete example of the "build against real usage, not just
spec" loop this roadmap depends on, and because the live-price tier list
(now three tiers) is referenced from this file's pillar table above.
