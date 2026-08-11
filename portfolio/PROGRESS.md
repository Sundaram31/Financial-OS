# Portfolio Tracker — Progress

## What this is
Standalone single-file tool (`index.html`), same design system and conventions
as every other module here (ITRGenie, Net Worth, Goals, Loans, Insurance) —
shared CSS variables, same `itrgenie_theme` light/dark toggle, paste-and-parse
plus CSV/TXT file-upload for data entry, own storage key, zero external
dependencies, fully offline once loaded. This is the module referenced as
"Built elsewhere, not yet moved here" in the original 8-pillar list and as
the "next major phase" in `MASTER_ROADMAP.md`'s "Updated module sequence" —
it did not exist in this repo before this session; everything here is new.

## Built (2026-08-09)
- **Accounts**: pre-seeded with the 4 real broker/demat accounts — Axis
  Direct, Tradejini, Angel One (all INR), Vested-US (USD). Pasting a broker
  name that doesn't match one of the 4 auto-creates a new account rather than
  silently dropping the row; you can also add one manually.
- **Holdings entry**: paste-and-parse plus CSV/TXT file upload, one holding
  per line — `Symbol, Broker, AssetType, Qty, BuyPrice, BuyDate,
  CurrentPrice, AsOf` (CurrentPrice/AsOf optional; a holding with no current
  price is flagged "stale" and shows zero gain/loss until updated).
- **Holdings table**: Current Price and As Of are editable inline in the
  table — this is the actual "manually updated or re-imported" refresh
  workflow, since there's no live feed (see Known gaps). Filterable by
  account. Delete per row.
- **Performance tracking**: cost basis vs current value, gain/loss in both
  absolute and % terms, per holding and aggregated across the whole
  portfolio (INR total) and per account (native currency).
- **Asset allocation view**: breakdown bar + legend by asset type
  (hand-drawn SVG-free div bar, same zero-dependency approach as Net Worth's
  breakdown bar), plus a per-account table (native-currency cost/value/gain).
- **USD → INR handling**: Vested-US is a genuinely different currency, not
  just a different broker. A manual "USD → INR rate" field lets Vested-US
  holdings fold into the aggregate INR total and asset-allocation view; until
  a rate is entered, USD holdings are still shown correctly in their own
  native-currency table but excluded from the INR aggregate, with an
  explicit count-and-warning rather than silently mixing currencies.
- **Net Worth feed**: builds the `{category, label, value, asOf}[]` array
  from `MASTER_ROADMAP.md`'s cross-module data contract (one row per
  account) — downloadable as JSON, plus a "copy paste-ready lines" button
  that matches Net Worth Dashboard's own `Label, Value` paste format so the
  numbers can actually be moved over today, not just theoretically exported.
- Export/Import full-state JSON for backup, own storage key
  (`portfolio_data_v1`), independent of every other module's data.

## Updated 2026-08-09 — Net Worth feed is now a one-click auto-import
Net Worth Dashboard's Import button now detects and merges this module's
feed shape directly (see `networth/PROGRESS.md`'s matching entry) — the
"Net Worth's own Import wasn't modified to auto-consume the feed" gap noted
below under "Deliberately NOT done yet" is resolved. The "Download Net
Worth feed (JSON)" button's downloaded file can now be fed straight into
Net Worth's Import file picker: it merges into the Investments category,
upserting by account label so re-exporting/re-importing after these
numbers change updates the existing row rather than duplicating it, and
correctly skips any account still unconverted (no USD→INR rate set) rather
than importing a raw dollar figure as rupees. The "copy paste-ready lines"
button remains as a manual alternative. `renderNetWorthFeedCard()`'s
description text was updated to point at the Import button as the primary
path.

## Updated 2026-08-09 — Live price feed built (Tier 1 Yahoo + Tier 2 Twelve Data)
Closes gap #1 below, with an important caveat — see "What's confirmed vs.
unverified" underneath. Built per explicit user direction this session:
"Twelve Data API where the user brings their own key can be one method, or
the user can bring any other API for live tracking. But we also have to
give some basic data tracking without any setup or API, something like
Google Finance or Yahoo Finance data."

**Tier 1 — no-setup default.** `fetchQuoteYahoo(symbol)` calls Yahoo
Finance's public chart endpoint (`https://query1.finance.yahoo.com/v8/finance/chart/{symbol}`,
falling back to `query2` if `query1`'s request errors — Yahoo runs both as
redundant hosts) directly from the browser, no key required. Reads
`json.chart.result[0].meta.regularMarketPrice`. Built defensively: any
non-2xx response, a `chart.error` field, a missing/non-numeric/≤0 price, or
a thrown network error is treated as a failure, never trusted as real data.

**Tier 2 — optional, bring-your-own-key.** `fetchQuoteTwelveData(symbol,
exchange, apiKey)` reuses the exact safe pattern from the earlier Portfolio
Tracker prototype found in the user's Drive (fetch → parse → treat any
`status:'error'`/`code` field or unusable price as a failure). The key is
entered into the collapsible "Live prices" settings panel and stored in its
own localStorage key (`portfolio_livekey_v1`) — deliberately **separate**
from `portfolio_data_v1` so it's never bundled into the Export JSON backup
file, and never hardcoded/committed. Free tier limits (800/day, 8/minute)
are stated in the UI, same as the old tool did. If a key is saved, Twelve
Data is tried first (the user opted into the more-reliable tier on
purpose) and Yahoo is the automatic fallback; with no key, only Yahoo is
tried.

**Provider architecture.** `fetchQuoteYahoo` and `fetchQuoteTwelveData` are
small, isolated, single-purpose functions; `fetchLivePrice(h)` is the only
orchestrator that knows about "try Twelve Data if a key exists, else
Yahoo, and surface every error." A future third provider (the user
explicitly said they might bring a different API later) is a new function
plus one more line in that orchestrator's attempt list, not a rewrite.

**Symbol/scope handling.**
- Only `Stock`/`ETF` holdings are refreshable — plus `Equity`, treated as a
  synonym for `Stock` because that's this module's own default/example
  AssetType for individual stock holdings (see the Holdings entry card's
  paste format); restricting the match to the literal word "Stock" would
  have left the module's own example data unrefreshable. `Mutual Fund` and
  everything else stays manual-only, visibly marked "manual only (<type>)"
  in the table rather than silently no-op'd — fund NAVs need AMFI scheme
  codes, not ticker quotes, and guessing at that mapping would be exactly
  the kind of unverified claim this project's conventions warn against.
- INR accounts get a `.NS` suffix appended for Yahoo (`RELIANCE` →
  `RELIANCE.NS`) unless the symbol already looks suffixed; Twelve Data
  instead gets `exchange=NSE` as a separate query param — the two
  providers' conventions are handled separately, not conflated.
- Vested-US (USD) holdings use the plain ticker for both providers, no
  suffix, no exchange param.
- A failed fetch (any reason) never overwrites the existing manually-entered
  `CurrentPrice` — confirmed by test (see below).
- "Refresh all" stages requests ~350ms apart (same pacing as the old
  prototype) so it doesn't hammer either provider.
- Manual entry of Current Price is completely unchanged and always works,
  live fetch or not — it's an assist, never a requirement.

**UI.** A collapsible `<details class="live-settings">` panel ("Live
prices — Yahoo (no setup) + optional Twelve Data key") sits above the
holdings table: an amber/gold `.notice` box discloses the outbound network
call plainly (worded like the old tool's amber notice — scoped only to
public symbol/price lookups, never holdings/personal data) and explains
both tiers; a text field + Save/Clear for the Twelve Data key. A
"↻ Refresh live prices (N)" button sits next to the account filter above
the holdings table (N = count of currently-refreshable holdings); each
Stock/Equity/ETF row also gets its own small "↻ live" button and a
per-row status line ("✓ HH:MM · live via Yahoo Finance (query1...)" in
green, or "✕ <error message>" in rust, with the full message in a
tooltip) — failures are always visible, never silent, never a broken UI.

**What's confirmed working vs. unverified.** Tier 2 (Twelve Data), the
scoping logic, symbol/exchange resolution, the fallback order, the
staggering, the "never overwrite on failure" guarantee, the key storage
separation, and the UI itself were all exercised with a real headless
Chromium browser (Playwright) with `window.fetch` mocked at the network
boundary — 34 automated checks (success paths, `query1`→`query2` host
fallback, total-failure visibility, malformed/negative-price rejection,
Twelve Data success/error/fallback-to-Yahoo, rate-limit staggering timing,
manual-entry-still-works, and confirming the API key never appears in the
Export JSON) all pass, plus a visual check in both themes. **Tier 1's
actual behavior against the real Yahoo endpoint in a real browser has NOT
been verified by anyone** — this build environment's outbound network
access to arbitrary hosts is blocked by its own sandbox proxy policy (a
403 from the sandbox, not from Yahoo, confirmed via a failed `curl` to
`query1.finance.yahoo.com` from this environment), so the actual
CORS/cookie/crumb behavior of Yahoo's public chart endpoint from a real
browser is unknown until the user tries it on the live deployed site. If
it turns out to be CORS-blocked in practice, the failure path is already
built and visible (a clear "Live fetch failed — CORS-blocked or endpoint
changed" message per row, manual entry unaffected) rather than a silent
failure or crash — but that a real network attempt actually reaches Yahoo
and gets a usable response is **not yet confirmed as true**, only "handled
gracefully either way."

## Updated 2026-08-09 — UX overhaul in response to real-user feedback (phone use)
The user actually used `index.html` on a phone and reported four blunt problems. All four
addressed in this pass; nothing about the data model, storage keys, or math changed.

**1. "Live feed not working."** This confirmed in practice what the previous session's entry
above only flagged as unverified: Tier 1 (Yahoo) failed in the user's real browser. Two changes:
- **Added Tier 1b — Stooq** (`fetchQuoteStooq(symbol)`), a second free/no-key attempt tried
  automatically if Yahoo fails, before the user is asked to set up Twelve Data. Calls
  `https://stooq.com/q/l/?s={symbol}&f=sd2t2ohlcv&h&e=csv`, parses the CSV (Close is the 7th
  field), rejects `N/D`/missing/non-numeric/≤0 prices, throws rather than trusts. `stooqSymbolFor`
  appends `.us` for USD holdings (Stooq's own documented, working convention) and `.in` for INR
  holdings — **the `.in` suffix and Stooq's actual NSE coverage are NOT confirmed**, same caveat
  as Yahoo's Tier 1 had. Stated plainly in-UI (Live Prices settings panel) and below.
- **Failure messaging now points at the fix.** `fetchLivePrice` attaches a `suggestTwelveData`
  flag to the error it throws once every attempt fails; the UI (`liveStatusHtml()` per-row status,
  `refreshAllLive()`'s summary line) renders a direct `<a href="#live-settings-panel"
  onclick="openLiveSettings(event)">add Twelve Data key ↗</a>` link instead of leaving the user
  with only an opaque error string. Clicking it opens the (now-collapsible) Live Prices settings
  panel and scrolls/focuses it. Twelve Data remains the confirmed-working path (proven against
  the old Drive prototype for NSE via `exchange=NSE`), so the message leads with it explicitly:
  "Free live sources aren't working right now (...)." A failed fetch still never overwrites an
  existing price — unchanged, re-verified by test.

**2. "Layout fonts too small to read on mobile."** Audited every font-size in the `<style>` block.
Added a real mobile baseline inside `@media (max-width:760px)` (previously that block only
touched padding) — body, helptext, field labels, buttons, and table cells all bumped to
comfortable sizes on narrow viewports (body 16px, helptext 13.5px, table cells 14px — verified via
Playwright's computed-style API at a 375×812 viewport, not just eyeballed). Desktop sizing is
untouched. Also switched the holdings/broker-breakdown tables from "shrink text and let it
horizontally scroll" to a stacked label/value **card layout on mobile** (`<thead>` hidden,
`<td data-label="...">` pseudo-labels via CSS `::before`) — confirmed via Playwright that
`document.documentElement.scrollWidth` never exceeds the viewport width at 375px, i.e. no
horizontal scroll requirement on phone, not just smaller text on a table still too wide.

**3. "Data entry very difficult to add stock details."** Added a proper guided **"Add a holding"**
form as the primary entry path, right below the holdings table: separate labeled fields (Symbol
text input; Broker `<select>` populated from `data.accounts`; Asset type `<select>` —
Stock/ETF/Mutual Fund/Other; Qty, Buy Price number inputs; Buy Date `<input type=date>`; optional
Current Price/As Of) and a single "Add holding" button. Produces the exact same holding object
shape (`{id, symbol, broker, assetType, qty, buyPrice, buyDate, currentPrice, asOf}`) the bulk
paste-parser already produces, so live price fetch, the Net Worth feed export, and all allocation
math work identically regardless of entry path. Remembers the last-used broker/asset-type
selection (module-level vars, not persisted to storage) so adding several holdings from the same
account is fast. The original paste-and-parse + CSV/TXT upload flow is kept, unchanged in its
parsing logic, moved into a collapsed `<details class="collapsible">` "Bulk add / advanced" panel
(same collapsible pattern as the Live Prices settings panel) — per this repo's own convention that
forms exist *alongside* paste/upload, not instead of it.
  - **Fixed a pre-existing bug while touching this code**: the old paste-entry feedback message
    (`"Added N, skipped M"`) was being written onto a DOM node captured *before* the enclosing
    `render()` call, which replaces the entire `#content` subtree — so the text was set on an
    already-detached element and never actually appeared on screen. Root-caused and fixed by
    moving the feedback text into a module-level variable (`bulkAddFeedbackMsg` /
    `addFormFeedbackMsg`) read back in during the next `render()`, the same pattern already used
    correctly elsewhere (`refreshAllStatusMsg`). The bulk-add panel is also forced open
    (`bulkAddOpen = true`) right after a successful add so the now-visible feedback isn't hidden
    behind a collapsed `<details>`.

**4. "Too much text, holdings buried, not a normal portfolio layout."** Restructured toward the
standard portfolio-tracker information hierarchy (Zerodha Console / Groww / Google Finance-style):
  - New `.stat-grid` of three bold stat tiles right after the header — **Current value**,
    **Invested (cost basis)**, **Total gain/loss** (green/rust, serif numerals, ~25px) — replacing
    the old single-paragraph `result-box`.
  - **Holdings table now renders immediately after the summary**, before any entry form or
    settings card. Added click-to-sort on Symbol/Qty/Value/Gain-Loss column headers
    (`holdingsSort` state, ▲/▼ indicator) — a reasonable "sortable if reasonable" per the request,
    given the table has no pagination to complicate. Renamed "Buy Price" column header to
    "Avg Price" to match the terminology the feedback referenced (the underlying field/value is
    unchanged — this module still only tracks one buy price per holding, not a computed average
    across multiple buys; a genuine per-lot average is future work if multi-buy tracking is ever
    added). Broker/Type/Buy Date de-emphasized with a muted/smaller style; Value and Gain/Loss
    bolded — so P&L reads at a glance rather than every column competing for attention equally.
  - Verbose paragraphs moved behind toggles: the paste-format description now only exists inside
    the collapsed "Bulk add / advanced" panel; the live-price disclosure/tier explanation was
    already inside the collapsed Live Prices panel (unchanged); the three-item Known Gaps list is
    now itself a collapsed `<details class="collapsible">` ("Known gaps — flagged, not papered
    over (3)") instead of an always-visible card.
  - Reordered the whole page: Header → Summary → Holdings table → Add a holding → Bulk
    add/advanced (collapsed) → Live prices (collapsed) → **Accounts & FX** → **Allocation &
    performance** (asset-allocation bar, by-account table) → **Cross-module** (Net Worth feed) →
    Known gaps (collapsed). Accounts, FX, Net Worth feed export, and Live Prices settings are all
    real, still fully functional, just no longer first — per explicit direction that a first-time
    user should see numbers, not paragraphs.
  - Kept the existing gold/rust/green ledger palette, IBM Plex Mono + Source Serif 4 pairing,
    hairline borders and seal-mark motif throughout — this was an information-hierarchy pass, not
    a re-skin; see `financial-os-visual-design` skill, which was reloaded before touching markup.

**Testing.** Real headless Chromium (Playwright), `window.fetch` mocked at the network boundary
(same approach as the 2026-08-09 live-feed session): guided add-holding form (success + validation
+ shows in table/totals), bulk paste/CSV (still works, panel-stays-open fix verified), Yahoo
success, Yahoo-fails→Stooq-succeeds fallback (confirmed price written from Stooq's CSV), full
failure with the Twelve-Data-link message (confirmed clicking it opens+scrolls the settings
panel), a failed fetch never overwriting an existing price, Twelve Data success/never-in-export,
mobile viewport (375×812) — zero horizontal overflow, computed font sizes read back and asserted
≥13-16px depending on element, table stacked-card layout active — column sorting, FX fold-in
behavior, Net Worth feed JSON shape, both themes. All pass. Full-page screenshots taken at 375px
and 1280px in both themes for visual review (not committed to the repo — passed back to the user
directly for review before this ships).

**What's confirmed vs. still unverified (updated).** Stooq's CSV parsing logic, the failure
message/link behavior, the mobile layout, and the guided form are all verified via the mocked
Playwright suite above. **Not verified**: Stooq's actual response for real NSE-suffixed symbols
(`.in` guess) and its real-world CORS/rate-limit behavior from an actual browser — this build
environment's outbound network is still sandboxed the same way it was for Yahoo, so neither Tier 1
nor Tier 1b has been exercised against the real internet by anyone. Tier 2 (Twelve Data) remains
the one tier with real-world provenance (the old Drive prototype). This is stated plainly in the
in-app Live Prices settings copy, not just here.

## Updated 2026-08-10 — Real Excel (.xlsx) import + CAS (NSDL/CDSL demat statement) PDF import
Built per explicit user feedback: document import was the weakest part of the app. Two concrete
problems fixed. **Nothing about this session's changes are speculative Drive-history work** — this
is capability, not data reconciliation (gap #3 below is unchanged).

**A. Real Excel import with fuzzy column detection (was: broken).** The old `#h_file` input
(`accept=".csv,.txt"`) fed every uploaded file through `reader.readAsText()` into the comma
parser — a real broker `.xlsx` export (Zerodha, Angel One, Groww, etc.) is a binary zip file, so
this silently produced garbage or nothing. Fixed:
- Self-hosted SheetJS at `portfolio/lib/xlsx.core.min.js` — copied from `itrgenie/lib/`, not
  referenced cross-module, matching this repo's per-module independence (ITRGenie doesn't
  reference Net Worth's files either; same reasoning applies here).
- `#h_file`'s `accept` now includes `.xlsx,.xls`; `wireFileUpload()` branches on extension —
  CSV/TXT still flow through the exact unchanged textarea+Parse&Add pipeline; Excel files route to
  `handleExcelFileSelected()`, which reads the real binary file via `XLSX.read(buf, {type:'array',
  cellDates:true})`.
- **Fuzzy column detection** (`detectColumnMapping`, `findHeaderRowAndMapping`): headers are
  normalized (lowercase, strip punctuation, collapse whitespace) and substring-matched against
  per-field alias lists (symbol ← instrument/symbol/scrip/ticker/stock name/trading symbol/
  security name/security; quantity ← qty/quantity/units/shares; price ← avg cost/average price/buy
  avg/avg price/buy price/cost price/purchase price/buy rate; date ← buy date/trade date/purchase
  date/date), so "Avg. cost" and "Buy Avg" both resolve to the price field without an exact-schema
  requirement. Scans the first 10 rows for the real header row (real exports often have a title row
  above it, e.g. "Holdings as on..."). A 12-character ISIN pattern found consistently in a column's
  actual cell values is used as an independent fallback signal for the symbol column when no header
  matches one — broker-independent, unlike a ticker convention.
- **Mapping preview before commit**: `renderXlsxImportPreview()` shows exactly which column was
  matched to which field and how (header-text match vs. ISIN-pattern match), a preview of the first
  5 parsed rows, an account/asset-type selector applied to the import, and a row
  imported/skipped count — nothing is written to `data.holdings` until the user clicks "Import N
  holdings". A file with too few recognizable columns shows a clear failure message (not a silent
  partial/garbage import) with a "Dismiss" button, no import path taken.

**B. CAS (NSDL/CDSL demat statement) PDF import — new capability, password-protected, client-side.**
A Consolidated Account Statement aggregates a user's holdings across ALL their brokers/demat
accounts into one document — genuinely broker-agnostic, unlike any single broker's own export;
confirmed by the user as their most readily-available document. Built:
- Self-hosted PDF.js at `portfolio/lib/pdf.min.js` + `pdf.worker.min.js` — same copy-not-reference
  pattern as SheetJS above.
- New collapsible "Import from CAS (NSDL/CDSL demat statement)" panel (`renderCasImportCard`),
  positioned next to the bulk-add panel. A `.notice` box states plainly that everything (the PDF,
  the password, the extracted data) stays client-side, nothing is uploaded — same tone/pattern as
  the existing Live Prices notice.
- **Password handling** (`startCasUnlock`, `submitCasPassword`): uses PDF.js's real
  `loadingTask.onPassword(updatePassword, reason)` callback — `NEED_PASSWORD` shows an inline
  password field + Unlock button in the page itself (not a browser `prompt()`); a wrong password
  re-fires the same callback with `INCORRECT_PASSWORD`, which the UI shows as a plain "Incorrect
  password — try again" message with the field still there, not a dead end. No password is ever
  guessed, hardcoded, or skipped.
- **Text extraction** (`extractPdfLines`): groups PDF.js text items by rounded y-position and sorts
  by x within each line, reconstructing row structure from a tabular PDF far more reliably than a
  naive extraction-order join (needed here because CAS parsing needs rows, not prose).
- **Parsing** (`parseCasPdfText` — see the "UNVERIFIED" callout below): anchors on the ISIN pattern
  as the one reliable signal in an otherwise inconsistent layout; for each ISIN-containing line,
  strips the ISIN's own embedded digits out of the numeric-token scan first (an ISIN like
  "INE009A01021" contains digit runs of its own that would otherwise contaminate quantity/value
  detection), takes the last two remaining numeric tokens as quantity then market value, and
  derives the security name by subtracting the ISIN and those numeric tokens from the line rather
  than assuming a fixed column order. Lines mentioning DP ID/Client ID/BO ID/CDSL/NSDL are used only
  to *label* groups of holdings for the account-assignment dropdown (mislabeling doesn't affect
  parsing correctness). CAMS/KFintech mutual-fund CAS (folio/AMC/scheme structure) is explicitly
  OUT of scope — its layout differs enough from a demat CAS that a half-built parser would produce
  worse results than a clear "not supported, try Excel/manual" message; NSDL/CDSL demat CAS is the
  sole target, since it maps directly onto this module's existing Stock/ETF holdings model.
- **Graceful failure**: no text layer (scanned PDF) → clear message, no crash. No ISIN+quantity
  pattern recognized anywhere in the unlocked text → clear "couldn't recognize a CAS holdings
  table... try Excel import or manual/paste entry instead" message with a retry button, never a
  silent wrong import.
- **The "buy price isn't in a CAS" honesty requirement — surfaced in the UI itself, not just docs.**
  A CAS shows current quantity and current market value; it does NOT contain historical purchase
  price/cost basis. Imported holdings get `buyPrice: ''` (genuinely blank), never a computed
  `marketValue/qty` mislabeled as buy price. This is stated in **two places directly in the import
  flow**: a rust-colored `.notice.warn` box in the CAS panel itself ("A CAS shows what you hold
  today, not what you paid for it... Buy Price left blank for you to fill in yourself") shown before
  the user even picks a file, and again in the post-import feedback message ("Buy Price left blank,
  fill in per row in the Holdings table above").
- **Closing the loop**: the Holdings table's Avg Price (Buy Price) column is now itself an inline-
  editable input (`data-bp`), the same pattern already used for Current Price/As Of — previously
  Buy Price could only be set at creation time via the guided form or paste/Excel import. This is
  what CAS-imported rows' "fill in Buy Price yourself" note above actually points at.
- **Real correctness bug found and fixed while building this**: `computeHoldingMetrics` previously
  did `+h.buyPrice || 0`, treating a missing buy price as a cost basis of zero — which would have
  made a CAS-imported holding's entire current value display as "gain" (misrepresenting "no cost
  data" as "100% profit"), a real math error, not a display nit. Fixed by threading `hasBuyPrice`
  through: `costBasis`/`gainAbs`/`gainPct` are now `null` (not 0) when buy price is genuinely unset,
  and every consumer was updated to handle it — the per-row Gain/Loss cell shows "— set Buy Price"
  instead of a number; the top stat tile's "Invested"/"Total gain-loss" figures and the "By
  account" table's Cost Basis/Gain-Loss columns now sum only over holdings with a known buy price
  (tracked separately from the always-complete "Current value" total), with an explicit
  gold-colored note ("N holding(s)... have no Buy Price yet — ... excluded from Invested/Gain-Loss
  until you fill in Buy Price") wherever this applies — same "flag it, don't fabricate it" pattern
  already used for the unconverted-USD-holdings case elsewhere on this page. Verified by test: a
  freshly CAS-imported holding shows ₹0 invested / ₹0 gain (not the holding's full value as fake
  profit); filling in its Buy Price via the new inline input immediately recalculates the correct
  gain.

**UNVERIFIED — CAS text-layout parsing (`parseCasPdfText`), flagged the same way the live-price
Tier 1 work was.** This build environment had no real CAS file to test against, and the actual
document is the user's private data. `parseCasPdfText` was built defensively against publicly
documented NSDL/CDSL CAS structure and the general technique used by open-source tools like
`casparser` (positional text extraction + ISIN-anchored regex) — it was **not** verified against a
real statement's actual text layout, which is well known to vary between depositories/DPs and PDF
generators. It is deliberately kept in one small, isolated, clearly-commented function (see
`portfolio/index.html`, search for "Isolated, easy-to-revise CAS text parser") specifically so it
can be corrected quickly once tried against a real CAS. If a real CAS becomes available, this is
the one function to revise/replace — the surrounding UI (password unlock, preview, account
assignment, import commit, the Buy-Price-blank guarantee) does not need to change.

**What's confirmed working vs. unverified — full breakdown.**
- **Verified with real headless Chromium (Playwright), real files, no mocking of the parsing logic
  itself:**
  - Excel fuzzy-matching: a real `.xlsx` built with realistic messy headers ("Instrument", "Avg.
    cost", "Qty.", plus an unrelated title row and a comma-formatted price string) was uploaded and
    correctly mapped/imported end-to-end.
  - Excel graceful failure: a `.xlsx` with no recognizable columns showed the failure message and
    did not import anything.
  - PDF password mechanics, fully real: a genuinely AES-128-encrypted PDF (built with `pypdf`, known
    password) was uploaded — wrong password correctly showed "Incorrect password — try again" and
    kept the field open for retry; the correct password correctly unlocked it and proceeded to
    extraction. This exercises the actual PDF.js `onPassword`/`updatePassword` callback mechanics
    for real, not a simulation.
  - Unencrypted-PDF path: no password prompt shown at all when the PDF isn't encrypted (confirmed).
  - Graceful parse failure: a plain PDF with ordinary prose (no ISIN pattern anywhere) correctly
    produced the "couldn't recognize a CAS holdings table... try Excel or manual entry" message
    with a working retry button, not a crash or silent wrong import.
  - The gain/loss correctness fix (above) — confirmed via a full import → check-neutral-gain →
    fill-in-Buy-Price → check-recalculated-gain round trip.
  - Mobile viewport (375×812), both themes: zero horizontal overflow on the Excel preview, the CAS
    password prompt, and the CAS parsed-holdings preview; screenshotted and reviewed in both themes.
  - Full regression pass: guided add-holding form, bulk CSV/TXT paste, and Export JSON all still
    work exactly as before — untouched by this session's changes.
- **NOT verified — the one piece that genuinely cannot be, without a real document:** whether
  `parseCasPdfText`'s ISIN-anchored heuristic actually matches a real NSDL/CDSL CAS's text layout
  once extracted by PDF.js. The synthetic test PDF used to exercise the parsing *logic* (line
  grouping, ISIN-vs-numeric-token separation, name extraction, group labeling) was built by this
  session, not sourced from a real statement, so it proves the code *runs and behaves sensibly*
  against a CAS-shaped layout — it does not prove real CAS files are shaped the way this code
  assumes. If the user obtains a real CAS and its password, re-running the import against it and
  fixing `parseCasPdfText` accordingly is the natural next step.

## Updated 2026-08-10 — Fast follow-up from independent review: duplicate-on-reimport + blocking library loads
The `financial-os-reviewer` subagent independently audited the Excel + CAS import build (commit
`62c8772`, above) and confirmed the core work correct and safe, but flagged two real issues. Both
fixed same-day, in the same file, no scope changes beyond these two.

**1. Duplicate holdings on re-import — fixed with a shared `findDuplicateHoldingIndex()` helper,
applied to all three import paths (CAS, Excel, bulk paste), not just CAS.** Previously, importing
the same CAS PDF or Excel file twice (or pasting the same rows twice) silently created duplicate
holdings, silently doubling the portfolio's value/gain totals — a real risk for CAS specifically,
since a CAS is a document a user would naturally re-import periodically (e.g. quarterly) expecting
a refresh, not a one-time paste.
- `findDuplicateHoldingIndex(candidate)` matches an incoming holding against `data.holdings` by
  ISIN (case-insensitive) when both sides carry one — the strongest, broker-independent signal a
  CAS always provides — falling back to broker + symbol (case-insensitive) when ISIN isn't
  available, which is the common case for Excel/paste imports. One small function, reused by all
  three commit paths, so the matching rule can't drift between them.
- **CAS import → update-in-place (chosen over skip-or-duplicate).** A CAS is a snapshot of current
  qty/value, so re-importing one — the exact scenario flagged as likely — is naturally a *refresh*,
  not a fresh addition. On a match, the existing holding's `qty`, `currentPrice` and `asOf` are
  updated from the new CAS; `buyPrice`/`buyDate` are deliberately left untouched (a CAS never
  carries that data, so overwriting a value the user filled in by hand would destroy real
  information for no reason). On no match, a new holding is added exactly as before. The "parsed"
  preview computes and shows the exact will-update/will-add split *before* the user commits (e.g.
  "2 of these already exist in your holdings — importing will refresh their Qty and Current Price
  in place... 1 new holding will be added"), and the confirm button label reflects it ("Import 1
  new / refresh 2 existing"). Verified end-to-end: re-importing an identical CAS a second time
  leaves holdings count unchanged (no duplication); re-importing a *different* CAS snapshot for the
  same ISIN (qty changed 50→60 in the test fixture) actually updates the existing holding's qty,
  proving this is a real refresh, not a silent no-op.
- **Excel import and bulk paste → skip-duplicates, checked by default, real user override.** These
  two paths carry buy price/date that a re-import might legitimately intend to change (e.g. a
  corrected cost basis), so an automatic update-in-place felt like the wrong default risk — instead,
  the (already-existing, for Excel) preview-before-commit step now also shows a duplicate count
  ("2 of these row(s) already exist... — matched by ISIN/symbol") with a "Skip duplicates
  (recommended)" checkbox, checked by default; unchecking it and re-confirming imports the
  duplicate rows anyway, so a user who genuinely wants two lots of the same stock isn't blocked,
  only defaulted away from an accidental double-import. Bulk paste (no preview step) got the same
  checkbox directly in the paste panel, defaulting to skip, with the skip count folded into the
  existing "Added N, skipped M" feedback line.

**2. `xlsx.core.min.js` (437KB) + `pdf.min.js` (377KB) — 814KB combined — no longer block every
page load.** Both were previously loaded via unconditional blocking `<script src>` tags in `<head>`
on every single Portfolio Tracker page view, regardless of whether the user ever touched Excel or
CAS import — measured ~10s to interactive on a throttled (750kbps) connection. Fixed by lazy-loading
both via dynamic `<script>` injection (`loadScriptOnce()`, cached so a second call is a no-op),
triggered the first time the user actually opens the relevant panel — "Bulk add / advanced" for
Excel, "Import from CAS" for the PDF path — via each `<details>` element's `ontoggle` handler, so
the library is usually already warm by the time a file is picked. `handleExcelFileSelected` and
`handleCasFileSelected` also `await` the same loader directly (via `ensureXlsxLoaded()` /
`ensurePdfJsLoaded()`) before touching `XLSX`/`pdfjsLib`, so a file chosen before the panel-open
fetch finishes still works correctly instead of racing. A "Loading Excel support…" /
"Loading PDF support…" state is shown (on the file-choose button before a file is picked; as a
loading card in the import preview once a file is being processed) so the UI never looks frozen
during the fetch. **The `pdfjsLib.GlobalWorkerOptions.workerSrc` correctness trap called out by the
reviewer was specifically avoided**: that assignment previously ran as a synchronous top-level
`if(typeof pdfjsLib !== 'undefined')` check at page-init time, which only worked because the
`<script>` tag was blocking; it's now set inside `ensurePdfJsLoaded()`, immediately after
`pdf.min.js`'s dynamic load actually resolves, not at page-init time when `pdfjsLib` doesn't exist
yet. `pdf.worker.min.js` was already correctly lazy (PDF.js only fetches it once `getDocument()`
runs) and is untouched.

**Testing.** Real headless Chromium (Playwright), same approach as every other session on this
module. 47 checks, all pass: (a) network-request capture confirms `xlsx.core.min.js`/`pdf.min.js`
are absent from a plain page load's request list, and are fetched exactly once panel-open/file-select
triggers them, with the globals (`XLSX`, `pdfjsLib`) and `workerSrc` confirmed set correctly
afterward; (b) a throttled-network (750kbps, CDP `Network.emulateNetworkConditions`) timing check —
time-to-`load` dropped to ~1.35s (vs. the reviewer's ~10s baseline) on a plain page view, with the
Excel library taking ~4.8s to become available *after* opening the Bulk add panel under the same
throttle (the cost moved from "always paid" to "paid once, by the user who opts in, with a visible
loading state"); (c) full Excel import (fuzzy-header `.xlsx`, ISIN/header-match tags, mapping
preview) and CAS import (password-protected PDF, wrong-then-correct password, ISIN-anchored parse,
preview) end-to-end through the lazy-loaded libraries — both work exactly as before; (d) the
duplicate/update-in-place logic: re-importing an identical Excel file skips both rows by default,
unchecking "skip duplicates" and re-confirming imports them anyway (2→4 holdings, proving it's a
real user choice, not a hard block); re-importing an identical CAS refreshes both existing holdings
in place (holdings count stays at 2, not 4); re-importing a CAS with a *changed* quantity for one
ISIN actually updates that holding's qty (60, not the original 50), proving a real refresh, not a
no-op; pasting the same row twice skips the second by default, and unchecking the checkbox adds it
anyway; (e) regression pass — guided "Add a holding" form, live price refresh (mocked `fetch`), and
the FX card all still render/work correctly, untouched by this session's changes; (f) mobile
viewport (375×812), both themes — the new duplicate-notice boxes and checkboxes screenshotted and
confirmed to render cleanly with zero horizontal overflow (`scrollWidth` stayed at 375px in every
case tested).

## Updated 2026-08-10 — Second-pass reviewer fix: unbounded retry loop in the lazy-load error path
The `financial-os-reviewer` subagent independently re-verified the 2026-08-10 dedup/lazy-load fix
above (confirmed the dedup/refresh logic and the lazy-load speed win both correct), but found a
real, reproducible reliability bug in the lazy-load *error path* specifically. Fixed same-day, no
scope changes beyond this.

**The bug.** `render()` does `content.innerHTML=''` and rebuilds the whole subtree on every state
change, so the `<details class="collapsible">` panel for Bulk-add/CAS-import was a brand-new DOM
node on every render. `if(casImportOpen) el.open = true` (and the equivalent for `bulkAddOpen`) ran
on every single render of that panel — and Chromium fires a synthetic `toggle` event when `.open`
is set programmatically on a `<details>` element, even with no user interaction. The `ontoggle`
handlers called `ensurePdfJsLoaded()`/`ensureXlsxLoaded()` unconditionally on every such toggle.
Those two functions' state guard resets an `'error'` state straight back to `'loading'` and retries
automatically (`if(state !== 'loading' && state !== 'ready'){ state='loading'; ...; render(); }` —
true for `'error'` too) — so: toggle fires → retry starts → `render()` rebuilds the `<details>` →
`el.open = true` fires another synthetic toggle → retry starts again, forever. Reviewer measured
~15-23 requests/second in an unbounded loop that did NOT stop when the panel was closed, and
confirmed the "Couldn't preload…" error message was never actually visible during this (sampled
30 times over 3 seconds, visible 0/30) — a silent hang from the user's perspective while actually
hammering the network and CPU.

**The fix.** Both `ontoggle` handlers now only call `ensurePdfJsLoaded()`/`ensureXlsxLoaded()` when
the corresponding load state is `'idle'` (i.e. only on the panel's genuine first-ever open):
`el.ontoggle = ()=>{ casImportOpen = el.open; if(el.open && pdfjsLoadState==='idle')
ensurePdfJsLoaded(); }` (and the `xlsxLoadState`/`ensureXlsxLoaded()` equivalent for the bulk-add
panel). Once state is `'error'` (or `'loading'`/`'ready'`), a synthetic toggle from a re-render is a
no-op — it no longer retries. The real retry-on-error path is now genuinely what the UI text already
claimed: `handleExcelFileSelected`/`handleCasFileSelected` already `await ensure...Loaded()`
themselves when the user actually picks a file, and that call is allowed to retry (it's a real user
action, not a synthetic re-render side effect) since the guard inside `ensureXlsxLoaded`/
`ensurePdfJsLoaded` is unchanged. `findDuplicateHoldingIndex` and the rest of the dedup/refresh
logic — confirmed correct by the reviewer — were not touched.

**Testing.** Real headless Chromium (Playwright), the lazy-loaded script URL routed to fail
(`route.abort('failed')`) to reproduce the reviewer's exact scenario, both before and after the fix
for contrast:
- **Before the fix (confirmed the bug for real, not just from the report):** opening the CAS panel
  with `pdf.min.js` routed to fail produced a request count climbing from 15 to 54 over 2.5 seconds
  (~15-16 req/sec) with zero growth-stopping, and the "Couldn't preload PDF support" message was
  visible 0/10 times sampled.
- **After the fix:** the exact same scenario (CAS panel, `pdf.min.js` failing) produces exactly 1
  request total, stable across 2.5 seconds of sampling (no growth); the same test against the
  bulk-add/Excel panel (`xlsx.core.min.js` failing) also produces exactly 1 request, stable. The
  error message is visible 20/20 and 20/20 times sampled (CAS and Excel panels respectively) over 3
  seconds. Closing the panel after a failure produces zero additional requests over the following 3
  seconds (nothing left spinning). The documented real retry path was verified to actually work:
  routing `pdf.min.js` to fail once then succeed, the panel-open call fails and shows the error
  message, and a second call to `ensurePdfJsLoaded()` (the same call `handleCasFileSelected` makes
  when a file is picked) succeeds, sets `pdfjsLib` and `GlobalWorkerOptions.workerSrc` correctly, and
  only issues one additional network request (2 total) — a real single retry, not a loop.
- **Regression, re-confirming the two things the reviewer verified as already correct, since this
  fix touches the same functions' guard condition:** the dedup/update-in-place logic (pasting the
  same holding twice via bulk-add skips the duplicate by default, unchecking "skip duplicates" still
  allows a genuine second lot) and the race-condition-safe path (a second caller invoking
  `ensurePdfJsLoaded()` while the panel-open call is still in flight — simulating a file picked
  before the library finishes loading — resolves correctly, sets `pdfjsLib`/`workerSrc` once, and
  `loadScriptOnce`'s caching means only one network request fires even though two callers raced) both
  still pass after this change.

**Two smaller items from the reviewer's report, also done in this pass:**
1. **Whitespace normalization in symbol matching.** `findDuplicateHoldingIndex`'s symbol comparison
   now runs through a small `normalizeSymbolForMatch()` helper that collapses internal whitespace
   runs (`.replace(/\s+/g,' ')`) in addition to the existing `.trim()`/`.toUpperCase()`, so
   "RELIANCE  INDUSTRIES" (double space, e.g. from an inconsistently-formatted export) now correctly
   matches "RELIANCE INDUSTRIES" (single space) instead of being treated as a different holding.
2. **The cross-import-path dedup gap is now documented** — see Known gaps #5 below. Deliberately
   NOT fixed in this pass (it needs a real decision about symbol/name matching across sources, not a
   quick patch) — flagged, not silently resolved.

## Updated 2026-08-10 — Sold/realized capital-gains tracking built (roadmap item 4's stated prerequisite)
`MASTER_ROADMAP.md`'s "Updated module sequence" item 4 ("What-if fund-switch tax modeling")
explicitly states this module "currently has no sell/capital-gains workflow (only open holdings)
-- that would need to be built as part of this item, not assumed to already exist." This session
built exactly that prerequisite — sold-position tracking, ST/LT classification, and a capital-gains
feed export — and nothing more; the actual what-if fund-switch simulation UI itself remains
unbuilt (see "Deliberately NOT done yet" below and `MASTER_ROADMAP.md`'s updated item 4).

**Recording a sale.** A new "Record a sale" guided form sits right after the Holdings table (also
reachable via a "Sell" button on each holdings-table row, which scrolls/focuses the form) — select
an open holding from a dropdown (`SYMBOL — Broker (N available)`), enter Qty to sell (defaults to
the holding's full remaining qty, capped at it), Sell date, Sell price. This is a guided-form-only
flow, deliberately not paste/bulk — recording a sale is inherently relational (it must reference
one specific existing holding by id, a small closed set), unlike adding a fresh holding, so a
dropdown-driven form is the right shape here, not a shortcut around this repo's paste+form
convention. Validates: qty > 0, qty ≤ the holding's current open qty (real error message naming
the actual available qty, not a silent clamp), sell date required and not before the holding's buy
date, sell price ≥ 0.
- **Full sale** (qty sold ≥ holding's qty): the holding is removed from `data.holdings` entirely; a
  sold lot is created carrying the holding's full original qty.
- **Partial sale**: the holding's `qty` is reduced by the sold amount in place; a separate sold-lot
  record is created for just the sold portion, copying the holding's `buyPrice`/`buyDate` (cost
  basis for the sold lot is the holding's single Avg Price — this module doesn't track multiple
  buy-lots per holding, the same limitation the holdings table's "Avg Price" naming already
  documents, so this is not a true per-lot FIFO cost basis; stated directly in the form's helptext).

**ST/LT classification — ported, not re-derived, from ITRGenie.** Per explicit instruction,
`holdingPeriodDays()` and the classification logic inside `computeSoldLotGain()` are copied from
`itrgenie/index.html`'s `holdingPeriodDays()` (~line 1556) and `computeRowGain()` (~line
2485-2496) verbatim, not referenced cross-module (this module's existing self-containment
convention — same reasoning as the self-hosted `lib/` copies). **The exact boundary behavior
matches ITRGenie's real-world Sec 2(42A) correction**: holding period is a raw calendar-day
difference with no `+1`, and the classification is `days > 365 ? LongTerm : ShortTerm` — so a
holding sold on **exactly 365 days** is Short-Term, not Long-Term. Verified by test at all three
boundary points: 364 days → ShortTerm, exactly 365 days → ShortTerm, 366 days → LongTerm.

**The missing-cost-basis case — handled the same honest way as the rest of this module.** A sold
lot whose source holding never had a Buy Price (a CAS-imported holding sold before its Buy Price
was ever filled in) gets `buyPrice: null` copied onto the sold lot, and `computeSoldLotGain()`
returns `{gain: null, term: null}` for it — matching ITRGenie's own `computeRowGain()` exactly,
which withholds BOTH gain and term (not just gain) when cost basis is unknown, since classifying a
term without a trustworthy gain figure would be a half-honest result. The Record-a-sale form
surfaces this *before* the user even submits ("No Buy Price on file for this holding... gain will
show as unknown"), and the Realized Gains table shows "— unknown" (gold-colored, not a fabricated
number) for that lot's Gain/Loss cell and an "unclassified" tag for Term. **Closing the loop**:
unlike the holdings table (which was already inline-editable for this), the sold lot's Buy Price
and Buy Date are now *also* inline-editable directly in the Realized Gains table — the natural
place to fix a missing cost basis after the fact, since the source holding itself may no longer
exist (full sale). Filling either in immediately recalculates the lot's gain/term on the next
render.

**Realized gains view.** A new page section (`renderRealizedGainsSection`) right after "Record a
sale": three stat tiles (Short-term/STCG, Long-term/LTCG, Total realized), each summed in INR via
the same `toINR()`/unconverted-USD-lot handling `computePortfolio()` already uses (a sold lot's
gain is in its account's native currency — summing raw numbers across INR and USD lots without
converting would silently mix currencies), plus a sold-lots table (Symbol, Broker, Qty, Buy,
Sell, Term tag, Gain/Loss). Explicit gold-colored notes appear when relevant: N lot(s) with unknown
gain (no Buy Price), N lot(s) with a known gain but no Buy Date (excluded from the ST/LT split,
folded into "Total realized" but not guessed as short-term — same "flag it, don't fabricate it"
pattern as ITRGenie's own equity module's `incompleteDateRows`), N unconverted USD lot(s). **This
view is explicit that it is not a tax computation** — the section header states directly: "no
Section 112A ₹1,25,000 exemption, no slab-rate tax, no loss carry-forward applied here. Full tax
treatment happens in ITRGenie" — per the instruction that ITRGenie remains the single source of
tax-computation authority; Portfolio's job here is correct raw transaction facts only.

**Capital gains feed export — checked against ITRGenie's actual paste-input format, not assumed.**
Before building this, `itrgenie/index.html`'s `CapitalGainsEquityModule` and `CapitalGainsMFModule`
were read directly (their `render()` paste-card markup and paste-button `onclick` parsing logic) to
confirm the real format rather than guess at one:
- **Capital Gains — Equity module** takes `Stock, Qty, BuyDate, BuyPrice, SellDate, SellPrice` per
  line (6 comma/tab-separated fields; BuyDate/BuyPrice may be left blank when unknown, `cols.length
  >= 6` still required), parsed via the shared `parseFlexDate()` which accepts ISO (`YYYY-MM-DD`)
  dates as-is.
- **Capital Gains — Mutual Funds module** takes a fundamentally different shape:
  `Scheme, 112A-or-112, RedemptionDate, Cost, Gain, TDS` — it needs a pre-computed Gain figure and a
  Sec 112A (equity-oriented, STT paid) vs Sec 112 (debt-oriented) classification that Portfolio has
  no basis to know (this module doesn't track STT/fund-category data), so this session did not try
  to auto-map Mutual Fund sold lots into that shape — that would be guessing at a tax classification,
  exactly what this project's conventions warn against.

Given that, `buildCapitalGainsFeed()` produces the exact `{symbol, buydate, selldate, buyprice,
sellprice, qty, assetType}[]` contract from `MASTER_ROADMAP.md` (JSON download button, same pattern
as the existing Net Worth feed), and the "copy paste-ready lines" button formats each row as
`Symbol, Qty, BuyDate, BuyPrice, SellDate, SellPrice` (ISO dates, blank BuyDate/BuyPrice preserved
as empty fields, not omitted) — matching ITRGenie's Capital Gains — Equity module's paste format
field-for-field, verified against its actual parser rather than assumed. The card's helptext states
plainly that Mutual Fund sold lots need to be tagged Sec 112A/112 by hand once pasted into
ITRGenie's separate MF module, since Portfolio doesn't track that classification — an honest
limitation stated in-UI, not silently papered over.

**Testing.** Real headless Chromium (Playwright), 40 checks, all pass: full sale (holding removed
from open holdings, exactly one sold lot created carrying the full original qty, correct gain and
LongTerm classification for a >365-day sale); the ST/LT boundary at all three points described
above (364/365/366 days); partial sale (open holding's qty correctly reduced, sold lot correctly
created for just the sold portion, buyPrice/buyDate correctly copied); a sale against a CAS-imported
(no Buy Price) holding shows the "unknown gain, fix the Buy Price" state in both the sale form and
the Realized Gains table rather than a fabricated number (`buyPrice: null`, `computeSoldLotGain`
returns `{gain: null, term: null}`); oversell validation (selling more than the holding's current
open qty is rejected with a real error message, no sold lot created, holding qty unchanged); the
capital-gains feed's exact contract shape and values (including the `null` buyprice/buydate case for
an unknown-cost lot) and the paste-ready line's 6-field format; mobile viewport (375×812) — zero
horizontal overflow after the sale form and Realized Gains table render, helptext/table-cell fonts
read back ≥13px via computed-style; full regression of existing open-holdings functionality (guided
Add-a-holding form, bulk CSV paste, Net Worth feed export, and `computeHoldingMetrics`'
null-vs-zero handling for a holding missing a Buy Price) all still pass unchanged; STCG/LTCG totals
aggregate correctly in INR across multiple sold lots. Screenshots taken in both themes, desktop and
375px mobile, for visual review (not committed — see this entry for the description instead).

**What's still explicitly out of scope — the actual next step.** This session built the
prerequisite roadmap item 4 named ("Portfolio currently has no sell/capital-gains workflow...that
would need to be built as part of this item"). The what-if fund-switch simulation itself — "if I
sold Fund A and bought Fund B today, what would the tax cost of that specific switch be" — is
genuinely not attempted here: it needs this sold-lot/cost-basis data joined with ITRGenie's actual
tax-rate/exemption logic in a dedicated simulation UI, which is a distinct, sizeable piece of work
in its own right (not something to bundle into the same pass as building the underlying data model).
See `MASTER_ROADMAP.md`'s updated item 4 entry.

## Updated 2026-08-10 — Second-pass reviewer fixes on the sold-lot/realized-gains feature
The `financial-os-reviewer` subagent independently re-verified the sold-lot/realized-capital-gains
build above (commit `36f841d`) — confirmed the core math, ST/LT boundary logic, and honesty
invariants (never fabricating a gain from missing cost basis) all correct — but found two real
issues, fixed same-day, same pattern as the earlier Excel/CAS review cycles (2026-08-10 entries
above).

**1. The "Copy paste-ready lines (ITRGenie Equity format)" button didn't filter out Mutual Fund
sold lots.** Reviewer verified directly: a Mutual Fund sold lot alongside a Stock sold lot got
copied together, unfiltered, formatted for ITRGenie's Equity capital-gains module — which taxes
rows under Sec 111A/112A equity rules. A mutual fund redemption needs its own Sec 112A-vs-112
classification that only ITRGenie's separate MF module asks for; pasting one into the Equity module
would make ITRGenie confidently compute a wrong tax number for that row. Every other honesty-gap in
this module (unconverted USD, unknown-cost lots, unknown-term lots) was already handled by
explicitly excluding it and telling the user why — this was the one place that pattern was missed.
Fixed: `isMutualFundAssetType()` filters the copy-lines output to exclude Mutual Fund rows only
(everything else — Stock/ETF/Equity/Other/any free-text bulk-paste value — is treated as
equity-like); the feedback message now states the excluded count ("N mutual fund lot(s)
excluded — route those to ITRGenie's own MF capital-gains module by hand"), and an all-MF-lots
edge case shows a clear "nothing to copy" message instead of copying an empty line or crashing. The
JSON export (`buildCapitalGainsFeed()`) is deliberately left unfiltered, as instructed — it already
carries `assetType` per row, so a downstream consumer can filter it itself; this fix is specific to
the one-click paste-ready-lines shortcut, which had no such safety net.

**2. The "Record a sale" form silently wiped user-entered values on a validation error.**
Reviewer reproduced: Qty=3, Sell price=1500, blank Sell date, submit → correct "Sell date is
required" error shown, but Qty reverted to the holding's full default quantity and Sell price
cleared to blank, because the validation-failure path called the same full `render()` used
everywhere else, which rebuilds the form from scratch with default `value="${holding.qty}"`
attributes — discarding whatever the user had typed into the other fields. A user who then just
fixed the one field they saw complained about could silently sell the wrong quantity at no price
without noticing. Fixed by having the validation-failure path (`showSaleError()`) update only the
`#rs_feedback` text node in place, in every one of the five validation branches in the "Record
sale" button handler, instead of calling `render()` — the success path still calls the full
`render()` unchanged, since a real state change (holding qty/removal, new sold lot) genuinely
warrants resetting the form to fresh defaults there.
- **Checked, not assumed, whether the sibling "Add a holding" form already avoided this** (as the
  reviewer's report suggested it might, worth confirming before assuming the same fix pattern
  applied). It does **not** — a real headless-Chromium check found the exact same bug there too
  (Symbol/Qty/etc. also revert to blank on its own validation error). This was flagged, not fixed,
  in this pass — it wasn't part of the reviewer's two reported issues or this session's requested
  scope (the sold-lot feature specifically), so fixing it here would have widened the diff beyond
  what was asked; the fix pattern above (in-place feedback update instead of full `render()` on
  validation failure) would very likely apply cleanly to it too, and is the correct one to reuse in
  a future session. **Adding to Known gaps below.**

**Testing.** Real headless Chromium (Playwright), reproducing the reviewer's exact scenarios: (1)
seeded a Stock sold lot + a Mutual Fund sold lot, clicked the copy-lines button — clipboard
contained only the Stock lot's 6-field line, the Mutual Fund line was absent, the feedback showed
"1 mutual fund lot(s) excluded..."; confirmed the JSON export (`buildCapitalGainsFeed()`) still
returned both lots unfiltered; confirmed the all-Mutual-Fund-lots edge case shows a "nothing to
copy" message rather than an empty/broken copy. (2) Filled Qty=3/Sell price=1500, left Sell date
blank, submitted — confirmed Qty and Sell price were still exactly 3 and 1500 after the "Sell date
is required" error appeared (not reverted/cleared), confirmed no sold lot was created and the
holding's qty was unchanged; then filled in the date and resubmitted — confirmed the sale went
through with the originally-entered Qty (3) and Sell price (1500), not the holding's default full
quantity, and the holding's open qty correctly reduced by 3. (3) Regression pass: full sale
(holding removed, sold lot carries full qty, correct gain, LongTerm classification), ST/LT boundary
at all three points (364/365/366 days), missing-cost-basis honesty (`buyPrice: null` →
`{gain: null, term: null}`, never fabricated), partial sale (holding qty reduced correctly, sold
lot created for the sold portion only), and the paste-ready-lines 6-field format for a real
Stock-only export — all still pass unchanged. 30 checks total, all pass.

## Updated 2026-08-10 — What-if fund-switch tax simulator built (roadmap item 4, the last piece)
`MASTER_ROADMAP.md`'s item 4 stated the actual next step for this item was "the what-if
fund-switch simulation UI itself... needs this sold-lot/cost-basis data joined with ITRGenie's
actual tax-rate/exemption logic in a dedicated simulation UI." This session built exactly that —
a "Simulate a sale" section right after Realized gains, reachable via a new "What-if" button on
each Holdings-table row too.

**Before writing any code, ITRGenie's actual capital-gains tax computation was re-read directly**
(`itrgenie/index.html` ~line 4802-4818) to confirm the exact rates rather than assume them: equity
STCG (Sec 111A) is `Math.max(0,stcg)*0.20`; equity/equity-MF LTCG (Sec 112A) is
`Math.max(0, ltcg112a - 125000) * 0.125` — a per-financial-year pooled ₹1,25,000 exemption, not a
per-transaction one; debt-MF/non-112A LTCG (Sec 112) is `Math.max(0,ltcg112)*0.125` with **no**
exemption at all.

**Scope: domestic (INR) Stock/ETF/Equity/Other open holdings only — two deliberate exclusions,
each honestly explained in-UI rather than producing a wrong number.**
1. **Mutual Fund holdings.** Same reasoning already established for the capital-gains feed export:
   `itrgenie/index.html`'s `CapitalGainsMFModule` (~line 2510) requires the user to type in the
   real gain figure from an actual CAS/CAMS redemption statement rather than deriving it (post-2023
   debt-fund rule changes, indexation grandfathering, etc. are too fragile to formula-derive) — a
   hypothetical future sale has no such statement to read from. Selecting an MF holding in the
   simulator shows a `.notice` explanation pointing at ITRGenie's real MF module instead of a
   computed tax figure.
2. **Foreign-currency (non-INR / Vested-US) holdings — found while grounding this in ITRGenie's
   real logic, not something the task spec called out explicitly.** Reading further than the given
   line range, `itrgenie/index.html`'s `ForeignAssetsModule` and its use in the main computation
   (~4809-4818) show foreign LTCG is added to the *separate* `ltcg112` bucket (still 12.5%, but with
   **no** pooled exemption — it never joins `ltcg112a`), and foreign STCG is taxed at the person's
   income **slab rate** (folded into `slabIncomeBase`), not the flat 20% Sec 111A `stcg` bucket.
   Sec 111A/112A's concessional rates require STT paid on a recognized Indian stock exchange, which
   a foreign-listed holding (Vested-US) doesn't have by definition. Applying this simulator's
   domestic-equity math to a USD holding would produce a confidently wrong number, so it's excluded
   the same honest way Mutual Funds are — a `.notice.warn` box names the real distinction and points
   at ITRGenie's Foreign Assets (Schedule FA) module, rather than guessing at the real foreign-asset
   holding-period/rate rules (e.g. a possible 24-month LT threshold) which weren't independently
   verified here.

**Inputs**, on any open (qty>0) holding: Qty to hypothetically sell (defaults to the holding's full
qty, capped at it), Sell price (defaults to the holding's `currentPrice` if set — which is the same
field the live-price-feed and manual refresh already write into, so "live price if this holding has
one" and "last-known/manual price" are literally the same field, not two things to track separately
— else the holding's own Buy Price, else blank, always editable), Sell date (defaults to today,
editable — lets the user check "what if I wait until it's long-term"). A plain optional
"Considering switching to: ___" text field exists for the user's own reference only — deliberately
never computed against and never persisted (module-level var only, not written to
`portfolio_data_v1`), since this tool doesn't evaluate switch destinations, only the tax cost of
exiting the current holding.

**Gain + ST/LT classification** reuses `holdingPeriodDays()`/`LTCG_HOLDING_DAYS` verbatim — the
exact same function the sold-lot feature already ported from ITRGenie, not re-derived a third time.

**The exemption-pooling math (`computeWhatIfTax`)** — a pure function, no data mutation:
- Short-term: `tax = gain * 0.20` (gain already confirmed >0 by this point; a loss is handled
  separately, see below).
- Long-term: needs "how much Sec 112A LTCG has this person already realized this financial year" to
  compute the MARGINAL tax on the new hypothetical gain, since the exemption is a shared FY pool.
  `computeAlreadyRealizedLTCG112AThisFY(fyRange)` sums `data.soldLots` that are Sec-112A-eligible
  (not Mutual Fund, INR account — same two exclusions as above, applied to historical sold lots too,
  since a foreign or MF sold lot was never part of this pool in real tax law either) and classify
  LongTerm, whose sell date falls in the given FY — a straight sum, not clamped per lot, mirroring
  ITRGenie's own `ltcg112a = eqLT + mf112A` aggregation (clamped to >=0 only once, right before the
  exemption is applied). Then: `taxableBefore = max(0, pool - 125000)`,
  `taxableAfter = max(0, pool + gain - 125000)`, `tax = (taxableAfter - taxableBefore) * 0.125`.
- **A new `getFinancialYearRange()`/`isDateInFY()` helper pair** computes the Indian FY (April 1 –
  March 31) containing a given date and buckets other dates into it — built fresh, verified at the
  boundary (see Testing below), not reusing any inclusive/exclusive day-counting logic from
  elsewhere in this file that solves a different problem.
- **The "already realized this FY" figure is shown explicitly and is fully editable/overridable** —
  a labeled input pre-filled with the auto-computed figure, with helptext stating plainly it's only
  as complete as sold lots tracked in *this* Portfolio module ("sales made through a broker
  directly, or before you started using this tracker, aren't included here") and should be checked
  against the user's own records. Editing it stores an override (`whatIfPoolOverride`, module-level,
  not persisted); a "↺ use tracked value" button appears once overridden, to get back to the
  auto-computed figure without manually re-typing it.
- **A loss (negative or zero gain)** shows ₹0 tax and a note that it's a capital loss that could
  offset gains elsewhere, pointing at ITRGenie's "Loss Set-off & Carry Forward" module for the
  complete Sec 70 set-off ordering — deliberately not modeled here.

**Explicit disclosures**, stated in the section's own intro text: this shows only the capital-
gains-specific flat-rate tax (Sec 111A/112A) — no surcharge, cess, or interaction with the rest of
the person's income/tax regime; ITRGenie remains the source of truth for the actual return. Also
stated plainly: this tool doesn't model or evaluate what the money would be switched into — purely
the tax cost of exiting the current holding.

**Reachability**: a new "What-if" button sits next to the existing "Sell" button on every Holdings-
table row (`openWhatIfSale(holdingId)`, mirrors `openSaleForm`'s scroll-into-view pattern), plus the
section's own holding dropdown for picking any open holding directly.

**No data mutation, by construction, not just by testing discipline.** Every input
(qty/price/date/pool-override/note) lives only in module-level `whatIf*` state variables declared
near the top of the file — the render function reads `data.holdings`/`data.soldLots` to compute
defaults and the exemption pool, but never writes to either. Verified by test (see below): `data`
is byte-identical (via `JSON.stringify` comparison) before and after fully filling out and
"running" a simulation.

**Testing.** Real headless Chromium (Playwright), system clock frozen to 2026-08-10 so financial-
year math is deterministic and hand-checkable, 29 checks in the tax-logic suite + 14 in a full
regression/mobile suite, all pass:
- Clean equity STCG (held ~70 days): `computeWhatIfTax` and the rendered UI both match
  `gain * 0.20` exactly for a hand-picked ₹5,000 gain → ₹1,000 tax.
- Clean equity LTCG, zero prior sold lots this FY: a ₹60,000 gain (under the ₹1,25,000 exemption)
  correctly showed ₹0 tax; a second case with a ₹2,00,000 gain correctly showed ₹9,375 tax
  (`(200000-125000)*0.125`).
- **Pooling scenario A** — seeded one prior Sec-112A sold lot with a ₹1,00,000 gain this FY: the
  pool input auto-computed to exactly ₹1,00,000 (not a fresh ₹1,25,000); a new hypothetical
  ₹20,000 gain (headroom is ₹25,000) correctly showed ₹0 tax; a new hypothetical ₹40,000 gain
  (straddling the ₹25,000 headroom) correctly showed ₹1,875 tax
  (`taxableAfter=15000, taxableBefore=0, 15000*0.125=1875`).
- **Pooling scenario B** — seeded a prior sold lot with a ₹2,00,000 gain (already over the
  exemption): pool auto-computed to ₹2,00,000; a new ₹50,000 hypothetical gain was fully taxed —
  ₹6,250 (`50000*0.125`), confirming no exemption was double-applied.
- **FY-boundary correctness**: `getFinancialYearRange('2026-03-31')` → `{2025-04-01..2026-03-31}`;
  `getFinancialYearRange('2026-04-01')` → `{2026-04-01..2027-03-31}` — confirmed no off-by-one at
  the actual April 1 boundary. A sold lot dated 2026-03-31 (relative to "today" 2026-08-10, current
  FY = 2026-04-01..2027-03-31) was confirmed excluded from the pool (₹0); the same lot moved to
  2026-04-01 was confirmed included. A sold lot from 13 months before "today" (a different FY
  entirely) was confirmed excluded.
- Mutual Fund holding: confirmed the exclusion `.notice` renders (naming CAS/CAMS), confirmed no
  "Estimated capital-gains tax" figure is shown, confirmed the qty/price/date inputs aren't even
  rendered for this case (blocked, not silently computed).
- Foreign (Vested-US/USD) holding: confirmed the exclusion `.notice.warn` renders (naming Sec 112 /
  slab-rate STCG / Schedule FA), confirmed no tax figure shown.
- **Data-mutation guarantee**: filled in qty/sell price/sell date on a real holding, confirmed
  `data.holdings`/`data.soldLots` were byte-identical before and after (via JSON comparison), and
  the holding's `qty` was still its original value, not reduced.
- Over-sell validation (qty > currently held) shows a real error message, not a tax figure.
- Loss case (sell price below buy price): confirmed ₹0 tax and the capital-loss/Loss-Set-off-module
  pointer text.
- Full regression: guided "Add a holding" form, "Record a sale" (still creates a real sold lot and
  reduces the source holding's qty), Realized gains section, capital-gains feed export card, Net
  Worth feed card, Export/Import JSON round-trip, and the theme toggle all still work unchanged.
  Opening the What-if panel via a holdings-row button was confirmed to not mutate `data.holdings`.
- Mobile viewport (375×812): zero horizontal overflow (`scrollWidth` stayed at 375px) with the
  What-if section rendered; its helptext read back ≥13px and labels ≥11px via computed-style
  (matching this module's existing mobile type-size floor). Screenshots taken in both themes,
  desktop and mobile, for visual review (not committed — matches this module's existing pattern of
  passing screenshots back for review rather than checking them into the repo).

**What's still explicitly out of scope, stated plainly in-UI, not silently done:** surcharge, cess,
and slab-rate/other-income interaction (ITRGenie's job); Mutual Fund capital-gains tax (needs a real
CAS/CAMS redemption statement, which a hypothetical sale can't have); foreign-holding capital-gains
tax (needs ITRGenie's Foreign Assets/Schedule FA module — the real foreign-asset holding-period and
rate rules weren't independently verified here beyond confirming the bucket split in ITRGenie's own
code); loss set-off ordering across multiple gains/losses (ITRGenie's Loss Set-off & Carry Forward
module); and what the sale proceeds would be switched into (the optional note field is for the
user's own reference only, nothing about a destination is computed). **This closes
`MASTER_ROADMAP.md`'s item 4** — see that file's updated entry.

### Fix (2026-08-10, same day) — reviewer-found eligibility gap
The `financial-os-reviewer` audit of the what-if simulator found one real (if
low-reachability) safety gap: `isSec112AEligibleHolding`/`isSec112AEligibleSoldLot`
and the what-if UI's own `isForeign` check both trusted `accountOf(brokerId)`,
which silently falls back to `{currency:'INR'}` for a broker id matching no
real account — reachable only via a hand-edited or corrupted Export/Import
JSON with a typo'd broker id, since every real entry path (guided form, paste,
Excel/CAS import) always resolves to a genuine account id. Under that one
narrow path, the simulator would have confidently computed a domestic Sec
111A/112A tax figure for a holding whose real currency was actually unknown —
the exact "wrong-but-confident number" failure mode this module exists to
avoid everywhere else. Fixed by checking `data.accounts.some(a=>a.id===...)`
before trusting `accountOf(...).currency`, in both the exemption-pool helpers
and the what-if UI's own eligibility gate (which didn't call those helpers at
all — the real gate was inline `acc.currency !== 'INR'`, so both spots needed
the fix, not just the higher-level one). An unrecognized account now shows an
honest "account isn't recognized, currency can't be confirmed" message
instead of either a wrong number or a self-contradictory "foreign-currency
account (INR)" label. Verified directly: seeded a holding with a broker id
matching no account — confirmed no tax figure is computed and the new message
renders; re-verified the normal INR case still computes the same ₹9,375
example from the original build, and the legitimate foreign-currency (Vested
US) exclusion still renders unaffected.

## Known gaps — flagged deliberately, not resolved by guessing
Per explicit instruction not to silently resolve these, and not to fabricate
functionality to paper over them:

1. **Live price feed — Tier 1 (Yahoo) confirmed broken in at least one real browser
   (user report, 2026-08-09); Stooq (Tier 1b) added the same day as a second
   no-key attempt, itself unverified for NSE.** See the two dated entries
   above for the full picture. Three layered options now exist (Yahoo, no
   setup; Stooq, no setup, US-ticker format confirmed but NSE format is a
   best-effort guess; Twelve Data, optional key, confirmed working for both
   NSE and US against the old Drive prototype). All three are defensively
   built (malformed/negative/missing prices rejected, failures always shown,
   existing prices never silently overwritten), and a total failure now
   surfaces a direct link to the Twelve Data setup in Live Prices settings
   instead of an opaque error. What's still open: nobody has run Tier 1 or
   Tier 1b against the real internet from this build environment (its own
   sandbox blocks outbound network to arbitrary hosts) — Tier 1 is now known
   broken in at least one real case, Tier 1b's real behavior is completely
   untested either way. Twelve Data (Tier 2) is the one path with actual
   real-world provenance.

2. **The "dark-terminal, Twelve Data, technical indicators" Portfolio
   Tracker referenced in earlier project notes was never located.**
   `networth/PROGRESS.md` already flagged this same ambiguity (the only
   Portfolio-related file found in an earlier search was a "Portfolio
   Ledger" tab inside a separate combined ITR+Portfolio app, not this
   description). This session did not have access to search elsewhere, and
   did not try to reconstruct that specific unseen design from memory or
   guesswork. This module was built fresh against this repo's actual,
   verifiable design system — the same light/dark toggle every other module
   uses, not a fixed dark-terminal look — rather than imitating an unseen
   reference. If that old file turns up later, treat it as a design
   reference to compare against, not a spec to have silently matched.

3. **5+ years of historical portfolio data in Google Drive has not been
   reconciled against this data model.** `MASTER_ROADMAP.md`'s 2026-08-07
   entry explicitly flags this as the intended resource for both building
   and testing the Portfolio module's logic. This session had no Google
   Drive access, so the data model above (accounts/holdings/fx shape,
   assetType as a free-text field, the specific paste-column order) is a
   reasonable first design based on the roadmap's stated scope — it has
   **not** been validated against real trade history. A future session with
   Drive access should pull that data and check it actually fits before
   this is treated as final; expect some rework (e.g. assetType taxonomy,
   corporate actions like splits/bonuses/dividends reinvested, closed/sold
   positions) once real data is run through it.

4. **CAS (NSDL/CDSL demat statement) PDF parsing (`parseCasPdfText`,
   2026-08-10) is UNVERIFIED against a real CAS document.** This session had
   no real CAS file (or its password) to test against — see the dated
   2026-08-10 entry above for exactly what was and wasn't verified. The
   password-unlock mechanics, the Excel fuzzy-matching, and the parser's
   *behavior* against a synthetic CAS-shaped test file are all confirmed
   real; whether the ISIN-anchored line-parsing heuristic matches a real
   statement's actual text layout is not. Kept in one small, isolated,
   clearly-commented function specifically so it's fast to revise once a
   real CAS is available — that's the next natural verification step, not a
   guess to be resolved by assumption.

5. **Dedup only catches duplicates *within* the same import path, not
   *across* different import paths for the same real-world holding
   (found by `financial-os-reviewer`'s second-pass review, 2026-08-10).**
   `findDuplicateHoldingIndex` matches by ISIN when both sides have one,
   else by broker+symbol. A holding imported via CAS gets `symbol` set to
   a full company name (e.g. "INFOSYS LTD") plus an `isin`; the same
   holding imported later via Excel/paste typically has a ticker
   ("INFY") and no ISIN at all. Neither side of the match condition fires:
   there's no ISIN on the Excel/paste side to compare, and "INFY" vs.
   "INFOSYS LTD" don't match as symbol text either — so a genuine
   duplicate can still be created if the same real holding is imported via
   two different paths (e.g. CAS first, then later an Excel export from
   the same broker). Within a single import path (CAS re-imported, or the
   same Excel file re-imported, or the same row pasted twice) dedup works
   correctly — this gap is specifically cross-path. Not fixed in this
   pass: it needs a real decision (e.g. a maintained ticker↔ISIN or
   ticker↔company-name mapping) rather than a quick patch that could
   silently merge two genuinely different holdings that happen to share a
   loosely similar name.
6. **The "Add a holding" form has the same validation-error-wipes-input bug
   the "Record a sale" form had (found while fixing the latter, 2026-08-10
   second-pass review).** Confirmed with a real headless-Chromium check, not
   assumed: filling Symbol + Qty but leaving Buy Price blank and submitting
   shows the correct "Fill in Symbol, Broker, Qty..., Buy Price and Buy
   Date" error, but Symbol and Qty are both wiped back to blank — same root
   cause as the sale form's bug (the validation-failure path calls the full
   `render()`, which rebuilds the form fresh with no `value="..."`
   preserving what was typed). Not fixed in this pass — it wasn't one of the
   reviewer's two reported issues or this session's requested scope (the
   sold-lot feature specifically); flagged here rather than silently left
   for someone to rediscover. The fix pattern used for the sale form
   (`showSaleError()` — update the feedback text node in place instead of
   calling `render()` on a validation failure) would very likely apply
   cleanly here too, in a future session.
7. **The what-if sale simulator's foreign-holding exclusion (2026-08-10) states the real bucket
   split (Sec 112 for LTCG, slab-rate for STCG) but does NOT independently verify the exact
   long-term holding-period threshold for foreign shares.** `itrgenie/index.html`'s
   `ForeignAssetsModule` takes the user's STCG/LTCG figures as direct manual entry — it never
   computes a holding-period boundary for foreign assets itself, so there was no code to read this
   threshold from (unlike the 365-day equity boundary and the 730-day/24-month House Property
   boundary, both of which ARE computed in ITRGenie and were verified against directly). This
   module's simulator sidesteps the question entirely by refusing to compute a foreign-holding tax
   figure at all (see the dated 2026-08-10 entry above) rather than guessing at that threshold —
   flagged here so a future session doesn't assume it was checked.
8. ~~**The Holdings tab is noticeably heavier than the other three**~~ — **CLOSED 2026-08-11.**
   Accounts, FX, and Live-price settings moved to the renamed "Accounts & Settings" tab (formerly
   "Export & Settings") — see that dated entry below. Holdings is now scoped to table + entry/import
   only; Accounts & Settings holds account configuration + the Net Worth feed export.

## Deliberately NOT done yet
- **~~The what-if fund-switch tax-modeling UI itself~~ — built 2026-08-10 (see the dated entry
  above), closing `MASTER_ROADMAP.md`'s item 4.** Scoped to "tax cost of exiting the current
  holding," not "simulate switching Fund A to Fund B" literally — the destination-fund side was
  deliberately left uncomputed (an optional free-text note only), per instruction, since evaluating
  a destination investment is a different, unscoped problem from computing exit tax cost.
- Sold-lot cost basis is this module's single per-holding Avg Price, not a
  true per-lot FIFO cost basis — if a holding was built up from multiple buys
  at different prices (this module only ever stores one buy price per
  holding), a partial sale's cost basis is that one average price, not the
  actual lot(s) sold. Real historical data (gap #3 below) would clarify
  whether per-lot buy tracking is ever actually needed here.
- Mutual Fund sold lots aren't auto-mapped into ITRGenie's Capital Gains —
  Mutual Funds module's paste format (`Scheme, 112A-or-112, RedemptionDate,
  Cost, Gain, TDS`) — that format needs a Sec 112A vs 112 classification this
  module has no basis to know (no STT/fund-category tracking). The capital
  gains feed's paste-ready-lines button matches the Capital Gains — Equity
  module's format instead, which works for any assetType's raw transaction
  facts; the UI states plainly that MF sales need manual 112A/112 tagging
  once pasted into ITRGenie's MF module.
- No corporate-actions handling (splits, bonuses, dividends, mergers) — buy
  price/qty are taken as entered; adjusting historical cost basis for these
  events is out of scope until real historical data (gap #3) shows it's
  actually needed.
- No CAMS/KFintech mutual-fund CAS parsing (folio number/AMC/scheme/units/
  NAV structure) — deliberately scoped out of the 2026-08-10 CAS import work.
  Its text layout differs enough from an NSDL/CDSL demat CAS that a
  half-built parser for it would produce worse results (confidently wrong
  data) than the current behavior (a clear "not recognized, try Excel or
  manual entry" message). NSDL/CDSL demat CAS was prioritized because it
  maps directly onto this module's existing Stock/ETF holdings model; MF CAS
  would need its own parser and probably its own preview UI, not a small
  extension of this one.

## Design invariants (same as every other module)
- Zero external dependencies, works offline once loaded. Self-hosted
  libraries live under `portfolio/lib/` (`xlsx.core.min.js`, `pdf.min.js`,
  `pdf.worker.min.js`, added 2026-08-10) — copied from `itrgenie/lib/`, not
  referenced cross-module, so this module stays independently self-contained
  (same reasoning as ITRGenie not referencing Net Worth's files).
- Paste-and-parse plus CSV/TXT/**Excel (.xlsx/.xls)** file upload (bulk
  add/advanced, collapsed by default), not form-fields-only — a guided
  single-holding form (added 2026-08-09) is the primary entry path, but
  paste/upload remains a fully supported, non-removed alternative, per this
  repo's convention. Excel files get real binary parsing + fuzzy column
  detection (added 2026-08-10), not the plain-text comma parser. A separate
  **CAS (NSDL/CDSL demat statement) PDF import** path (also added
  2026-08-10) is the broker-agnostic option for a user's most
  readily-available document — see the dated entry above; its holdings
  always import with Buy Price left blank (a CAS has no cost-basis data),
  never a fabricated `marketValue/qty` mislabeled as buy price.
- Shared theme key: `itrgenie_theme`.
- Own data storage key: `portfolio_data_v1` — never writes into Net Worth's,
  Goals', or any other module's key. Feeds Net Worth only via explicit
  export, never by writing into its localStorage key directly.
- Live prices are the one deliberate, narrow exception to "nothing leaves
  the browser" — scoped only to public symbol/price lookups (Yahoo Finance,
  Stooq, and Twelve Data if a key is saved), disclosed plainly in-UI, never
  carrying holdings/personal data. The Twelve Data key lives in its own
  storage key, `portfolio_livekey_v1`, separate from `portfolio_data_v1` so
  it's never included in the Export JSON backup. Excel and CAS PDF import
  (2026-08-10) do NOT call out to the network at all — all parsing (SheetJS,
  PDF.js) runs entirely client-side on the file the user picked.
- Mobile viewport (down to 375px) gets its own font-size and table-layout
  rules under `@media (max-width:760px)` — desktop sizing stays denser by
  design; don't remove the mobile block thinking it's redundant with base
  styles.
- A holding's `buyPrice` (and therefore `costBasis`/`gainAbs`/`gainPct`) can
  now genuinely be unset (CAS-imported, awaiting manual entry) — every
  aggregate that sums cost/gain (`computePortfolio`, the top stat tile, the
  "By account" breakdown) must treat this as excluded-and-flagged, never as
  a cost basis of zero, per the 2026-08-10 fix. Any future change to
  `computeHoldingMetrics`/`computePortfolio` must preserve `hasBuyPrice` /
  `null`-vs-`0` handling rather than reintroducing `+h.buyPrice || 0`.
- `xlsx.core.min.js` and `pdf.min.js` (added 2026-08-10 build to `lib/xlsx.core.min.js` and
  `lib/pdf.min.js`) are lazy-loaded, not blocking `<head>` `<script>` tags (fixed 2026-08-10,
  follow-up) — do not re-add unconditional `<script src>` tags for either; use
  `ensureXlsxLoaded()`/`ensurePdfJsLoaded()` (which cache via `loadScriptOnce()` and set
  `pdfjsLib.GlobalWorkerOptions.workerSrc` right after `pdf.min.js` resolves, not at page-init
  time) from wherever a new consumer needs either library. `pdf.worker.min.js` stays as-is — it's
  fetched lazily by PDF.js itself once `getDocument()` runs, nothing to change there.
- Every commit path that adds holdings from an import (CAS, Excel, bulk paste — fixed 2026-08-10,
  follow-up) must run new rows through `findDuplicateHoldingIndex()` before pushing to
  `data.holdings`, matching by ISIN when available, else broker+symbol. CAS import updates a
  matched holding in place (qty/currentPrice/asOf refreshed, buyPrice/buyDate left untouched);
  Excel/paste default to skip-with-a-visible-count-and-override-checkbox. A future new import path
  (or a change to any of the three existing ones) that pushes to `data.holdings` without this check
  reintroduces the exact "importing the same document twice doubles your portfolio" bug this fix
  closed.
- The CAS and bulk-add `<details>` panels' `ontoggle` handlers must only call
  `ensurePdfJsLoaded()`/`ensureXlsxLoaded()` when the corresponding load state is `'idle'`
  (fixed 2026-08-10, second-pass reviewer fix) — never unconditionally on every `open`-toggle.
  Because `render()` rebuilds these `<details>` nodes from scratch on every state change, and
  `el.open = true` on a fresh node fires a synthetic Chromium `toggle` event with no user
  interaction involved, an unconditional call here retries a failed (`'error'`-state) load forever
  in a tight loop (measured ~15-23 req/sec before the fix). The real retry-on-error path is the
  user picking a file — `handleExcelFileSelected`/`handleCasFileSelected` already call
  `ensure...Loaded()` directly, and that call is allowed to retry since it's genuinely
  user-triggered. Don't remove the `pdfjsLoadState==='idle'`/`xlsxLoadState==='idle'` guard from
  either `ontoggle` handler.
- **Sold-lot tracking (added 2026-08-10) lives in `data.soldLots`, same storage key
  (`portfolio_data_v1`), not a separate one** — it's this module's own data, per this repo's "own
  data storage key" convention meaning *one key per module*, not one key per feature. A full sale
  removes the source holding from `data.holdings`; a partial sale reduces its `qty` in place and
  pushes one `soldLots` entry for the sold portion — any future change to the sale-recording path
  must preserve both halves of that transaction (never leave a sold lot without correspondingly
  updating/removing the source holding, or vice versa).
- **`holdingPeriodDays()`/`computeSoldLotGain()`'s ST/LT boundary is copied verbatim from
  `itrgenie/index.html`'s `holdingPeriodDays()`/`computeRowGain()`, not referenced cross-module or
  re-derived.** The rule is `days > 365 ? LongTerm : ShortTerm` computed via a raw (`no +1`)
  calendar-day difference — exactly 365 days held is Short-Term per the real Sec 2(42A) correction
  already baked into ITRGenie. Do not "simplify" this to `>= 365` or reuse the inclusive
  `daysBetween()`-style day counting used elsewhere for travel/presence-day counts — those are a
  different, deliberately inclusive calculation for a different purpose. If ITRGenie's own
  `holdingPeriodDays()`/`computeRowGain()` boundary logic ever changes, this module's copy needs the
  matching update, since there's no shared reference between the two files by design.
- A sold lot's `buyPrice`/`buyDate` can genuinely be unset (copied from a CAS-imported holding that
  was sold before its Buy Price was ever filled in) — `computeSoldLotGain()` returns `{gain: null,
  term: null}` for these, matching ITRGenie's `computeRowGain()`'s exact behavior of withholding
  BOTH fields (not just gain) when cost basis is unknown. Any future change to
  `computeSoldLotGain()`/`computeRealizedGains()` must preserve this `null`-vs-fabricated-zero
  handling, same as the existing `hasBuyPrice` convention for open holdings above.
- **The "Copy paste-ready lines (ITRGenie Equity format)" button must always run through
  `isMutualFundAssetType()` before copying (fixed 2026-08-10, second-pass reviewer fix)** — never
  copy a Mutual Fund sold lot into that button's output. ITRGenie's Equity module taxes rows under
  Sec 111A/112A equity rules; a mutual fund needs its own Sec 112A-vs-112 classification this module
  has no basis to know, so an unfiltered copy would make ITRGenie confidently compute a wrong tax
  number for that row. The JSON export (`buildCapitalGainsFeed()`) is deliberately left unfiltered
  on purpose (it carries `assetType` per row for a downstream consumer to filter itself) — don't
  "fix" that by filtering the JSON too, and don't remove the filter from the copy-lines button
  thinking it's now redundant with the JSON's `assetType` field.
- **The "Record a sale" form's validation-failure path must update `#rs_feedback` in place
  (`showSaleError()`), never call the full `render()` (fixed 2026-08-10, second-pass reviewer
  fix).** `render()` rebuilds the form from scratch with fresh `value="${holding.qty}"` / blank
  defaults, silently discarding whatever the user had typed into the other fields — a real risk of
  someone unknowingly submitting the wrong qty/price after fixing just the one field they saw an
  error about. The success path is unaffected and still calls the full `render()`, since a genuine
  state change (holding qty/removal, new sold lot) correctly warrants resetting the form. Any new
  validation branch added to this form's submit handler must call `showSaleError()`, not set
  `saleFormFeedbackMsg` directly and call `render()`.
- **The "Simulate a sale" what-if tax calculator (added 2026-08-10) must stay purely computational —
  never write to `data.holdings`/`data.soldLots`, never call `saveData()`.** All of its state
  (selected holding, qty/price/date, pool override, note) lives only in module-level `whatIf*`
  variables, read fresh on every `render()`. Any future change to this section must preserve that —
  it's the one feature in this module explicitly designed to have zero side effects on stored data.
- **`isSec112AEligibleHolding()`/`isSec112AEligibleSoldLot()` (both MF-excluded AND non-INR-account-
  excluded) gate both halves of the what-if simulator — the hypothetical sale itself and the
  "already realized this FY" exemption pool it's computed against.** A future change that adds a
  new non-INR account or a new MF-like assetType must keep both eligibility checks in sync (they're
  intentionally two small separate functions, not one shared with the sold-lot/capital-gains-feed
  code elsewhere in this file, since a holding and a sold lot are different shapes) — don't let one
  learn about a new exclusion the other doesn't.
- **`getFinancialYearRange()`/`isDateInFY()` are this module's own Indian-FY (April 1 – March 31)
  helpers, separate from `holdingPeriodDays()`.** Don't conflate them — `holdingPeriodDays()`
  computes a raw day-count for ST/LT classification (Sec 2(42A)), while `getFinancialYearRange()`
  answers a completely different question ("which FY does this date fall in," for the Sec 112A
  exemption-pool computation). Both are real, independently boundary-tested — see the 2026-08-10
  entry above for the exact FY-boundary test cases (March 31 vs April 1).
- **The page is organized into four tabs (added 2026-08-11): Dashboard, Holdings, Gains & What-If,
  Accounts & Settings (id `accounts`, renamed 2026-08-11 from "Export & Settings"/id `export` in the
  same dated rebalance pass that moved Accounts/FX/Live-price settings there — see the dated entries
  below for the exact section-to-tab mapping, both original and rebalanced).**
  `switchTab()` must never call the full `render()` — it only toggles `.tab-pane` visibility via
  `applyTabVisibility()`, deliberately, so that merely clicking between tabs can never wipe an
  in-progress form (all four panes are always fully built on every `render()`, just hidden/shown).
  A new section added to this module in the future should be appended into whichever existing
  `tab-pane` container fits it thematically (or a new one, added to the `TABS` array), not appended
  directly to `content` the way sections were before this session. Any function that
  `scrollIntoView`s a panel that isn't on the currently-active tab (the pattern
  `openSaleForm`/`openWhatIfSale`/`openLiveSettings` use) must set `activeTab` to that panel's tab
  before calling `render()`, or the scroll/focus will silently no-op against a `display:none`
  element — `openLiveSettings()` picked this up on 2026-08-11 when Live Prices settings moved to the
  `accounts` tab (it previously didn't need to, since it lived on the same tab as every caller).
- **`renderGainersLosersCard`/`renderConcentrationCard` (Dashboard, added 2026-08-11) must keep the
  same honesty gates as the rest of this file.** Gainers/losers only includes holdings with
  `hasBuyPrice` true (via `computeHoldingMetrics`) — never fabricates a gain for a CAS-imported
  holding with no Buy Price, same pattern as `computePortfolio`/the stat tiles. Concentration's
  top-2-holdings check only evaluates once there are `>=3` priced holdings (with 1-2 holdings
  total, "most of the portfolio is in the top 2" is true by construction, not a real signal) — don't
  drop that guard when touching this code later.
- **Sold lots (Gains & What-If tab) default to showing only the most recent
  `SOLD_LOTS_COLLAPSE_THRESHOLD` (10) via `soldLotsShowAll` (added 2026-08-11) once there are more
  than that many.** This only limits which rows `renderRealizedGainsSection` renders in the table —
  `computeRealizedGains()`'s STCG/LTCG/Total stat tiles and `buildCapitalGainsFeed()`'s export always
  operate over the full `data.soldLots`, uncollapsed. Don't let a future change to the sold-lots
  table slice the underlying array itself; only the rendered rows should ever be limited.

## Updated 2026-08-11 — Tab sub-navigation (pure reorganization, no feature/logic changes)
The page had grown to 17 stacked render functions on one long scroll over several sessions. Per
explicit direction (referencing Value Research's "My Investments" portfolio manager, which uses
Dashboard/Overview/Performance/Analysis/Tax Report/Transactions/Alerts tabs instead of one long
page), this session added a tab bar and regrouped the existing sections into it. **This was
deliberately scoped as reorganization only — zero new features, zero changes to any render
function's internal markup/math/behavior.** `git diff` on this change touches only: new CSS for
`.tab-bar`/`.tab-btn`, a new `renderTabBar()`/`switchTab()`/`applyTabVisibility()` trio, two
one-line additions to `openSaleForm()`/`openWhatIfSale()` (see below), and the master `render()`
function's wiring of which container each existing `renderXxx(container)` call appends into. No
render function's own body was touched.

**Final tab structure — every one of the 17 original sections accounted for:**
- **Dashboard** (`activeTab='dashboard'`) — `renderPerformanceSummary`, then an "Allocation &
  performance" sub-heading, `renderAllocationCard`, `renderBrokerBreakdown`. The "what's my
  situation right now" overview, exactly as scoped.
- **Holdings** (`activeTab='holdings'`) — `renderHoldingsTable`, `renderAddHoldingForm`,
  `renderHoldingsEntryCard` (which internally calls `renderXlsxImportPreview` when a file is being
  previewed — unchanged), `renderCasImportCard` (which internally calls `renderCasBody` —
  unchanged), `renderLiveSettingsCard`, then an "Accounts & FX" sub-heading, `renderAccountsCard`,
  `renderFxCard`. Everything about viewing and entering/importing holdings data, matching the
  original task grouping exactly.
- **Realized Gains & What-If** (`activeTab='gains'`) — `renderRecordSaleForm`,
  `renderRealizedGainsSection`, `renderWhatIfSaleSection`. The sold-lot tracking and tax-simulation
  cluster, unchanged order.
- **Export & Settings** (`activeTab='export'`) — `renderNetWorthFeedCard`.
- **`renderKnownGapsCard`** was deliberately NOT put in the Export & Settings tab — per the task's
  own suggestion, it's rendered once, outside all four tab-pane containers, so it's visible
  regardless of which tab is active (a page-wide disclosure a user might otherwise never click into
  if it were gated behind one specific tab). Verified there is exactly one `<details>` "Known gaps"
  element in the DOM at all times, not duplicated per tab.

**Tab labels**: Dashboard / Holdings / Realized Gains & What-If / Export & Settings — the task's
starting-point grouping read naturally once the actual sections were laid out, so no regrouping
was needed beyond what was proposed.

**Mechanics — chosen specifically to avoid a re-render-wipes-drafts bug.** `render()` still does
`content.innerHTML=''` and rebuilds all four tab panes plus the tab bar on every real state change
(adding a holding, recording a sale, etc.) — that data-mutation-driven full-rebuild behavior is
unchanged from before this session. What's new: each of the four panes is wrapped in a
`<div class="tab-pane" data-tab="...">` and **all four are always fully built on every render()**,
just hidden via `style.display='none'` for the non-active ones (`applyTabVisibility()`, called at
the end of `render()` and by `switchTab()`). Clicking a tab pill calls `switchTab()`, which **does
NOT call `render()`** — it only re-runs `applyTabVisibility()` against the already-built DOM. This
means merely browsing between tabs can never wipe an in-progress "Add a holding" / "Record a sale"
/ what-if form the way a fresh `render()` would (the same class of bug found and fixed earlier the
same day in `goals/index.html`) — confirmed by test (see below), not just designed defensively.
A genuine state change still resets *other* sections' unsubmitted input exactly as it always did
(pre-existing behavior, tracked as Known gap #6 below — out of scope for a pure reorganization to
fix).

**Cross-tab jump fix required for two existing functions.** The Holdings table's per-row "Sell" and
"What-if" buttons (`openSaleForm`/`openWhatIfSale`) `scrollIntoView` their target panel after
setting state and calling `render()` — but those panels (`#sale-form-panel`, `#whatif-panel`) now
live in the Realized Gains & What-If tab, a different tab than the Holdings table that triggers
them. Both functions now also set `activeTab = 'gains'` before their existing `render()` call, so
the target panel is actually visible (not `display:none`) by the time `scrollIntoView`/`.focus()`
run. This is the one behavioral addition beyond "which container it renders into" — without it,
clicking Sell/What-if from the Holdings tab would silently no-op (`scrollIntoView` on a hidden
`display:none` element is a no-op, no error thrown). Verified by test: clicking either button
switches the active tab pill to "Realized Gains & What-If" and the target panel is visible.

**Mobile (375×812)**: the tab bar is a horizontally-scrollable row (`.tab-bar{overflow-x:auto}`,
`-webkit-overflow-scrolling:touch`), not wrapped/cramped pills — confirmed all 4 tab buttons remain
in the DOM and reachable, tab-button font-size reads back ≥13px via computed style (14px under the
`max-width:760px` mobile block), and `document.documentElement.scrollWidth` never exceeds the
375px viewport on any of the 4 tabs, in both themes. Screenshots taken (not committed) for visual
review — the active tab shows the gold color + 2px gold bottom-border pattern already used
elsewhere in this app's design language (sortable table headers, etc.), no new visual pattern
introduced.

**Testing.** Real headless Chromium (the environment's pre-installed `/opt/pw-browsers` build,
since `cdn.playwright.dev` is blocked by this session's outbound network policy — `npx playwright
install` fails there; used the already-present global install instead), both themes, desktop and
375×812 mobile:
- **Structure** (17 checks): all 4 tabs present with the expected labels; Dashboard is the default
  active tab on load; each tab's pane becomes visible (and all others hidden) on click; each tab
  contains the expected section headings; the Known Gaps card is visible regardless of active tab
  and appears exactly once in the DOM; zero console/page errors in either theme.
- **Real interactions, not just DOM presence** (23 checks): added two holdings via the guided "Add
  a holding" form on the Holdings tab and confirmed both appear; confirmed the Dashboard tab's stat
  tiles and asset-allocation legend reflect the new holdings; clicked a Holdings-row "Sell" button
  and confirmed the cross-tab jump to Realized Gains & What-If with the sale form visible; recorded
  a real partial sale (4 of 10 units) and confirmed the sold lot appears in Realized Gains and the
  source holding's remaining qty is correct; confirmed the "Record a sale" form's existing
  validation-error-preserves-input behavior (Qty/Sell price un-wiped on a blank-date error) still
  works post-move; clicked a Holdings-row "What-if" button, confirmed the cross-tab jump, and
  **reproduced this session's own documented ₹9,375 tax figure** (a ₹2,00,000 LTCG gain against a
  fresh/zero exemption pool: `(200000-125000)*0.125 = 9375`) using a freshly seeded long-held
  holding; clicked the capital-gains "Copy paste-ready lines" button and confirmed no crash; clicked
  the Net Worth feed's "Download JSON" button on the Export & Settings tab and confirmed a real file
  download fires; confirmed the Live Prices settings card renders on the Holdings tab; **confirmed
  the Add-a-holding form's typed-but-unsubmitted Symbol/Qty values survive switching away to
  Dashboard and back** (the specific regression this session's tab mechanics were designed to
  avoid); confirmed the bulk-paste textarea's typed-but-unsubmitted draft also survives a tab
  switch (see note below); multiple tabs switched in varied order (7 switches) with zero console/
  page errors throughout the whole run.
- **Mobile (375×812), both themes** (10 checks): zero page-level horizontal overflow on every tab;
  tab bar has real internal `overflow-x` scroll; all 4 tab buttons present in the DOM; tab-button
  font-size ≥13px; active tab has a visible bottom-border; zero console/page errors.
- **Data persistence unaffected**: added a holding, reloaded the page fresh (not just re-rendered),
  confirmed the holding survives (localStorage, unchanged by this session) and the tab correctly
  resets to Dashboard (in-memory `activeTab`, not persisted — a fresh page load intentionally always
  starts on Dashboard, matching how every other in-memory UI-state variable in this file already
  behaves, e.g. `liveSettingsOpen`/`bulkAddOpen` are also not persisted across reloads).
- **One test-methodology note, not a regression**: while testing the bulk-paste textarea's draft
  survival, an early version of the test (typing immediately after first-opening the "Bulk add"
  panel, then switching tabs within ~100ms) intermittently saw the draft cleared. Root-caused to a
  **pre-existing, unrelated** background behavior: opening that panel for the first time triggers
  `ensureXlsxLoaded()` (lazy-loading `xlsx.core.min.js`, built 2026-08-10), which calls `render()`
  once when the load starts and again when it resolves/fails — both already existed before this
  session and are unrelated to tab-switching (confirmed directly: the same draft-loss reproduces
  with zero tab switches at all if you type before that second `render()` fires). This is a
  pre-existing race between "first panel open" and "typing immediately," not something this
  session's tab mechanism introduced or made worse — the test was adjusted to let that unrelated
  async settle first, after which the tab-switch draft-survival check passes cleanly and
  repeatably. Not added as a new Known gap since it's a narrow, pre-existing timing window in
  already-shipped 2026-08-10 code, out of this reorganization's scope to touch.

**What wasn't independently re-verified beyond the checks above**: the CAS PDF import flow itself
(password unlock, ISIN-anchored parsing) and the live-price fetch providers (Yahoo/Stooq/Twelve
Data network calls) were not re-exercised end-to-end in this pass — both were already extensively
tested in their own 2026-08-10 sessions (see the dated entries above) and neither's internal logic
changed here, only the container each one's render function (`renderCasImportCard`/
`renderLiveSettingsCard`) now appends into. Their presence/rendering on the correct tab (Holdings)
was confirmed structurally and via the "Live prices" text/element check above, but a real
password-protected PDF and a real network fetch were not re-run in this session — reasonable given
this was a structural move only, but noted so it isn't assumed to have been re-verified end-to-end.

### Fix (2026-08-11, same day) — reviewer-found mobile tab-bar discoverability gap
`financial-os-reviewer` confirmed the restructure structurally sound (all 17 sections accounted
for, no lost input across any form/tab combination tried, no stuck states) but found one real,
non-blocking gap: at 375px the tab bar overflowed (`scrollWidth` 611px vs `clientWidth` 343px) with
**"Export & Settings" 0% visible** and nothing hinting more tabs existed beyond a mid-word cut on
"Realized Gains & What-If" — a first-time phone user had a real chance of never finding the Net
Worth feed export, which only lives on that tab. Fixed two ways: (1) shortened the label to "Gains
& What-If" (saves ~70px); (2) added a right-edge fade-gradient cue (`.tab-bar-wrap.has-overflow`,
toggled by comparing `scrollWidth`/`clientWidth` in JS, re-checked on window resize) that only
renders when the bar actually overflows — confirmed absent at 1280px where all 4 tabs already fit,
present at 375px in both themes with the correct `--bg` color per theme. Verified via Playwright:
overflow correctly detected (536px vs 343px after the label shortening), the fade renders with the
right gradient stops, and scrolling the bar fully right brings "Export & Settings" completely
within the 375px viewport. The tab-grouping-imbalance observation from the same review (Holdings
pane much taller than Export & Settings) was left as a follow-up per the reviewer's own
recommendation, not fixed here — noted in Known gaps for whoever next touches this file's tab
grouping.

## Updated 2026-08-11 — Value Research-inspired Dashboard additions: Top Gainers & Losers, Diversification flag, sold-lots collapse; Accounts/Settings tab rebalance
Three additive features requested against reference screenshots of Value Research's "My
Investments" portfolio manager, plus a judgment call on a fourth. No existing render function's
math or storage shape changed — all new code, reusing `computeHoldingMetrics`/`toINR`/`formatMoney`
exactly as already established in this file.

**1. Top Gainers & Losers widget (`renderGainersLosersCard`, Dashboard tab).** A card right after
the summary stat tiles, two columns (Gainers / Losers), ranked by unrealized **% return** — not
absolute ₹ gain, which would let one large position crowd out both lists regardless of how well
anything else actually performed (the task text said "by unrealized gain/loss," read here as "the
gain/loss calculation basis," not the sort key — both the ₹ figure and the % are shown per row
either way, so the number itself is never hidden). Same `hasBuyPrice` honesty gate
`computeHoldingMetrics()` already enforces everywhere else in this file: a holding with no Buy Price
(CAS-imported, cost basis unknown) is excluded, never given a fabricated gain — the card states this
plainly and shows an excluded-count note when it applies. A holding priced exactly flat (₹0 gain) is
excluded from **both** lists (it's neither a gainer nor a loser). Gainers only draws from holdings
with `gainAbs>0`, Losers only from `gainAbs<0` — so a "loser" is always a genuine loss, never just
"the least-good performer among gains" (which would be a misleading label). Degrades gracefully at
every edge: 0 holdings → "No holdings yet"; holdings present but none priced → "None of your
holdings have a Buy Price set yet"; fewer than 3 real gainers or losers → shows however many exist,
never padded; a column with zero entries shows "No holdings currently showing a gain" /
"...at a loss" instead of a blank space.

**2. Diversification/concentration flag (`renderConcentrationCard`/`computeConcentration`, Dashboard
tab, placed directly under Asset allocation).** Two independent, threshold-based checks, each with
its reasoning kept in the code comment directly above `computeConcentration()` (not just here):
- **Top-2-holdings share of current INR-convertible value ≥ 50%.** Half the portfolio's value
  resting on two positions means either one's decline meaningfully swings the whole total — 50% was
  picked as a deliberately blunt "literally half" line rather than a more precise-sounding number a
  rule of thumb doesn't actually earn. Only evaluated once there are **at least 3** priced holdings —
  with only 1 or 2 holdings total, "most of the portfolio is in the top 2" is true by construction
  (that's just what the person owns), not a genuine concentration signal, so the check doesn't fire
  and doesn't mislabel a small/starting portfolio as "concentrated."
- **More than 20 direct Stock/Equity positions.** Grounded in the commonly cited practitioner/
  academic finding (Evans & Archer 1968 and its many later replications) that the marginal
  diversification benefit of adding another individual stock is mostly exhausted by roughly 15-20
  names — past that, more positions mainly add tracking burden, which is the literal complaint this
  feature is modeled on (Value Research's own reference copy: "too many stocks directly...hard to
  manage"). 20 is deliberately generous so a 12-15 stock portfolio someone runs on purpose isn't
  flagged.
Only ever shown when actually true for the current data — 0, 1, or both flags can appear
independently; when neither fires, a calm green "No concentration flags right now — your top
holdings and stock count are both in a reasonable range" note is shown instead, never silence and
never a fabricated concern. Every render of this card ends with an explicit, unconditional
disclosure line — "Descriptive only, based on your current holdings — not investment advice, and not
a recommendation to buy, sell, or rebalance anything" — matching this module's existing
not-a-recommendation pattern from the what-if simulator.

**3. The "sold investments hidden by default" toggle — reconsidered, not built as Value Research
built it, per explicit instruction to use judgment.** Checked first, as asked: this module already
structurally separates open and closed positions (a fully-sold holding is removed from
`data.holdings` and becomes a `soldLots` entry in the separate Gains & What-If tab), so there is
genuinely no scenario where a sold position lingers inside the open Holdings table needing to be
hidden — VR's exact toggle doesn't map onto this app's data model. The one real remaining case: the
**sold-lots table itself**, inside Realized Gains, has no pagination/collapse and would grow
unbounded for someone who has recorded many sales over years. Built that instead:
`soldLotsShowAll` (module-level, not persisted) + `SOLD_LOTS_COLLAPSE_THRESHOLD = 10` — once there
are more than 10 sold lots, the table defaults to showing only the 10 most recently recorded, with a
"Show all N" / "Show recent only" toggle button in the card header and a one-line note when
collapsed. Below the threshold, no toggle renders at all (nothing to declutter). Only the rendered
**rows** are limited — `computeRealizedGains()`'s STCG/LTCG/Total stat tiles and
`buildCapitalGainsFeed()`'s JSON/paste-lines export always operate over the full, uncollapsed
`data.soldLots`, so collapsing the table view never hides a real number from the totals or the
ITRGenie feed.

**Bonus (accepted): Holdings/Export & Settings tab rebalance, closing Known gap #8.** Per the
reviewer's own 2026-08-11 recommendation (Holdings was 1246px/7 cards vs. Export & Settings'
237px/1 card), this was a clean, low-risk container move — no render function's internal
markup/logic touched. `renderAccountsCard`, `renderFxCard`, and `renderLiveSettingsCard` (plus their
"Accounts & FX" sub-heading) moved out of the Holdings tab-pane into the renamed **Accounts &
Settings** tab (label changed, `id` changed `export` → `accounts`), which now reads: Accounts & FX
heading → Accounts card → FX card → Live Prices settings → **Cross-module** heading (new, for
clarity) → Net Worth feed card. Holdings is now scoped purely to viewing + entering/importing
holdings data (table, guided form, bulk/CSV, CAS import) — 4 cards, materially lighter.
`openLiveSettings()` (the function every "add Twelve Data key ↗" link in this file calls) now also
sets `activeTab = 'accounts'` before its `render()` call, the same cross-tab-jump pattern
`openSaleForm`/`openWhatIfSale` already established — without this one-line addition, clicking any
of those links from the Holdings tab (their real-world trigger point) would leave the Live Prices
panel built but `display:none`, since it no longer lives on the tab the click originated from.

**Testing.** Real headless Chromium (Playwright), a local static server (not `file://`, to match how
the module actually loads over HTTP on the deployed site), 66 checks, all pass:
- **Gainers/Losers**: a seeded 7-holding portfolio (6 priced with known gains/losses spanning
  ±10%/±15%/±25%/±33%, one deliberately given no Buy Price) — confirmed the correct top-3 gainers
  (including a genuine 25%/25% tie both surfacing, with the clear 3rd-place 15% holding ranked below
  both) and top-3 losers, confirmed the no-Buy-Price holding is excluded from the list (never given a
  fabricated number) and counted in the "N holding(s) excluded" note. Degrade-gracefully checks: an
  empty portfolio, a single profitable holding (Losers column shows a sensible "no holdings at a
  loss" message, not blank/broken), and an all-no-Buy-Price portfolio (correct explanatory message,
  no crash).
- **Concentration flag**: a genuinely concentrated 3-holding portfolio (two large + one small,
  top-2 ≈ 96.6%) correctly triggered the top-2 flag with the right rounded percentage and the actual
  symbol names; a genuinely diversified 5-equal-holding portfolio correctly showed **no** flags and
  the clean "well diversified" note (no false alarm); a 25-equal-value-stock portfolio correctly
  triggered *only* the stock-count flag (not top-2, since holdings are equal-weighted) with the real
  count (25); a 2-holding portfolio correctly did **not** trigger the top-2 flag (confirming the
  `>=3` guard against the "100% in top 2 by construction" false positive).
- **Sold-lots toggle**: 14 seeded sold lots correctly showed only 10 by default with a "Show all 14"
  button; clicking it revealed all 14 and relabeled to "Show recent only"; clicking that again
  correctly re-collapsed to 10. A separate 3-sold-lot seed correctly showed no toggle button at all
  (under the threshold) and all 3 rows directly.
- **Tab rebalance**: confirmed the tab bar shows "Accounts & Settings" (not the old "Export &
  Settings" label anywhere); confirmed the Holdings tab no longer contains the FX card or Live
  Prices settings text; confirmed the Accounts & Settings tab contains Accounts, FX, Live Prices
  settings, *and* the Net Worth feed card; confirmed calling `openLiveSettings()` from the Holdings
  tab correctly jumps `activeTab` to `accounts` and the panel is genuinely visible (not
  `display:none`) afterward.
- **Full regression**: the guided "Add a holding" form still works post-rebalance (added a holding
  with a real ₹50 gain, confirmed it appears in Holdings *and* surfaces correctly in the new
  Gainers/Losers widget on Dashboard); the Holdings-row "Sell" button still correctly cross-tab-jumps
  to Gains & What-If (unaffected by the Accounts-tab-id rename, since it targets a different tab).
- **Mobile (375×812), both themes**: zero horizontal overflow on all four tabs; both new Dashboard
  cards (Gainers/Losers, Diversification check) visible and correctly rendering the concentration
  flag at mobile width, not just desktop.
- **Zero console/page errors** across all 10 seeded scenarios run in this session.
- Full-page screenshots taken (dark/light, desktop/375px, Dashboard and the rebalanced Accounts &
  Settings tab) for visual review — not committed to the repo, matching this module's existing
  pattern.

**Design invariants added** — see the updated tab-structure bullet and two new bullets in "Design
invariants" above (the honesty-gate requirement for the two new Dashboard cards, and the
sold-lots-collapse-is-display-only requirement).

### Fix (2026-08-11, same day) — reviewer-found disclosure gap in the Diversification check
`financial-os-reviewer` independently re-verified all three features by hand (own fixtures, not the
builder's numbers) — confirmed the sold-lots collapse never partializes the STCG/LTCG/Total stat
tiles or the capital-gains export (the axis scrutinized hardest, given the safety stakes of a
silently-partial total), confirmed the Gainers/Losers ranking and no-cost-basis exclusion correct
including the specific "smallest gainer must never appear as a Loser" edge case, and confirmed every
threshold boundary (50% top-2, 20 stocks, 10 sold lots) behaves exactly as documented. One real gap:
`computeConcentration()` silently excluded holdings that couldn't convert to INR (unconverted USD,
no FX rate set) from its top-2 denominator and its `priced.length>=3` gate, but — unlike every other
computation in this file (`renderPerformanceSummary`, `renderRealizedGainsSection`) — gave no
disclosure and said "your portfolio" rather than qualifying the claim. Reviewer's exact repro: two
small INR holdings + one large unconverted USD holding showed a clean "No concentration flags right
now," silently blind to the USD position dominating the real portfolio. Fixed by adding
`unconvertedCount` to `computeConcentration()`'s return (same pattern as the existing
`unconvertedCount` fields elsewhere in this file), disclosing it in the card exactly like the
performance-summary and realized-gains cards already do, and rewording the top-2 flag from "of your
portfolio" to "of your INR-convertible holdings." Also softened an inaccurate in-code comment (the
Evans & Archer 1968 study's own original figure was 8-10 stocks, later revised UP to 15-20+, not
down — so 20 sits at the low end of what's considered adequate, not a generous cushion above it; left
the threshold itself unchanged since it's explicitly a rule of thumb, not a hard line). Verified both
changes directly: the reviewer's exact repro now shows "1 USD holding(s) not included in this check
— set the USD → INR rate further down to fold Vested-US in," and a separately-constructed
top-2-flag-triggering scenario confirms the reworded "INR-convertible holdings" text renders
correctly when the flag actually fires.

## Updated 2026-08-11 — App-wide font-size/contrast/consistency pass (closes out the earlier mobile UX pass's stragglers)
Direct, blunt user feedback: font sizing is hard to see "in places" and the color scheme needs
improvement, across the whole app, not one module — flagged repeatedly this session and deferred
as out-of-scope until now. This is the exhaustive, whole-app fix; this module got the most
individual changes since it has the most UI surface.

The 2026-08-09 UX pass (see "Layout fonts too small to read on mobile" above) established the
13px floor pattern and fixed most of the module, but a full fresh grep sweep of the `<style>`
block (not assuming the earlier pass was complete) found 30 declarations still under 13px — both
in the desktop base rules (which that pass didn't touch, only the `@media (max-width:760px)`
block) and a few mobile overrides that were bumped previously but not all the way to 13px:

- Desktop base, previously untouched: `.brand .sub` 11px→13px, `.panel-header .eyebrow`
  11px→13px, `.field label` 11px→13px, `.btn` 12px→13px, `.btn.small` 11px→13px,
  `table.day-table th` 11px→13px, `table.day-table input[type=number/date]` 12.5px→13px,
  `.cell-muted` 12.5px→13px, `.stat-tile .stat-label` 11px→13px, `.helptext` 12.5px→13px,
  `.breakdown-bar .seg` 10px→13px, `.legend .item` 12px→13px, `.tag` 10px→13px, `.acct-chip`
  12.5px→13px, `.acct-chip .cur` 10px→13px, `.btn.tiny` 10px→13px, `.notice` 12.5px→13px,
  `.match-tag` 10px→13px, `details.collapsible summary .summary-hint` 12px→13px, plus two inline
  styles (an accounts-settings section label, a holding's "manual only" note, a checkbox label).
- Mobile media-query overrides that had been bumped in the 2026-08-09 pass but landed below the
  floor anyway: `.panel-header .eyebrow` 11.5px→13px, `.brand .sub` 12px→13px, `.field label`
  12.5px→13px, `.btn.tiny` 12px→13px, `.stat-tile .stat-label` 11.5px→13px, `.acct-chip .cur`
  11px→13px, `.tag` 11px→13px, `table.day-table td[data-label]::before` 11.5px→13px.

`.tag` (ST/LT gain classification, holding-status badges) and `.breakdown-bar .seg` (the
percentage label inside asset-allocation bar segments) were deliberately raised to the full 13px
floor rather than kept as a smaller "badge exception" — both carry real information (tax
treatment, allocation %), not decoration, and the app-wide instruction was to err toward raising.
Verified visually (Playwright screenshot with a real holding + populated allocation bar in both
themes) that the larger text doesn't overflow the pill/segment shapes; narrow bar segments that
can't fit the label still degrade gracefully via the pre-existing `overflow:hidden` — same
fallback behavior as before, just at a different width threshold.

**Cross-module consistency**: `--bg/--panel/--panel-2/--line/--text/--muted/--gold/--gold-dim/
--green/--rust` hex values (both themes) diffed byte-for-byte against every other module —
already identical, no drift found here. One hardcoded, non-variable color noted but *not*
changed (out of scope — not a `--variable` consistency issue): `.match-tag.isin` uses a one-off
blue (`#7EA8C9`) not part of the gold/rust/green accent system, pre-existing from this module's
CAS-import work. Flagging for whoever next touches the palette, not resolved here.

**Contrast**: `--muted` against `--bg`/`--panel`/`--panel-2` computed at 6.5–7.4:1 dark, 4.9–5.7:1
light — already passes WCAG AA (4.5:1) in both themes, no change needed. Separately noticed (not
in this task's explicit scope, not changed): `--rust` used as *text* color (not just
border/background) for warning/error copy — e.g. live-price-fetch-failed notices, form validation
errors — computes to 3.93:1 against dark `--bg`, below AA's 4.5:1 normal-text threshold (passes
the 3:1 large-text threshold only). This is shared across every module that uses `--rust` for
inline warning text, not portfolio-specific, and fixing it means picking a new accessible-but-
still-"rust" hex for a color also used for borders/icons/tags elsewhere — a real design decision,
not something to guess at here. Flagged for a future session, not silently resolved.

**Tested with real headless-Chromium (Playwright)**: full DOM text-node sweep at 375px and
1280px, both themes, across all 4 tabs (Dashboard/Holdings/Gains & What-If/Accounts & Settings)
with every `<details>` expanded — 0 nodes under 13px anywhere, 0 console errors. Also swept after
populating real data: added a holding via the guided "Add a holding" form (INFY, qty 10, buy
₹1500, current ₹1800) — holding card, gain/loss figures, and the "Add a holding" form itself all
render at ≥13px with the pill/badge shapes intact in both themes at both viewports. Functional
regression: guided "Add a holding" form re-verified end-to-end (feedback message, holding appears
in the list, value/gain computed correctly) — no JS logic touched, CSS/inline-style values only.

## Updated 2026-08-11 — Bulk-paste currency tolerance, plus a "paste one line to fill in" option for the guided Add-a-holding form
Same app-wide audit as `itrgenie/`, `goals/`, `networth/`, `loans/` (see `itrgenie/PROGRESS.md`'s
matching entry for the full rationale). Audited both this module's entry paths per the task's
specific instruction:

**1. Bulk paste/CSV box (`Symbol, Broker, AssetType, Qty, BuyPrice, BuyDate, CurrentPrice,
AsOf`)** — already reasonably good (the module was built with real CAS statements in mind, and
the separate Excel upload already does real fuzzy header-matching, see the 2026-08-10 entry
above), but the plain-text/paste path itself used bare `+qty`/`+buyPrice`/`+currentPrice`
conversions with no currency-symbol tolerance, and `parsePastedRows()` had the same
thousands-comma-splits-into-fake-columns risk already found and fixed in the other modules. Fixed
by reusing `parseNumericCell()` (already defined in this file for the Excel fuzzy importer's own
numeric parsing — one implementation, not a new duplicate) for the plain paste path's Qty/
BuyPrice/CurrentPrice columns, and adding the same `protectThousandsCommas()` shape-detection fix
to `parsePastedRows()`. Column order stays strictly positional here too, same reasoning as the
other modules — 8 columns with no header row to key off of, so reordering would be guessing.

**2. Guided "Add a holding" form** — this is the one the user's complaint most directly
describes: 6+ separate typed fields (Symbol, Broker select, Asset type select, Qty, Buy price,
Buy date) for what's fundamentally one record someone often already has written down in one
place (a trade confirmation, broker SMS/email, or a line copied from a spreadsheet). Added a
"Paste one line to fill in below" input + "Fill fields" button directly above the existing field
grid, reusing the exact same column order as the bulk-paste box (`Symbol, Broker, AssetType, Qty,
BuyPrice, BuyDate, CurrentPrice, AsOf`) so one mental model covers both entry paths. Critically,
this only **fills the existing DOM inputs** — nothing is written to `data.holdings` until the
user reviews/edits the now-pre-filled fields and clicks the pre-existing "Add holding" button,
exactly matching the task's "review before submit" requirement. Broker and Asset type are
`<select>` dropdowns, not free text, so they're matched against the real options (case-insensitive
substring match against account names, and a small `guessAssetTypeFromText()` normalizer for
Stock/ETF/Mutual Fund/Other) — if nothing recognizable is found, the dropdown is left at its
existing value rather than guessed at, and the feedback message says so ("review... complete
Broker/Asset type if not recognized"). Dates reuse `excelDateToISO()` (already defined for Excel
import) rather than adding a third date-parsing implementation to this file.

**Deliberately not extended to "Record a sale"**: that form only has 3 typed fields (Qty, Sell
date, Sell price) plus one dropdown (which open holding) — already low-friction, not the
"five separate fields for one holding" pattern the task specifically flagged. Adding a
paste-to-fill option there would add complexity for a form that isn't actually the source of the
complaint.

**Verified with real headless-Chromium (Playwright), 11 checks**: bulk paste — regression (plain
numbers `INFY, Axis Direct, Equity, 50, 1450, 2022-04-15, 1850, 2026-08-01` still work), tolerant
($ symbol: `VOO, Vested-US, ETF, 10, $380.25, ...`), tolerant (₹ symbol + Indian
thousands-grouping: `RELIANCE, Axis Direct, Equity, 25, ₹12,50,000, 2021-03-01` parses to
`buyPrice: 1250000, qty: 25` — confirmed the comma-grouping doesn't corrupt the column count),
honesty (a row with a non-numeric Qty is skipped, not pushed as `NaN`); quick-fill — Symbol field
filled from a pasted line, Broker select correctly matched "Axis Direct" by name, Asset type
correctly guessed "Stock" from the word "Stock", Qty/Buy price/Buy date fields all filled
correctly (buy price `₹3,500` → field shows `3500`, currency symbol/comma stripped), and —
critically — confirmed `data.holdings` is unchanged immediately after "Fill fields" (nothing
written until the explicit "Add holding" click, which then does add exactly one holding with the
reviewed values). 0 console errors. Full-app smoke pass (both viewports, both this module and the
other 3 touched modules) — 0 console errors. `node --check` confirmed no syntax errors after
every edit.
