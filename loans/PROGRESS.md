# Debt & Loan Tracker — Progress

## What this is
Standalone tool (index.html), same design system as rest of Financial OS.
First real implementation of the "Financial Events extraction" vision --
scoped to loans specifically because EMI/prepayment is 100% derivable from
bank statement data alone (unlike capital gains, which needs broker/CAMS
source data for security-level detail).

## Built (2026-08-07)
- Loan CRUD: lender, type, principal, rate, EMI.
- Bank-statement paste/file-upload with pattern-based EMI/prepayment
  detection -- reuses the validated classifier approach from AIS
  Reconciliation session work (98.7% accuracy on real data, description-text
  only, no reliance on a pre-existing category column).
- Amortization-based payoff projection from outstanding balance + EMI.
- Export/Import JSON, own storage key (loans_data_v1), shared theme.

## Updated 2026-08-11 — file upload widened to accept Excel
`l_file` (bank-statement file upload) now accepts `.csv,.txt,.xlsx,.xls`,
not just CSV/TXT. Vendored a module-own copy of SheetJS
(`lib/xlsx.core.min.js`, self-hosted, no CDN -- same pattern as `itrgenie/`
and `portfolio/`). `wireFileUpload` now converts an uploaded `.xlsx`/`.xls`
file's first sheet to CSV text via `XLSX.utils.sheet_to_csv` before handing
it to the same callback the CSV/TXT path already used -- the pattern-based
EMI/prepayment classifier downstream is completely untouched. Tested
end-to-end (Playwright): CSV and Excel versions of the same statement row
land in the paste textarea as byte-identical text, and "Scan & add" detects
the same payment either way; CSV/TXT path re-verified unchanged.

## Known limitations, stated plainly in the UI
- Payoff projection doesn't re-amortize after each prepayment -- directional
  estimate, not exact.
- For Sec 24(b) interest deduction, use the actual bank interest certificate,
  not this tool's estimate.
- EMI vs prepayment classification during bulk-paste is heuristic (smaller
  recurring figure = EMI, larger lump sum = prepayment) -- always shown for
  review, never auto-committed without the user seeing the detected list.

## Queued next (Financial Events vision, remaining pieces)
1. FD/RD lifecycle tracker (open, contributions, maturity date/amount) --
   also 100% bank-derivable, same classifier pattern.
2. Investment cash-flow ledger (SIP totals by fund house/broker) -- feeds
   Net Worth Dashboard's Investments category instead of manual entry.
3. Insurance premium ledger -- premiums from bank data, maturity/lapse date
   needs one-time policy document capture (not derivable from bank alone).
4. Capital gains explicitly stays OUT of self-computation -- bank data can
   only flag that a sale event happened, not compute the gain (no security/
   quantity/price in bank transaction descriptions).

## Updated 2026-08-11 — App-wide font-size/contrast/consistency pass
Part of an exhaustive, whole-app pass (every module touched the same day) responding to direct
user feedback that font sizing is hard to see and the color scheme needs improvement everywhere.

**7 sub-13px `font-size` declarations raised to 13px**: `.brand .sub` 11px->13px,
`.panel-header .eyebrow` 11px->13px, `.field label` 11px->13px, `.btn` 12px->13px,
`.btn.small` 11px->13px, `table.day-table th` 11.5px->13px, `.helptext` 12.5px->13px.

**Real cross-module inconsistency found and fixed**: this file was missing the
`.btn.primary:hover{ background:#dab63a; }` rule every other module has -- the primary button
(e.g. "+ Add a loan") had no lighter-gold hover state here, unlike everywhere else in the app.
Added, matching the other modules byte-for-byte.

**Cross-module consistency (colors)**: `--bg/--panel/--panel-2/--line/--text/--muted/--gold/
--gold-dim/--green/--rust` hex values (both themes) diffed byte-for-byte against every other
module -- already identical, no drift found there.

**Contrast**: `--muted` against `--bg`/`--panel`/`--panel-2` computed at 6.5-7.4:1 dark,
4.9-5.7:1 light -- already passes WCAG AA (4.5:1) in both themes.

**Tested with real headless-Chromium (Playwright)**: full DOM text-node sweep at 375px and
1280px, both themes -- 0 nodes under 13px, 0 console errors. Functional regression: "+ Add a
loan" flow re-verified (new loan card renders with editable fields, hover state now present) --
no JS logic touched, CSS values only.

## Updated 2026-08-11 -- Statement paste made tolerant of date-format variation; a real amount-misread bug found and fixed
Same app-wide audit as `itrgenie/`, `goals/`, `networth/` (see `itrgenie/PROGRESS.md`'s matching
entry for the full rationale). This module's "Auto-detect EMI/prepayment" box was audited first
and found to already be UNUSUALLY tolerant compared to the other modules' paste boxes: it doesn't
split the pasted text into fixed columns at all -- `classifyLoanTxn()` scans the raw description
text for EMI/prepayment keywords, and separate regexes scan the same raw line for a date and an
amount wherever they appear. That means it was never dependent on a particular column ORDER in
the first place; a real bank statement's actual layout (columns in any order, extra columns, no
columns at all) already worked.

**What was genuinely missing**: `dateRe` only matched numeric date formats (`DD/MM/YYYY`,
`DD-MM-YYYY`, `YYYY-MM-DD`) -- not the month-name format many real Indian bank e-statements use
(`01-Jan-2026`, `01 January 2026`), and not 2-digit years (`01/01/26`). Broadened to
`/(\d{1,2}[-\/.]\d{1,2}[-\/.]\d{2,4}|\d{4}[-\/.]\d{1,2}[-\/.]\d{1,2}|\d{1,2}[-\/
](?:jan|feb|...|dec)[a-z]*[-\/ ]\d{2,4})/i` -- also now accepts dot-separated dates
(`01.01.2026`). Amount matching (`[\d,]+\.\d{2}|\b[\d,]{4,}\b`) was already tolerant of
thousands-separator commas and any digit-run length; left unchanged.

**Real correctness bug found and fixed during this same audit** (not caused by the date-format
widening above -- pre-existing, confirmed via `git diff` that the amount-matching code was
untouched): the amount regex scanned the ENTIRE line for candidate amounts, including the
already-matched date substring. A line like `"05/04/2025 NACH LOAN DEBIT 1,25,000.00"` would pick
up **both** `2025` (from the date) and `125000` (the real EMI figure) as candidate amounts --
since EMI picks `Math.min(...amounts)` (documented as "EMI is usually the smaller recurring
figure"), `2025` would silently win and get recorded as the payment amount instead of ₹1,25,000.
Fixed at the root: amounts are now scanned only in the line with the matched date substring
removed (`line.replace(dateMatch[0], ' ')`), so a date's own digits can never be mistaken for a
payment amount. This exactly matches the standard this whole audit is held to -- "never silently
misread a number" -- and would have produced a wrong-but-confident figure exactly like the kind
this task explicitly warns against.

**Verified with real headless-Chromium (Playwright), 5 checks**: regression -- numeric
`01/04/2025` date still detected with the EMI classifier; tolerant -- month-name date
`01-Jan-2026` now detected (previously would have failed to match `dateRe` at all, so the whole
line would have been silently dropped); tolerant -- space-separated month name `01 Jan 2026`
detected; honesty -- an unrelated transaction with no EMI/prepayment keyword (`ATM WITHDRAWAL`)
stays un-added; regression + bug-fix combined -- `1,25,000.00` (comma-grouped amount, adjacent to
a numeric date) now correctly records ₹1,25,000 as the payment amount, not the date's `2025`. 0
console errors. `node --check` confirmed no syntax errors after the edit.

## Fix: EMI/prepayment amount silently misread as the statement's running-balance figure (2026-08-13)
`financial-os-ux-tester` reproduced a real, live silent-data-corruption bug: the auto-detect
handler's `const amount = kind==='emi' ? Math.min(...amounts) : Math.max(...amounts);` picked
whichever number happened to be smallest/largest on the line, with no awareness that a
running/closing-balance figure -- present on nearly every real Indian net-banking statement export,
and almost always numerically larger than the transaction -- was itself one of the candidates. The
tester's exact reproduction: `15-Mar-2026 NEFT PART PAYMENT TOWARDS HOME LOAN PREPAY 1,00,000.00 DR
3,25,000.00` (a real ₹1,00,000 prepayment with a ₹3,25,000 closing balance) was recorded as a
₹3,25,000 prepayment -- the balance, not the real transaction. The same collision risk applies to
EMI lines too on a smaller loan or near payoff, where the balance can be numerically *smaller* than
the EMI, silently winning `Math.min()` instead.

**Fix, same "exclude the known-non-amount substring, then rescan" pattern as the existing
date-digit-exclusion fix in this same file** (see the entry above). New `stripLikelyBalance(line,
amtRe)` runs on the amount-candidate line (after the date substring is already removed) before the
Math.min/Math.max pick, using two genuinely reliable label/marker signals (a third,
position-only signal was built, then removed after an independent review — see "Reviewer pass"
below):
1. An explicit `Bal`/`Balance`/`Avl Bal`/`Closing Balance` label immediately before a figure --
   the least ambiguous signal, since the statement is naming the figure itself.
2. `<amount> DR/CR <balance>` -- a very common real Indian statement shape (confirmed by the
   tester's own reproduction line) where a Dr/Cr marker sits directly between the transaction
   amount and the balance that follows it; the number *before* the marker is the transaction, the
   number *after* it is the balance.
Any residual case with 2+ numeric candidates and neither signal present is left ambiguous rather
than guessed at (position alone can't say which extra number is the balance) -- that line is
honestly skipped, folded into the scan feedback with its own count ("N line(s) skipped: couldn't
confidently tell the transaction amount apart from a balance/running-total figure -- add those
manually") instead of silently recording a guess.

**A second real bug found and fixed while testing this fix**: the "Detected and added N
payment(s)" feedback message (`#l_import_feedback`) never actually rendered -- it was being set
directly on the `importCard` DOM node captured by the click handler's closure, but `saveData();
render();` (called just before it, to refresh the payments table) replaces the *entire* `#content`
subtree on every call, so by the time the feedback line ran, `importCard` was already a detached
node nobody could see. Exact same root cause and fix pattern as `portfolio/PROGRESS.md`'s
`bulkAddFeedbackMsg` fix (2026-08-09): a new module-level `loanImportFeedbackMsg` variable is set
*before* `render()` runs and read back into the freshly-rebuilt `#l_import_feedback` markup on the
next render, instead of writing to a stale node after the fact. This mattered directly for the fix
above -- without it, the new honest-skip count would never actually have been visible to the user.

**Tested with real headless Chromium (Playwright), reproducing the tester's exact scenario plus
several other realistic statement-line shapes:**
| Line | Before | After |
|---|---|---|
| `15-Mar-2026 NEFT PART PAYMENT TOWARDS HOME LOAN PREPAY 1,00,000.00 DR 3,25,000.00` (tester's exact case) | ₹3,25,000 (the balance, wrong) | **₹1,00,000** (correct) |
| `01-Apr-2026 ACH-DR-TP ACH EMI PAYMENT 25,000.00 DR 4,50,000.00` (EMI, DR marker, large balance) | risk of ₹4,50,000 if it ever won min() | **₹25,000** (correct) |
| `05/06/2026 NACH LOAN EMI 15,000.00 8,000.00` (EMI near payoff, balance smaller than EMI, no marker) | ₹8,000 (the balance, wrong -- `Math.min` picked it) | **honestly skipped** (see "Reviewer pass" below -- an earlier version of this fix resolved this case via a position-only signal that was found unsafe and removed) |
| `12-Jun-2026 BRN-CLG-CHQ PAID TO SBI BANK 2,00,000.00 CR 5,00,000.00` (CR marker variant) | risk of ₹5,00,000 | **₹2,00,000** (correct) |
| `20-Jul-2026 NEFT PREPAY LOAN 75,000.00 Bal: 6,10,000.00` (explicit Bal: label) | risk of ₹6,10,000 | **₹75,000** (correct) |
| `22-Aug-2026 NEFT LOAN PREPAY CHQ NO 123456 1,00,000.00 3,25,000.00` (genuinely 3 candidates, no signal -- a cheque/reference number that IS picked up as a digit-run) | would have guessed one of the 3 | **honestly skipped**, feedback names the reason |
| `05/04/2025 NACH LOAN DEBIT 1,25,000.00` (single amount, no balance column -- regression) | ₹1,25,000 | **₹1,25,000** (unchanged) |
| `01/04/2025`, `01-Jan-2026`, `01 Jan 2026` date-format regression + `ATM WITHDRAWAL` non-keyword regression | all correct | all still correct, unchanged |

The feedback-message fix was verified separately: before, `#l_import_feedback`'s textContent was
always empty after a scan regardless of outcome; after, it correctly shows "Detected and added N
payment(s)" plus the new skip count when applicable. 0 console/page errors across every scenario.
`node --check` clean after every edit.

Files touched: `/home/user/Financial-OS/loans/index.html` (`stripLikelyBalance` added,
`l_import_btn`'s onclick handler, `loanImportFeedbackMsg` module-level variable, the
`#l_import_feedback` markup and `renderLoanBody`'s importCard template).

### Fix (2026-08-13, same day) — reviewer-found gap in the surviving DR/CR signal
`financial-os-reviewer` gave this fix its first real independent review (the earlier pass used
`code-review` as a substitute, since `financial-os-reviewer` wasn't invocable in that session) and
found a live, reproducible instance of the exact bug class this fix exists to close — just moved
onto the signal that survived, not the one that was removed. The `code-review` pass's own
reference/cheque-number counter-example was only tested against a line with **no** DR/CR marker
present; a reference or cheque number sitting directly *before* a DR/CR marker (a completely
realistic shape in Indian bank narration -- e.g. `...REF 123456789 DR 15,000.00` or `...CHQ NO
998877 DR 42,000.00`) was still being trusted as "the amount" purely on its position before the
marker, with no check that it plausibly WAS an amount -- silently stripping the real figure after
the marker as if it were the balance.

Fixed by requiring the pre-marker number to actually look like a real amount (paise-formatted,
`.dd`) before trusting that signal — every genuine transaction/balance figure in this module's own
verified test cases above is `.00`-formatted; a reference/cheque number never is. If the pre-marker
number doesn't have that shape, the line falls through instead of guessing (honestly ambiguous,
same as any other unresolved case).

Verified directly, live through the real `#l_import_paste`/`#l_import_btn` UI, not just in
isolation: `...REF 123456789 DR 15,000.00` and `...CHQ NO 998877 DR 42,000.00` both now correctly
honest-skip (`Detected and added 0 payment(s)... couldn't confidently tell the transaction amount
apart from a balance/running-total figure`) instead of recording ₹12,34,56,789 / ₹9,98,877; every
row in the table above was re-run and still resolves identically.

Also checked, not changed: the reviewer separately flagged the CR-marker-variant test row above as
possibly not reproducible as written (no PREPAY/EMI/FORECLOS keyword). Verified this directly —
`classifyLoanTxn()` has a SECOND, separate pattern (`BRN-CLG-CHQ PAID TO.*(BANK|ICICI|HDFC|AXIS|
SBI)`) that this exact line matches on its own, independent of the PREPAY/PART-PAY/FORECLOS keyword
check the reviewer compared it against — confirmed via direct execution, not assumption. The row was
already accurate as written; no correction needed there.

## Reviewer pass: an unsafe position-only signal removed, per-loan feedback isolation fixed (2026-08-13, same day)
`financial-os-reviewer` wasn't available as an invocable skill in this session's environment;
`code-review` was used as the closest available substitute for the required independent
verification pass before committing. It found two real issues in the fix directly above, both
fixed before this reached its final form.

**1. The removed "exactly-2-candidates, no label/marker -> last one is the balance" signal was
unsafe -- live-reproduced.** The original version of this fix included a third signal alongside the
Bal-label and DR/CR-marker checks: when a line had exactly 2 numeric candidates and neither
explicit signal matched, the LAST one was assumed to be the balance. The review found this was a
blind positional guess that can't tell a genuine "amount, balance" pair apart from any other
2-number narration -- e.g. a reference/cheque/account number sitting elsewhere on the line. Live-
reproduced: `05/04/2026 NACH LOAN EMI PAYMENT REF 123456789 15,000.00` (a reference number BEFORE
the real amount, itself a plausible narration shape) has exactly 2 candidates
(`123456789`, `15000`) and no label/marker -- the removed signal treated the LAST one (`15,000`, the
REAL amount) as the balance and stripped it, leaving only the reference number, which then won
`Math.min()` and got recorded as a **₹12,34,56,789 EMI** -- the exact silent-wrong-number failure
class this whole fix exists to close, reintroduced via the new heuristic on a different input
shape. **Fixed by removing the signal entirely** rather than trying to patch around it -- same
standard this app's own paste-parsing safety work already holds itself to (see
`itrgenie/PROGRESS.md`'s "fourth round" entry: a shortcut that fixed real cases but reopened silent
corruption on others was reverted rather than shipped partially-safe). The practical cost: a plain
"amount, balance" line with no Bal label and no DR/CR marker (e.g. the near-payoff EMI case in the
table above) is now an honest skip rather than a resolved parse -- correctly conservative, since
real Indian statement exports overwhelmingly DO carry one of the two remaining signals (a Dr/Cr
marker or an explicit balance label) per the tester's own description of the shape, and guessing
blind at position risked exactly the class of bug the fix was written to eliminate.

**2. `loanImportFeedbackMsg` was a single flat variable, so one loan's scan feedback bled into a
different loan's import panel.** Live-reproduced: scan Loan A, see its "Detected and added N
payment(s)" message, then expand Loan B (no scan ever run for it) -- Loan B's import panel showed
Loan A's message, falsely implying a scan had just run for Loan B. Fixed by keying the variable by
loan id (`loanImportFeedbackMsg[loan.id]`, defaulting to `''` when unset) instead of one shared
string, read back per-loan at render time.

**Re-verified with real headless Chromium (Playwright) after both fixes**: the reviewer's exact
reference-number counter-example (both orderings -- reference number before AND after the real
amount) now honestly skips instead of misreading either number; the tester's original DR-marker
scenario, the EMI+DR-marker+large-balance case, the explicit `Bal:` label case, the CR-marker
variant, and all pre-existing date-format/keyword/date-digit-exclusion regressions still pass
exactly as before; a fresh second loan's import panel now correctly shows no feedback (not the
first loan's message) when expanded without a scan of its own. 0 console/page errors. `node
--check` clean.
