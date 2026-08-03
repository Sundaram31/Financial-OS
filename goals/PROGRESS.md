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

## Design invariants (same as ITRGenie/Net Worth)
- Zero external dependencies, works offline once loaded.
- Paste-and-file-upload dual input mode (CSV/TXT via FileReader, same parser
  as paste — not a separate code path).
- Shared theme key: `itrgenie_theme`.
