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
- Dropped-click/data-loss repro, now fixed: typing into `g_name` (unblurred) then clicking "Parse &
  add" adds the investment, commits the in-flight name edit, *and* renders "1 investment added." in
  `#inv_fb`; typing into `g_infl` then moving straight into the paste textarea and typing there
  preserves that text, the earlier `g_infl` edit, and parses correctly once submitted.
- Keyboard-only: Tab+Enter and Tab+Space independently verified on all 8 preset buttons (2 cost-mode,
  3 inflation-preset, 3 risk-preset) — each actually changes goal state; a plain mouse click on the
  same buttons still works and does not double-fire/double-add.
- Annuity-due note: appears once near the projection, dismiss button hides it and persists the flag.
- Regression: inflation FV, annuity-due SIP (₹1,28,093 for the ₹10,000/mo·12%·12mo example), and the
  risk-profile table (Conservative 6.5% → ₹28,147/mo, matches the corrected worked example below,
  declining correctly as return rises) all unchanged; a goal with no `costMode`/`presentCost`/
  `inflationRate` fields at all still computes and displays correctly (backward compatibility intact).

## Design invariants (same as ITRGenie/Net Worth)
- Zero external dependencies, works offline once loaded.
- Paste-and-file-upload dual input mode (CSV/TXT via FileReader, same parser
  as paste — not a separate code path).
- Shared theme key: `itrgenie_theme`.
- Assumptions (inflation rate, assumed return) are always shown as editable
  fields with a visible suggested default — never applied silently. Presets
  (risk profile, inflation category) fill the field, they don't lock it.
