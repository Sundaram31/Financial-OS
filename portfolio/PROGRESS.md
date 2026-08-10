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

## Deliberately NOT done yet
- No capital-gains export (`{symbol, buydate, selldate, buyprice, sellprice,
  qty, assetType}[]` contract, Portfolio → ITRGenie) — that's for *sold*
  positions, and this module only tracks current holdings. Roadmap item 4
  (what-if fund-switch tax modeling) is the natural place to build a sell
  workflow that would produce this; not attempted here to avoid guessing at
  a shape that isn't needed by anything yet.
- No long-term/short-term holding-period classification or any tax
  characterization of gains — that's ITRGenie's domain (capital gains
  logic), deliberately kept separate per the roadmap's synthesis-layer
  framing ("Portfolio + ITRGenie's capital gains logic" is future work).
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
