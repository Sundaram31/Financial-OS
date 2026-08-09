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

## Known gaps — flagged deliberately, not resolved by guessing
Per explicit instruction not to silently resolve these, and not to fabricate
functionality to paper over them:

1. **Live price feed — built 2026-08-09, Tier 1 unverified in a real browser.**
   See the dated entry directly above for the full picture. Two layered
   options exist now (Yahoo, no setup; Twelve Data, optional key), both
   defensively built, but nobody has confirmed Tier 1 actually works
   against Yahoo's real endpoint outside this build environment — that's
   the one piece of this gap still open, not the integration itself.

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
- Paste-and-parse plus CSV/TXT file upload, not form-fields-only.
- Shared theme key: `itrgenie_theme`.
- Own data storage key: `portfolio_data_v1` — never writes into Net Worth's,
  Goals', or any other module's key. Feeds Net Worth only via explicit
  export, never by writing into its localStorage key directly.
- Live prices are the one deliberate, narrow exception to "nothing leaves
  the browser" — scoped only to public symbol/price lookups (Yahoo Finance,
  and Twelve Data if a key is saved), disclosed plainly in-UI, never
  carrying holdings/personal data. The Twelve Data key lives in its own
  storage key, `portfolio_livekey_v1`, separate from `portfolio_data_v1` so
  it's never included in the Export JSON backup.
