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

## Known gaps — flagged deliberately, not resolved by guessing
Per explicit instruction not to silently resolve these, and not to fabricate
functionality to paper over them:

1. **No live price data.** Yahoo/NSE/Google Finance are CORS-blocked from a
   browser with zero backend. The Goals module's earlier research (see
   `MASTER_ROADMAP.md` status log, 2026-08-03) concluded a dedicated API
   (Twelve Data-style, needs a paid API key) is the only viable client-side
   option, and that conclusion still holds — nothing changed it this
   session. This module does **not** wire up any price feed or guess at an
   integration. Current Price is always user-entered (typed directly in the
   holdings table, or via re-paste/re-import), same pattern as every other
   module's manual-entry design. Picking and paying for a data provider is a
   real decision left to the user, not something to fake.

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
