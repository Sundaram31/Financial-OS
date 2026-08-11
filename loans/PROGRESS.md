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
