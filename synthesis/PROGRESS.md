# Synthesis — Progress

## What this is
The cross-module insights view described in `MASTER_ROADMAP.md`'s "Synthesis
Layer" section — one page that reads every other module's own localStorage
data (same-origin, no export/import handshake needed) and joins it into a
single picture: net worth + trend, goal progress, portfolio performance, the
debt picture, insurance adequacy, and (as of 2026-08-11) a Financial
independence projection. It is **strictly read-only** against every other
module: it only ever calls `localStorage.getItem()` on `networth_data_v1`,
`goals_data_v1`, `portfolio_data_v1`, `loans_data_v1`, `insurance_data_v1`
— never `setItem()`. It owns a small amount of data itself, stored in its
own `synthesis_data_v1` key: an annual income figure (insurance adequacy
check) and, since 2026-08-11, the Financial independence card's own
assumption inputs.

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
- **Income-shock stress test, retirement corpus projection, family
  resilience/estate planning, children's education cost projection,
  NRI/FEMA compliance, household view** — later items in the Life
  Confidence pillar list (`MASTER_ROADMAP.md`), not this pass's scope.
  None of them are blocked by anything built here; they're simply
  separate, larger builds. (Financial independence date — pillar item 2 —
  was originally listed here too; it's now built, see the 2026-08-11 entry
  below.)

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

## Updated (2026-08-10) — Emergency fund coverage line on the Goals card
Small, additive touch alongside `goals/index.html`'s new Emergency fund adequacy calculator (see
`goals/PROGRESS.md`'s 2026-08-10 entry, and `MASTER_ROADMAP.md`'s Life Confidence pillar item 1).
For any goal with `category === 'Emergency fund'` that has a nonzero `efMonthlyExpenses` entered,
`renderGoalsCard()`'s per-goal row now shows one extra line — "Emergency fund: 4.2 of 9 months
covered" — computed as `proj.currentValue / efMonthlyExpenses` (reusing the same tagged-
investments total already computed for that goal's normal progress bar, against
`efMonthsWanted||9`), with the same red-under-3 / gold-building / green-adequate tier coloring
`goals/index.html` uses. Every other goal category, and an Emergency-fund goal with no expenses
entered yet, renders exactly as before (line is simply omitted, not a placeholder/zero). This is
the one figure from the Life Confidence pillar's "peace of mind" framing worth surfacing on the
cross-module dashboard specifically, not buried inside Goals — kept deliberately small (one new
helper function, one new line in the existing row template), not a restructure of the card.

Verified via real headless-Chromium (Playwright): seeded `goals_data_v1` with one Emergency-fund
goal (₹50,000/mo expenses, ₹2,10,000 tagged, 9 months wanted) and one unrelated Retirement goal —
confirmed the coverage line reads exactly "Emergency fund: 4.2 of 9 months covered" and appears
exactly once (not duplicated onto the other goal).

**Found, not fixed, flagged for a future session**: this file's own `projectGoal()` (line ~276)
is a verbatim-at-the-time copy of `goals/index.html`'s function, but `goals/index.html` switched
its SIP math to the annuity-due convention on 2026-08-10 (earlier the same day) and this copy
was not updated to match — so Synthesis's per-goal "projected value"/on-track verdict can now
disagree slightly with what Goals itself shows for goals with a monthly contribution. The
months-covered figure added here is unaffected (it only uses `currentValue`, which didn't
change), but the drift is real and worth a dedicated small fix in a future session — out of
scope for this task since it's unrelated to the emergency fund work and the task's own
instruction was not to restructure this card wholesale.

## Built (2026-08-11) — Financial independence card (Life Confidence pillar item 2)
The "one combined projection across debts, investments, and goals: the date work becomes
optional" item from `MASTER_ROADMAP.md`'s Life Confidence pillar. New card + overview tile in
`synthesis/index.html`; own data lives in `synthesis_data_v1.fi` (own key, same as the existing
income figure — never written into another module's key).

**Two dependency risks designed around up front, not discovered late:**
- **Double-counting between Net Worth and Portfolio.** Net Worth's `categories.investments` is
  manual-entry-only (no live sync from Portfolio), so a user could have the same holdings entered
  in both places. The card never sums Portfolio's tracked value + Net Worth's Investments total —
  it's a `<select>` the user picks explicitly ("Portfolio Tracker's tracked value" / "Net Worth's
  Investments category total" / "Manual entry"), each option showing its live figure inline, with
  the chosen source's label always shown next to the "Investable assets now" stat tile. Options
  with no data are `disabled` rather than hidden, so the choice itself stays visible. If a
  previously-picked source loses its data (e.g. holdings deleted), `effectiveAssetsSource()`
  falls back safely (portfolio → net worth → manual) rather than silently computing from stale
  zero data.
- **No general "monthly expenses" figure exists anywhere except inside an Emergency-fund goal.**
  If a goal has `category === 'Emergency fund'` and a real `efMonthlyExpenses` (built 2026-08-10),
  that value one-time-prefills this card's own `fi.monthlyExpenses` field — labeled explicitly
  ("From your '[goal name]' goal's essential-expenses figure... That's essential spend only... a
  realistic full retirement/FI budget may run higher"), with a "use this" link to re-pull the
  live figure later, and the field stays fully editable/overridable afterward. If no such goal
  exists, the field is a fresh manual entry with the same "self-reported, no other source"
  framing the Emergency Fund calculator itself uses — no fabricated figure.

**Inputs, all visible/editable, none silently assumed** (stored in `synthesis_data_v1.fi =
{assetsSource, manualAssets, monthlyInvestment, expectedReturn, monthlyExpenses, multiple}`):
- Investable assets source (above).
- Monthly investment — one-time-prefilled from the sum of Goals' own `monthlyContribution`
  values, labeled "From your tracked goals' planned contributions... not a full income/savings-
  rate figure," with a "use this" re-sync link; fully editable.
- Expected return — the SAME `RISK_PROFILES` preset list `goals/index.html` defines (Conservative
  6.5% / Balanced 8.5% / Aggressive 11.5%), copied verbatim into this file (not referenced cross-
  file, per this app's self-containment convention) so presses fill the field without locking it,
  exactly like Goals' own SIP calculator.
- Monthly expenses target (above).
- FI multiple (withdrawal-rate assumption) — editable, defaults to 25 (the standard "4% safe
  withdrawal rate" rule of thumb), with its known limitations disclosed directly in-UI: sourced
  from research on ~30-year retirement horizons against US market data, sequence-of-returns risk
  not modeled, and it doesn't specifically account for this app's own irregular/contract-based
  income context.

**The projection**: a NEW function, `monthsToReachTarget()`, using the same annuity-due SIP
convention `goals/index.html`'s `projectGoal()` was fixed to use on 2026-08-10 (each month's
contribution compounds as if invested at the start of that month) — solved in reverse (given a
monthly rate/contribution, find the month count until FV first crosses a target, rather than FV
at a fixed date), since "when do I become FI" is the inverse question `projectGoal()` answers.
Deliberately NOT calling into or fixing this same file's own `projectGoal()` (used by the Goals
card above) — that copy is still the pre-2026-08-10 stale ordinary-annuity formula (flagged in
this file's 2026-08-10 entry below), and fixing it was explicitly out of scope for this task per
its own regression requirement that the Goals/Net Worth/Portfolio/Debt/Insurance cards must not
change. `monthsToReachTarget()` is a fresh, independent calculation instead, so the FI projection
can be correct without touching another card's numbers. The stale-`projectGoal()` drift remains a
real, still-open item for a dedicated future session.

**Hand-traced verification example**: current assets ₹20,00,000 (from a seeded Portfolio holding),
monthly investment ₹50,000 (from a seeded goal's `monthlyContribution`), 8.5% expected return,
₹60,000/month expenses (from a seeded Emergency-fund goal's `efMonthlyExpenses`), 25× multiple →
FI target ₹1,80,00,000. By hand: `B = pmt·(1+r)/r ≈ 71,08,824`, `A = current + B ≈ 91,08,824`,
`months = ln((target+B)/A) / ln(1+r) ≈ 143.66` months (≈11.97 years) → `addMonths(today, round(143.66)=144)`
= **11 Aug 2038** from a run dated 11 Aug 2026. The app matched this exactly in a real headless-
Chromium check.

**Tested** with a real headless-Chromium (Playwright) suite (43 checks): the hand-traced example
above matched exactly; switching the assets-source `<select>` between portfolio/net-worth/manual
recomputes the projection correctly and never sums two sources (explicitly checked that
20L+5L=25L never appears); the Emergency-fund-sourced expense suggestion is labeled and
overridable, and its absence produces the honest "self-reported, no other source" copy instead of
a silent default; a zero-return + zero-contribution + zero-asset scenario renders "Not reachable
with current assumptions" rather than a fabricated date, in both the card and the overview tile;
an already-sufficient-assets scenario renders "You're already there"; a fully-empty-app scenario
renders the honest "enter your monthly expenses" prompt, not a bare/undefined date; mobile
(375×812) with no text under 13px anywhere in the card and no horizontal scroll (one real gap
found and fixed here: `.field label`'s existing mobile CSS was 12.5px sitewide in this file,
below the visual-design skill's floor — bumped to 13.5px, which also fixes the pre-existing
Insurance-card income label at that size); light and dark themes; and a full regression pass
confirming Net Worth, Portfolio, Goals, Debt & Loan, and Insurance cards render identically to
before (byte-level localStorage read-only guarantee re-verified: `goals_data_v1`/
`portfolio_data_v1`/`networth_data_v1` untouched after all FI-card interaction, including source
switches and manual overrides).

**Known gap carried forward, not introduced here**: this file's `projectGoal()` (used only by the
Goals card) is still the pre-2026-08-10 ordinary-annuity formula, not the annuity-due fix Goals
itself uses — see the 2026-08-10 entry below. The new FI math above sidesteps this by not reusing
that function at all.

## Updated (2026-08-11, reviewer fix) — negative expected-return bug in `monthsToReachTarget()`
`financial-os-reviewer` audited commit 38d4b6e (the Financial independence card above) and found one
real bug in `monthsToReachTarget()`: it branched on `if(monthlyRate<=0)` and always used a linear,
growth-free approximation (`(target-current)/pmt`) in that branch — correct only for exactly `r===0`,
but silently wrong for a genuinely negative `expectedReturn`. Nothing in the UI stops a user from
typing a negative return (the "Expected return" field is free-text `%`, no `min` attribute). For the
reviewer's exact repro (current ₹10,00,000, ₹20,000/month, target ₹1,80,00,000, -5% expected return),
the app previously reported a confident "850 months → 11 Jun 2097" — a fabricated headline number for
a scenario where, under true negative compounding, the target is never reached at all (contributions
asymptote toward a finite ceiling below the target). Exactly the "confidently wrong headline number"
failure mode this whole feature exists to prevent.

**Why the obvious fix (just widen the r>0 closed form to cover r<0) doesn't work**: the closed-form
inversion (`B = pmt*(1+r)/r`, `A = current+B`, solve via `ln((target+B)/A)/ln(1+r)`) relies on `A<=0`
as its only "not reachable" guard. For negative r, `B` isn't small — it's `pmt*(1+r)/(-r)`, which is
the *actual finite ceiling* the balance asymptotes toward, and for small `|r|` this ceiling is huge, so
`A = current - ceiling` goes deeply negative even when the target is well below that ceiling and *is*
genuinely reachable in a few years. Verified by hand-simulation: widening the closed form to `r<0`
wrongly reported "not reachable" for a -0.1%/year case that direct month-by-month simulation shows
reaches its target in ~54 months. This isn't just floating-point cancellation for tiny `|r|` — the
`A<=0` check is simply the wrong reachability condition once `r` is negative.

**Fix applied** (a hybrid of the reviewer's two suggested approaches, chosen to be both correct and
zero-risk to the already-verified r>0 path): `monthlyRate===0` and `monthlyRate>0` are now separate,
untouched branches (byte-identical logic/output to before — re-verified against the documented
₹20,00,000/₹50,000/8.5%/₹60,000/25× → 11 Aug 2038 example, which still matches exactly). A NEW
`monthlyRate<0` branch was added that:
1. Returns "not reachable" immediately if there's no contribution (`pmt<=0`) — with no growth and no
   contribution, and `currentValue<target` already established above, the balance can only shrink.
2. Computes the true finite ceiling `L = pmt*(1+r)/(-r)` the balance asymptotes toward as months→∞
   (proven algebraically: `(1+r)^n → 0` since `0<1+r<1` for `-1<r<0`) and returns "not reachable"
   immediately, mathematically (not just "not found within a search window"), if `target>=L`.
3. Otherwise (target below the ceiling, so a crossing is mathematically guaranteed to exist),
   bisects over the SAME forward annuity-due FV formula used everywhere else in this app
   (`current*(1+r)^n + pmt*(1+r)*((1+r)^n-1)/r`, evaluated directly via `Math.pow` rather than
   rearranged into the cancellation-prone `A*(1+r)^n - B` form), capped at 1200 months (100 years) as
   an outer safety bound in case a target sits absurdly close to the ceiling.

**Verified — independent ground-truth simulation, not just trusting the new code**: wrote a standalone
month-by-month simulator (`FV(n) = (FV(n-1)+pmt)*(1+r)`, the same annuity-due recursion, evaluated as a
literal loop with no closed-form shortcuts at all) and cross-checked it against the fixed function
across a matrix of cases before touching the app file:
- Reviewer's exact -5%/year case (₹10,00,000 / ₹20,000/mo / ₹1,80,00,000 target): both the simulator
  (out to a 1000-year cap) and the fixed function agree — never reached. No confident date.
- -0.1%/year edge case (constructed with a smaller gap so it's genuinely reachable — ₹1,70,00,000 /
  ₹20,000/mo / ₹1,80,00,000 target): simulator crosses at month 54; fixed function returns 53.94
  (rounds to 54) — matches. Also checked -0.01%/year and -0.0001%/year on the same inputs: both
  correctly reachable (~50-51 months), confirming the fix isn't just accidentally right at one rate.
- Positive-rate regression, byte-for-byte: the documented 8.5%/₹20,00,000/₹50,000/₹1,80,00,000 example
  still returns exactly `143.65591010201672` months (same float, to the last digit, as before the fix)
  — the r>0 branch was never touched.
- `monthlyRate===0` (typed literally "0"): unaffected, still the exact pre-existing linear formula
  (400 months for a hand-picked gap/pmt pair, checked against `(target-current)/pmt` by hand).
- Checked the adjacent edge the reviewer flagged as worth double-checking (a rate that rounds to
  effectively zero from floating point vs literal `0`): `expectedReturn/12/100` for an input of `"0"`
  or `"-0"` produces exactly `0`/`-0` in JS, and `-0===0` is `true` in JS while `-0<0` is `false`, so
  both land in the untouched `monthlyRate===0` branch correctly — no adjacent fragility found. Tiny
  *positive* rates were already reviewer-confirmed solid and are untouched by this fix (still the r>0
  branch).

**Real headless-Chromium (Playwright) suite, seeding `synthesis_data_v1.fi` directly** (own module's
data, not another module's — no cross-module writes involved in testing): confirmed in a real browser,
not just node math —
- -5%/year case → verdict is "Not reachable with current assumptions" (no date at all), matching the
  ground-truth simulation.
- -0.1%/year case (₹1,70,00,000/₹20,000/₹1,80,00,000 target) → verdict is a concrete date ("11 Feb
  2031", 54 months from today 2026-08-11), NOT "not reachable" — confirms the fix is granular, not a
  blanket "all negative rates unreachable" shortcut.
- Full regression, all re-run in-browser and all still exactly correct: the documented ₹20,00,000/
  ₹50,000/8.5%/₹60,000/25× example → "11 Aug 2038" (today is 2026-08-11, so this is the exact same
  ~144-month projection as the original build); zero-return/zero-contribution/zero-asset → "Not
  reachable with current assumptions"; already-sufficient-assets → "You're already there"; the
  assets-source picker (portfolio/net worth/manual) still never sums two sources (checked a seeded
  portfolio holding worth ₹20,00,000 alongside a seeded Net Worth Investments row worth ₹5,00,000 —
  switching the source selector shows one or the other, never ₹25,00,000); the Emergency-fund
  expense-sourcing hint and its "use this" sync link still populate the monthly-expenses field
  correctly. Zero console/page errors across every run.
- Also spot-checked mobile (375×812) and both themes for the FI card and Emergency-fund sync flow
  specifically — no new sub-13px text introduced by this change. **Found, not fixed (pre-existing,
  unrelated to this fix, confirmed via `git stash` that it predates this change)**: a generic `.tag`
  element (used for "No target set" on the Goals card, loan-type tags on the Debt card, and the
  income-adequacy tag on the Insurance card) renders at 12px on mobile, below this app's 13px floor —
  out of scope for this bug fix, worth a small dedicated pass in a future session.

No UI copy changes were needed — the existing "Not reachable with current assumptions" honest message
(already used for the zero-input case) now also correctly covers genuinely-unreachable negative-return
scenarios, and the existing date-rendering path now correctly covers reachable negative-return
scenarios. Only `monthsToReachTarget()` itself changed; nothing else in `synthesis/index.html` was
touched.

## Known gaps
- This page reads `localStorage` once at load time, not reactively — if you
  add data in another module in a different tab, use the "↻ Refresh"
  button (or reload) to see it reflected here. No `storage` event listener
  was added since this is a simple read-once dashboard, not a live sync
  tool; revisit if that friction turns out to matter in practice.
- No export/import on this page — nothing to back up, since it owns no
  data of consequence beyond the income figure and the FI assumptions
  (all trivially re-enterable).
- Debt-free date is only as accurate as Loans' own amortization formula,
  which (per `loans/index.html`'s own comment) doesn't re-amortize after
  prepayments — an approximation, not a schedule.
- The FI projection assumes a roughly steady monthly investment and return
  — disclosed in-UI — and doesn't model an income-shock scenario (delayed
  contracts, lump-sum gaps). That's a separate, later Life Confidence
  pillar item ("Income-shock stress test"), not built here.
- ~~A generic `.tag` element (Goals card's "No target set", Debt card's loan-type tags, Insurance
  card's income-adequacy tag) renders at 12px on mobile — below this app's 13px floor.~~ **Fixed
  2026-08-11** in the app-wide font-size/contrast/consistency pass (see dated entry below) — `.tag`
  is now 13px in both the desktop base rule and the mobile override.
- `projectGoal()` in this file (used only by the Goals card) is still the
  pre-2026-08-10 stale ordinary-annuity formula — a real, known drift from
  `goals/index.html`'s own annuity-due fix, carried forward again from the
  2026-08-10 entry above. The new FI card's math is independent of this
  function specifically so it isn't affected, but the drift itself is
  still unfixed and worth a dedicated future session.

## Design invariants (same as every module)
- Zero external dependencies, works offline once loaded.
- Shared theme key with the rest of the app: `itrgenie_theme`.
- Own data storage key: `synthesis_data_v1` — the manual income figure
  plus, as of 2026-08-11, the `fi` sub-object (assets-source choice,
  manual-assets override, monthly investment, expected return, monthly
  expenses, FI multiple) — never writes to any other module's key.
- Guided single-field form for the one piece of manual entry (annual
  income), consistent with how Insurance Tracker's own context fields work
  — no paste/CSV needed for a single scalar value.

## Updated 2026-08-11 — App-wide font-size/contrast/consistency pass
Direct, blunt user feedback: font sizing hard to see "in places," color scheme needs
improvement, across the whole app — flagged repeatedly this session (including this file's own
"Known gaps" list, twice) and deferred as out-of-scope until now. This pass closes both of this
file's own dangling `.tag` gap entries (see the struck-through bullet above) and does the same
fix everywhere else in the app.

**17 sub-13px `font-size` declarations raised to 13px** (full grep sweep, not just the
already-flagged `.tag`): `.brand .sub` 11px→13px, `.panel-header .eyebrow` 11px→13px,
`.card .card-sub` 12px→13px, `.field label` 11px→13px, `.notice` 12.5px→13px, `.btn` 12px→13px,
`.btn.small` 11px→13px, `.stat-tile .stat-label` 11px→13px, `.stat-tile .stat-note` 11.5px→13px,
`.helptext` 12.5px→13px, `.breakdown-bar .seg` 10px→13px, `.legend .item` 12px→13px, `.tag`
10px→13px (desktop) and 12px→13px (the mobile override — the specific gap this file's own Known
gaps list had flagged twice), `.item-row-sub` 12px→13px, plus the mobile-only `.panel-header
.eyebrow` 11.5px→13px and `.brand .sub` 12px→13px overrides.

**Cross-module consistency**: `--bg/--panel/--panel-2/--line/--text/--muted/--gold/--gold-dim/
--green/--rust` hex values (both themes) diffed byte-for-byte against every other module —
already identical here, no drift found.

**Contrast**: `--muted` against `--bg`/`--panel`/`--panel-2` computed (not eyeballed) — 6.5–7.4:1
dark, 4.9–5.7:1 light (this file's `--panel-2` case is the tightest margin of any module at
4.91:1, still clears WCAG AA's 4.5:1 by a real margin). No change needed.

**Tested with real headless-Chromium (Playwright)**: full DOM text-node sweep at 375px and
1280px, both themes, on initial load (empty-state, since this page has no data of its own — it
reads every other module's `localStorage`) — 0 nodes under 13px, 0 console errors. No JS logic
touched, CSS values only, so the read-only cross-module rendering this page depends on is
unaffected.
