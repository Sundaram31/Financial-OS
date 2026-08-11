# Goals — Progress

## What this is
Standalone tool (`index.html`), same design system as ITRGenie/Net Worth.
Multi-goal support: each goal has a target amount/date, its own tagged
investments (paste or CSV/TXT file upload), a planned monthly contribution,
and an assumed annual return — from which progress % and an on-track/behind
projection are computed.

## Built (2026-08-03)
- Add/expand/delete goals, one card per goal, click to expand.
- Tagged-investments ledger per goal (paste or file upload).
- Projection math: current tagged corpus compounds at assumed rate + monthly
  contributions compound as an annuity (computed separately, not blended) —
  gives projected value at target date, and if short, the required monthly
  contribution to actually hit the target on time.
- Export/Import JSON, own storage key (`goals_data_v1`), shared theme key
  with ITRGenie/Net Worth Dashboard.

## Updated 2026-08-11 — file upload widened to accept Excel
`inv_file` (the tagged-investments file upload) now accepts
`.csv,.txt,.xlsx,.xls`, not just CSV/TXT. Vendored a module-own copy of
SheetJS (`lib/xlsx.core.min.js`, ~427KB, self-hosted, no CDN -- same pattern
already used by `itrgenie/` and `portfolio/`) and extended `wireFileUpload`
to convert an uploaded `.xlsx`/`.xls` file's first sheet to CSV text via
`XLSX.utils.sheet_to_csv` before handing it to the exact same "Label, Value"
row parser the paste box and plain-CSV upload already use -- no new parsing
logic, same rows either way. Tested end-to-end (Playwright): an Excel file
with two Label/Value rows imports identically to the equivalent CSV; CSV/TXT
path re-verified unchanged.

## Deliberately NOT done yet
- No cross-goal validation that the same holding isn't tagged to two goals
  (documented as a user responsibility in the UI copy for now).
- No connection to Net Worth Dashboard or Portfolio Tracker — tagged
  investments are entered independently here. Once Portfolio Tracker is
  migrated, tagged investments could pull live current values instead of a
  manually-entered snapshot.

## Built (2026-08-10) — inflation-adjusted targets, risk-profile SIP presets, annuity-due fix
Real goal-planning calculator added on top of the existing per-goal structure
(`projectGoal()`, tagged investments, on-track projection) — two things users
explicitly asked for were missing, plus a formula-correctness fix:

**1. Present-day cost → inflation-adjusted future target.** Each goal now has
a "Target amount — how do you know it?" toggle: *Enter amount directly*
(unchanged, default for existing goals) or *Calculate from today's cost +
inflation*. In the second mode the user enters a present-day cost and an
inflation rate; the effective target used everywhere (progress bar, on-track
verdict, required-monthly math) becomes `presentCost * (1+inflationRate/100)
^ years`, computed live off `targetDate` (not stored back into
`targetAmount` — always reflects the current inputs). Both numbers (today's
cost and the inflated future cost) are shown together, never just the
computed one. Inflation rate has category-aware presets — General/lifestyle
6.5% (6-7% range), Education 11% (10-12%, `Child education` category),
Healthcare 9% (8-10%, new `Healthcare/Medical` category added to the
category list) — auto-suggested from the goal's category but always a plain
editable number field, never silently applied.

**2. Risk-profile SIP presets.** Three buttons — Conservative/Debt (6.5%),
Balanced (8.5%), Aggressive/Equity (11.5%) — each *fills* the still-editable
"Assumed annual return" field rather than locking it. The projection card
now also shows a small "Required monthly contribution by risk profile"
table with all three profiles' numbers side by side (not just the currently
selected one), so the return/contribution tradeoff is visible directly
rather than requiring the user to click through each preset one at a time.

**3. Annuity convention fix (behavior change for every existing goal).**
`projectGoal()`'s SIP math previously used the *ordinary annuity* formula
(`pmt * (growthFactor-1)/monthlyRate`) — contributions credited at the END
of each month. Real Indian SIP calculators (Groww/ET Money-style) converge
on *annuity-due* — contributions invested at the START of each month — which
is `pmt * ((growthFactor-1)/monthlyRate) * (1+monthlyRate)`, and
`requiredMonthly` is divided by that same factor. This repo now matches
that convention. It's a real, deliberate correctness fix, not cosmetic:
**example** — ₹10,000/month, 12% assumed annual return, 12 months, starting
from ₹0: old (ordinary) formula → **₹1,26,825**; new (annuity-due) formula →
**₹1,28,093**. Every existing goal's "projected value" and "required
monthly" figures will shift by this same small amount (~1 month of
compounding) after this change — expected, not a bug.

**4. Disclosures.** Every goal with a target set now shows, right under the
projection: "This is an illustrative projection based on your own assumed
rate of return — not a guarantee, actual returns vary." plus the SEBI-style
"Mutual fund investments are subject to market risks; read all
scheme-related documents carefully." Small, muted, not a modal/banner —
matches Portfolio Tracker's live-price/CAS-import disclosure tone.

**Race-condition fix found during testing:** the app's existing pattern
(every field's `onchange` does a full `saveData(); render()`, replacing the
whole DOM) meant a real risk: type into a field, then — without clicking
elsewhere first — click an adjacent preset button, and the click could be
silently dropped (the blur-triggered re-render detaches the button between
the browser's mousedown and click phases, so the click event never fires;
confirmed via Playwright reproducing the exact mousedown→blur→detach
sequence). Fixed by binding the new cost-mode / inflation-preset /
risk-preset buttons to `mousedown` (which fires *before* the blur-triggered
rebuild) and having them explicitly read+commit any in-flight field edits
from the DOM first (`syncParamsFields()`), so a "type then immediately
click a preset" flow always commits both actions correctly regardless of
order. Verified with a dedicated Playwright test that types into a field and
clicks a preset button with no explicit blur in between.

**Verification (headless Chromium/Playwright, 15/15 checks):**
- Inflation FV: ₹15,00,000 today, 6.5%/yr, 10 years → app shows
  ₹28,15,706, matches hand-computed `1500000 * 1.065^10 = 2,815,706.20`.
- Risk-profile table for one goal (target ₹20,00,000, 60 months, ₹0
  current): Conservative 6.5% → ₹28,147/mo required, Balanced 8.5% →
  ₹26,677/mo, Aggressive 11.5% → ₹24,583/mo (declining as assumed return
  rises, correctly ordered).
- Annuity-due: ₹10,000/mo, 12%, 12 months → app shows ₹1,28,093 (matches
  hand calc above); confirmed different from the old ordinary-annuity
  figure (₹1,26,825).
- Mobile (375×812): no horizontal overflow, min font size 11px among
  small text (unchanged from the module's existing label/helptext sizing).
- Regression: a goal that never touches present-cost/inflation (direct
  target amount, paste-tagged investment) computes and displays exactly as
  before.

Data model additions to each goal object: `costMode` (`'direct'` default |
`'inflate'`), `presentCost`, `inflationRate` — all optional, all
backward-compatible (goals saved before this change have no `costMode` and
are treated as `'direct'`). New goal default `assumedReturn` changed from
`'10'` to `'8.5'` (Balanced preset) to match the new risk-profile framing —
existing goals' stored `assumedReturn` values are untouched.

## Updated 2026-08-10 — Second-pass reviewer fix: display/calc mismatch, dropped-click race, keyboard access
The `financial-os-reviewer` subagent independently audited the inflation/SIP-preset build above
(commit `cd11be9`) — confirmed the core math (inflation FV, annuity-due SIP, risk-profile table) is
correct — but found four real issues in how it's wired up. All four fixed same-day.

**1. Inflation-rate display disagreed with what was actually calculated.** With the inflation-rate
field empty (a realistic state — clear it to retype, click away), the helptext near the field fell
back to the *category preset rate* for display (e.g. "6.5%/yr"), while `effectiveTarget()` and the
projection card both fell back to **0%** for the actual math — the future-cost figure shown was
computed unchanged from today's cost, but the label next to it confidently claimed a nonzero rate.
Fixed: the display fallback now matches the calculation fallback (`||0`, not `||invPreset.rate`) in
both places (the inline future-cost helptext and the projection card's target line), and when the
rate is empty the copy explicitly says so — "Enter an inflation rate above to include inflation...
which understates what this will actually cost by the target date" — instead of silently showing a
number that isn't what's being used. Never auto-fills the field with the preset (that would violate
the "assumptions are never applied silently" invariant below); it just stops misdescribing 0%.

**2. Race-condition fix from the previous pass was real but incomplete, and the gap caused actual
data loss.** Two gaps confirmed via Playwright: (a) typing into any `onchange` field then clicking
the pre-existing "Parse & add" button without an intervening blur silently dropped the click — and
separately, `#inv_fb` was never actually rendered with the added/skipped result (dead code, always
empty); (b) typing into an `onchange` field then moving straight into the tagged-investments paste
textarea — a completely normal flow — silently lost whatever was typed into that textarea, because
the intervening full-card re-render recreated it from scratch before "Parse & add" was ever clicked.
Fixed with two changes: a `pasteDrafts` map (goal.id → in-progress paste text, updated on every
keystroke via `oninput`, never persisted to storage) rehydrates the textarea across *any* re-render
triggered elsewhere on the card, so nothing typed into it is ever silently dropped regardless of what
else changes first. "Parse & add" (and "Choose CSV/TXT file") now use the same reliable-button
pattern as the preset buttons (see #3) instead of a plain `onclick`, so the click itself is no longer
race-prone. Getting `#inv_fb` to actually render surfaced a second, subtler bug: removing a
currently-focused, edited field via the render's `innerHTML=''` fires that field's own blur→change
*reentrantly*, nesting a second `render()` inside the first — and since the one-shot `invFeedback`
message was being deleted the instant it was read, the nested (ultimately-discarded) pass consumed
it before the real, final pass ever got to show it. Fixed by deferring the delete to `setTimeout(fn,
0)` so every render pass within the same synchronous burst can see the message, and only the next
tick clears it — still shown exactly once, never lost, never stuck.

**3. The 8 new preset buttons were keyboard-inoperable.** Binding them to `mousedown` (the previous
pass's race fix) meant Enter/Space on a focused button did nothing, since `mousedown` never fires for
keyboard activation. Fixed by splitting the two concerns: `mousedown` now calls `e.preventDefault()`
(which blocks the browser's default focus-shift, so the currently-focused field never blurs and never
fires an unrelated re-render that would detach the button before its own `click` can fire) plus syncs
any in-flight field edits as a safety net; the actual state change (cost mode / inflation preset /
risk preset / parse-and-add / choose-file) now happens in a `click` handler, which fires reliably for
*both* pointer and keyboard activation. Verified with real keyboard-only interaction (Tab to each of
the 8 buttons, press Enter or Space, confirm state actually changes) — not just that the code compiles.

**4. One-time note about the annuity-due formula change.** The 2026-08-10 SIP formula switch (see
above) can silently flip an existing goal's status from "Behind" to "On track" purely from the
formula change — previously undisclosed anywhere in-app (only in this file, which no end user reads).
Added a small, dismissible note right under the projection, shown until the user clicks "Got it"
(flag in `localStorage['goals_annuity_note_dismissed_v1']`, not part of exported/imported goal data):
"We updated how monthly SIP figures are calculated to match industry-standard calculators (Groww/ET
Money-style annuity-due) — projected numbers may look slightly different than before."

**Verification (headless Chromium/Playwright, 33/33 new checks + all 15/15 checks from the prior
pass still passing, zero regressions):**
- Inflation display/calc agreement: empty rate → `effectiveTarget()` returns exactly `presentCost`
  (0% applied) and the on-page text neither claims a nonzero rate nor omits the "enter a rate" note;
  non-empty rate (6.5%/10yr) → display and calc both show the same ₹28,15,706 figure.
- Dropped-click repro, fixed: typing into `g_name` (unblurred) then clicking "Parse & add" adds the
  investment, commits the in-flight name edit, *and* renders "1 investment added." in `#inv_fb`.
- **Correction (2026-08-10, third-pass reviewer)**: the claim above that typing into `g_infl` then
  moving straight into the paste textarea "preserves that text" was wrong as originally tested —
  the reentrant-render fix protected text *already in* the textarea across further re-renders, but
  not the initial focus transition *into* it: the synchronous `render()` on a field's `onchange`
  could tear down and rebuild the textarea mid-click/mid-Tab, interrupting the browser's own
  focus-shift and leaving nothing focused, so a keystroke or paste right after silently landed
  nowhere (confirmed via `document.activeElement`, not just draft-map state). Fixed by deferring
  that `render()` by one tick (`setTimeout(render, 0)` instead of a synchronous call) so the
  browser finishes moving focus before the DOM gets rebuilt. Re-verified with the same real
  mouse+keyboard reproduction that first caught it, including the multi-hop draft-preservation
  case and a same-tick rapid-interaction stress test.
- Keyboard-only: Tab+Enter and Tab+Space independently verified on all 8 preset buttons (2 cost-mode,
  3 inflation-preset, 3 risk-preset) — each actually changes goal state; a plain mouse click on the
  same buttons still works and does not double-fire/double-add.
- Annuity-due note: appears once near the projection, dismiss button hides it and persists the flag.
- Regression: inflation FV, annuity-due SIP (₹1,28,093 for the ₹10,000/mo·12%·12mo example), and the
  risk-profile table (Conservative 6.5% → ₹28,147/mo, matches the corrected worked example below,
  declining correctly as return rises) all unchanged; a goal with no `costMode`/`presentCost`/
  `inflationRate` fields at all still computes and displays correctly (backward compatibility intact).

## Built (2026-08-10) — Emergency fund adequacy calculator (Life Confidence pillar item 1)
Built the highest-ranked item from `MASTER_ROADMAP.md`'s Life Confidence pillar: "6-12 months
of true liquid expenses, not 'some savings somewhere'." Scoped deliberately as a sub-flow inside
the existing `Emergency fund` goal category (already one of `GOAL_CATEGORIES`), not a new
auto-computed figure — checked Net Worth's actual data model first and confirmed it has no
monthly-expenses field and no liquidity classification (its "Investments" category bundles
genuinely liquid FDs/liquid funds together with retirement-locked EPF/PPF), so an auto-derived
number would have silently misrepresented locked money as available cash. The existing per-goal
tagged-investments mechanism already represents "what the user has explicitly earmarked" — the
right model here, since deciding what counts as "liquid enough for an emergency" is the user's
own judgment call, not something to auto-derive.

**What was built**, only shown when a goal's `category === 'Emergency fund'`, positioned right
above the existing "Target amount — how do you know it?" section (a normal goal in every other
respect — target/date, tagged investments, projection all still apply):
- **Two new manual inputs**, both explicitly labeled as unconnected to any other module's data:
  `efMonthlyExpenses` (₹, plain number field, no pre-fill — "your own estimate of essential
  monthly spend — rent/EMI, food, utilities, insurance premiums... not discretionary spending")
  and `efMonthsWanted` (range slider 6-12 plus three tap presets — 6/9/12 — defaulting to **9**,
  not the generic 6-month minimum, since this app's own seafarer/contract-income context is
  exactly the profile personal-finance guidance says should lean toward the higher end).
- **Recommended target** = `efMonthlyExpenses × efMonthsWanted`, shown as a suggestion with a
  "Use ₹X as target amount" button that fills the goal's real `targetAmount` field and switches
  `costMode` to `'direct'` — only on explicit click, never automatically; the target field stays
  untouched (verified empty) until that button is pressed.
- **Months-covered figure** — the actual peace-of-mind number: `currentTaggedValue /
  efMonthlyExpenses`, reusing the goal's own existing tagged-investments total (no new liquidity
  classification invented — tagging an investment to an Emergency fund goal already *is* the
  user's own liquidity judgment). Shown prominently as a large stat ("4.2 of 9 months") with a
  calm three-tier color: red/rust under 3 months, gold/amber from 3 up to the chosen months-
  wanted, green at or above it.
- **Explicit warning copy**, matching the roadmap's own framing near-verbatim: "This is only as
  good as what's actually tagged below. Retirement-locked money (EPF/PPF) or anything not
  genuinely accessible on short notice shouldn't be tagged here even if it shows up in Net Worth
  or Portfolio — the point is true liquid coverage, not 'some savings somewhere.'"

Data model additions to each goal object: `efMonthlyExpenses`, `efMonthsWanted` — both optional,
backward-compatible (fallback `efMonthsWanted||9` used for display when unset, never persisted
until the user actually touches the slider/preset/field).

**Implementation notes**: reused the existing `bindSyncedButton()` pattern (mousedown syncs
in-flight field edits + blocks focus-loss, click commits + re-renders, works for both pointer
and keyboard activation) for the new months-wanted preset buttons and the "Use as target" button,
so this doesn't reopen the dropped-click/keyboard-inaccessible bugs fixed earlier the same day.
The "Use as target" button's apply function recomputes the recommended figure fresh from `goal`
at click time (not the render-time closure variable) since `syncParamsFields()` runs first and
may have just committed an unblurred edit — verified by test that typing into the expense field
then immediately clicking works correctly.

**Verification (headless Chromium/Playwright, 30/30 checks)**: calculator appears only for
Emergency-fund-category goals and disappears immediately on switching category away (and back);
zero-expense state shows a plain "enter monthly expenses" hint, never `NaN`; zero-tagged-
investments state shows "0.0 of 9 months" (not `NaN`/`Infinity`), correctly tiered red; hand-
traced example — ₹50,000/mo expenses, ₹2,10,000 tagged (one "Savings account" investment) →
**4.2 of 9 months covered**, tiered gold/"Building coverage" (matches `210000/50000 = 4.2`
exactly, and matches the worked example in the roadmap task itself); recommended target
₹50,000 × 9 = **₹4,50,000** shown correctly, target field confirmed empty until the "Use as
target" button is explicitly clicked, then confirmed filled to exactly `450000` and `costMode`
switched to `direct`; low-tier (2.1 months, ₹1,00,000/mo expenses) and adequate-tier (10.5
months, ₹20,000/mo expenses) boundaries both verified against the same ₹2,10,000 tagged total;
months-preset buttons (6/9/12) and keyboard Tab+Enter activation both verified; an in-flight,
unblurred edit to the expenses field survives clicking an unrelated risk-profile preset button
elsewhere on the same card (no data loss, matching the race-condition fix pattern already
established for this module); regression — a non-Emergency-fund goal (tested: default "Other"
and "Child education" with inflation mode active) never shows the calculator, and existing
inflation/risk-profile functionality is unaffected; mobile (375×812) — no horizontal overflow,
no text below 11px; both themes render correctly.

**Small Synthesis Layer touch** (see `synthesis/PROGRESS.md`): Synthesis's existing Goals card
now surfaces this same months-covered figure for Emergency-fund-category goals specifically
("Emergency fund: 4.2 of 9 months covered", same tier coloring), additive to the existing
progress-bar treatment every other goal category still gets unchanged.

**Deliberately not fixed here, flagged for a future session**: while building the Synthesis
touch, found that `synthesis/index.html`'s own copy of `projectGoal()` still uses the *old*
ordinary-annuity SIP formula, not the annuity-due fix this module (`goals/index.html`) switched
to on 2026-08-10 earlier the same day — the two modules' "current tagged value" figures (used
here) agree, since that math didn't change, but their *projected future value* / on-track
figures can now disagree slightly. Out of scope for this task (unrelated to the emergency fund
feature) and touching it risks the "don't restructure Synthesis's Goals card wholesale"
instruction — noted here as a real, found gap rather than silently left for someone to discover.

### Fix (2026-08-10, same day) — reviewer-found visual-emphasis gap
`financial-os-reviewer` audited this feature and confirmed the math, category-gating, edge cases,
and Synthesis parity all correct — no wrong-but-confident number found anywhere. One real ease-of-
operation gap: the EPF/PPF liquidity warning (the single sentence this whole feature's correctness
depends on) was styled identically to five other pieces of throwaway `.helptext` on the same card,
not visually elevated as a caution. Fixed by giving it the same `.notice.warn` rust-bordered callout
treatment already established in `portfolio/index.html` (added the same CSS rules here, this module
didn't have them yet) — now visually distinct rather than blending into ordinary muted copy.
Verified via headless Chromium: the callout renders with the correct rust border/background, and the
months-covered figure is unaffected by the change (still 4.2 for the same example as above).

## Design invariants (same as ITRGenie/Net Worth)
- Zero external dependencies, works offline once loaded.
- Paste-and-file-upload dual input mode (CSV/TXT via FileReader, same parser
  as paste — not a separate code path).
- Shared theme key: `itrgenie_theme`.
- Assumptions (inflation rate, assumed return) are always shown as editable
  fields with a visible suggested default — never applied silently. Presets
  (risk profile, inflation category) fill the field, they don't lock it.
