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

## Design invariants (same as every other module)
- Zero external dependencies, works offline once loaded.
- Paste-and-parse plus CSV/TXT file upload (bulk add/advanced, collapsed by
  default), not form-fields-only — a guided single-holding form (added
  2026-08-09) is the primary entry path, but paste/upload remains a fully
  supported, non-removed alternative, per this repo's convention.
- Shared theme key: `itrgenie_theme`.
- Own data storage key: `portfolio_data_v1` — never writes into Net Worth's,
  Goals', or any other module's key. Feeds Net Worth only via explicit
  export, never by writing into its localStorage key directly.
- Live prices are the one deliberate, narrow exception to "nothing leaves
  the browser" — scoped only to public symbol/price lookups (Yahoo Finance,
  Stooq, and Twelve Data if a key is saved), disclosed plainly in-UI, never
  carrying holdings/personal data. The Twelve Data key lives in its own
  storage key, `portfolio_livekey_v1`, separate from `portfolio_data_v1` so
  it's never included in the Export JSON backup.
- Mobile viewport (down to 375px) gets its own font-size and table-layout
  rules under `@media (max-width:760px)` — desktop sizing stays denser by
  design; don't remove the mobile block thinking it's redundant with base
  styles.
