# Synthesis — Progress

## What this is
The cross-module insights view described in `MASTER_ROADMAP.md`'s "Synthesis
Layer" section — one page that reads every other module's own localStorage
data (same-origin, no export/import handshake needed) and joins it into a
single picture: net worth + trend, goal progress, portfolio performance, the
debt picture, and insurance adequacy. It is **strictly read-only** against
every other module: it only ever calls `localStorage.getItem()` on
`networth_data_v1`, `goals_data_v1`, `portfolio_data_v1`, `loans_data_v1`,
`insurance_data_v1` — never `setItem()`. It owns exactly one small piece of
data itself (an annual income figure, needed for the insurance adequacy
check), stored in its own `synthesis_data_v1` key.

Same visual system as every other module (shared CSS variables, IBM Plex
Mono + Source Serif 4, gold/rust/green accents, seal mark, shared
`itrgenie_theme` toggle) — built and reviewed against the visual-design
skill's usability bar (numbers before explanation, mobile type floor,
no-horizontal-scroll layouts) from the start, not as a later fix.

## Built (2026-08-09)

**Scope — deliberately the "annual financial health report card" from the
Life Confidence pillar (item 8), not the full aspirational Synthesis Layer
wishlist**, because that's what's genuinely computable from data that
already exists in this app today:
- **Net worth**: current total (computed live from Net Worth's entered
  categories/liabilities, not just the last saved snapshot) + trend delta
  and a sparkline if 2+ snapshots exist, + the same category breakdown bar
  Net Worth's own dashboard shows.
- **Goal progress**: per-goal progress bar, on-track/behind status, and an
  aggregate "N of M goals on track" — uses `projectGoal()` copied verbatim
  from `goals/index.html` (same PV-growth + FV-of-annuity math), not a
  reimplementation that could silently drift from what Goals itself shows.
- **Portfolio performance**: current value, cost basis, gain/loss (₹ and
  %), and asset-type allocation breakdown — uses the same
  `computeHoldingMetrics`/`toINR` logic as `portfolio/index.html` (own
  accounts/fx per the read `portfolio_data_v1` object, not assumed).
- **Debt/loan picture**: total outstanding, total EMI/month, and a
  projected debt-free date. Loans doesn't store a debt-free date field
  directly (confirmed by reading `loans/index.html` before assuming) — it
  computes months-to-payoff via a standard amortization formula
  (`amortizationSummary()`); that function is reused verbatim here, and the
  overall debt-free date is the *latest* projected payoff across all loans
  that have enough info (rate + EMI) to project. Loans missing rate/EMI are
  flagged as "Can't project" per-loan and noted in the aggregate stat rather
  than silently excluded from the total outstanding figure.
- **Insurance adequacy**: total policy count, total term life cover, and
  cover-vs-income multiple against the usual 10x floor.

## The income-figure question (explicit design decision)
A true adequacy check needs an annual income figure. Per explicit
instruction, this was **not** reverse-engineered from ITRGenie's
`itr_advisor_profile_v1` — that shape is scattered per-tax-module, not a
single clean number, and guessing at extracting one would violate this
project's "real data over guesses" rule.

Instead: Synthesis has its own manual income input, stored in its own
`synthesis_data_v1` key (`{annualIncome}`), fully independent of every
other module's data. As a one-time convenience, if Synthesis has never had
a value entered *and* Insurance Tracker already has a real user-entered
`annualIncome` (Insurance already asks for this itself, for its own
mis-selling/adequacy checks), Synthesis prefills its own field from that
value once — clearly labeled "Pulled from your Insurance Tracker entry —
edit here if it's changed" — then saves it into its own key and never reads
`insurance_data_v1.annualIncome` again. `insurance_data_v1` itself is never
written to. This uses real, already-entered data instead of asking the user
to retype a number they already gave the app once, while still keeping the
figure fully owned and editable within Synthesis, as instructed.

## What's deliberately NOT in this first pass, and why
- **What-if fund-switch / capital gains tax modeling** (roadmap items 6-7
  in the Synthesis wishlist) — needs Portfolio's *sold*-position (realized
  gains) tracking joined with ITRGenie's capital gains logic. Portfolio
  currently only tracks open holdings; there is no sell/capital-gains
  workflow yet (confirmed in `portfolio/index.html` and
  `MASTER_ROADMAP.md`'s "Updated module sequence" item 4). Building this
  properly means building that Portfolio feature first, not guessing at a
  parallel data shape here.
- **"How is my portfolio performing" + "true asset allocation" beyond what's
  shown** — covered by the Portfolio performance section above; nothing
  deeper (e.g. account-level allocation, historical performance over time)
  was in scope for this pass.
- **Overall tax-reduction synthesis across ITRGenie + Portfolio +
  What-If Planner** — same blocker as capital gains above, plus this needs
  the What-If Planner's own logic wired in, which is a separate future item.
- **Financial independence date, income-shock stress test, retirement
  corpus projection, family resilience/estate planning, children's
  education cost projection, NRI/FEMA compliance, household view** — later
  items in the Life Confidence pillar list (`MASTER_ROADMAP.md`), not this
  pass's scope. None of them are blocked by anything built here; they're
  simply separate, larger builds.

## Tested (2026-08-09)
Real headless-Chromium (Playwright) suite, 29 checks, run against the actual
module files (not mocks) via a local static server:
- **Partial-data path**: seeded realistic data into `networth_data_v1`,
  `goals_data_v1`, `portfolio_data_v1` only (left `loans_data_v1` and
  `insurance_data_v1` unset). Verified: correct net worth total/trend/
  breakdown, correct goal on-track/behind counts and per-goal progress bars
  (including a goal with no target date showing "No target set" rather than
  a false status), correct portfolio value/gain/allocation math (hand-
  checked against the seeded holdings and FX rate), and clear "no data yet"
  empty states with working links for the two unset modules — no crash, no
  misleading zero.
- **Full-data path**: added `loans_data_v1` (one fully-specified loan, one
  missing rate/EMI) and `insurance_data_v1` (two policies + an
  `annualIncome`). Verified debt-free date computed correctly (hand-checked
  against the amortization formula), the under-specified loan correctly
  shown as "Can't project" instead of silently omitted, the income field
  correctly prefilled from Insurance's own `annualIncome`, and the adequacy
  verdict computed correctly against the 10x floor.
- **Read-only guarantee**: compared `localStorage` for every source key
  byte-for-byte before and after page load, after editing the income field,
  and confirmed `loans_data_v1`/`insurance_data_v1` are never created when
  absent and never mutated when present (including immediately after being
  read for the income prefill) — this module truly never writes to another
  module's key.
- **Fully-empty state**: no source module data at all — verified all five
  section empty-states render with working "Add in [Module]" links, no JS
  errors.
- **Mobile usability**: 375×812 viewport, verified no text renders below
  13px anywhere in normal reading flow (found and fixed two CSS-specificity
  bugs during testing where a mobile media-query override was being beaten
  by a more specific base-CSS selector — `.stat-label` and `.card-sub` were
  silently staying at their desktop size on phone width until fixed) and no
  horizontal scroll.
- Both themes (light/dark) checked at both viewports; zero console/page
  errors across all passes.

## Path chosen
`/synthesis/` — added as a live card to the root `index.html` module list.

## Known gaps
- This page reads `localStorage` once at load time, not reactively — if you
  add data in another module in a different tab, use the "↻ Refresh"
  button (or reload) to see it reflected here. No `storage` event listener
  was added since this is a simple read-once dashboard, not a live sync
  tool; revisit if that friction turns out to matter in practice.
- No export/import on this page — nothing to back up, since it owns no
  data of consequence beyond the one income figure (which is trivially
  re-enterable).
- Debt-free date is only as accurate as Loans' own amortization formula,
  which (per `loans/index.html`'s own comment) doesn't re-amortize after
  prepayments — an approximation, not a schedule.

## Design invariants (same as every module)
- Zero external dependencies, works offline once loaded.
- Shared theme key with the rest of the app: `itrgenie_theme`.
- Own data storage key: `synthesis_data_v1` (just the one manual income
  figure) — never writes to any other module's key.
- Guided single-field form for the one piece of manual entry (annual
  income), consistent with how Insurance Tracker's own context fields work
  — no paste/CSV needed for a single scalar value.
