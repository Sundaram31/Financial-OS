---
name: financial-os-visual-design
description: Required visual identity AND usability/ease-of-operation bar for every screen in the Financial-OS repo (Sundaram31/Financial-OS) — how to keep new screens from drifting into the generic "obviously AI-generated" look, AND how to keep them genuinely easy to use on a phone (readable type, low-friction data entry, numbers before paragraphs). Use this whenever building a NEW module's UI, redesigning an existing one, or adding any visual element (charts, dashboards, cards, buttons, empty states, forms) to itrgenie/, networth/, goals/, loans/, insurance/, or a new module directory. Trigger this even if the user just says "build" or "add a screen for X" without mentioning design or usability — every module in this repo is a real screen a real person operates on their phone, not throwaway output, so it must look professional, be genuinely easy to operate, and never read as a default AI-generated template.
---

# Financial-OS visual identity

Every live module in this repo already shares one deliberate visual system —
it was designed once (in ITRGenie) and every module since has extended it
rather than invented its own. That's the whole point: a user moving between
Net Worth, Goals, Loans, and Insurance should feel like they're in one
product, a private financial ledger, not five separate AI-generated demos
stapled together. Your job on any visual work here is to **extend this
system faithfully**, and where you need something genuinely new, design it
*within* the system rather than reaching for whatever a generic prompt would
produce.

## The existing system (pull these, don't reinvent them)

Copy the `:root` / `body[data-theme="light"]` CSS variable block from an
existing module (e.g. `itrgenie/index.html` or `networth/index.html`) rather
than retyping values from memory — but for reference, the tokens are:

- **Dark theme** (default): `--bg:#0B0E11; --panel:#12161B; --panel-2:#171C22;
  --line:#242A31; --text:#E8E6E0; --muted:#9BA0A8; --gold:#C9A227;
  --gold-dim:#8f7419; --green:#4A9B6E; --rust:#B5533C;`
- **Light theme** (`body[data-theme="light"]`): `--bg:#F7F5F0;
  --panel:#FFFFFF; --panel-2:#F1EEE7; --line:#DCD7CC; --text:#242220;
  --muted:#6B6660; --gold:#96741A; --gold-dim:#7a5f15; --green:#2F7A50;
  --rust:#9B3F2A;`
- **Type**: `--mono: 'IBM Plex Mono', 'Courier New', monospace` for body/data
  (this is a numbers-heavy financial app — mono keeps figures aligned and
  legible), `--serif: 'Source Serif 4', Georgia, serif` for headings, brand
  mark, and emphasis. No third typeface family.
- **Motif**: a small circular "seal" mark next to the brand name (gold
  border, serif initial/glyph), 1px hairline borders (`--line`), small
  `border-radius` (4px) rather than large rounded cards, uppercase
  letter-spaced "eyebrow" labels above section headers.
- **Theme toggle**: reads/writes the shared `itrgenie_theme` localStorage
  key so the choice is consistent across every module — never give a new
  module its own separate theme key or a hardcoded single theme.

This ledger/seal aesthetic (gold accent, serif+mono pairing, hairline
borders, restrained near-black/warm-cream backgrounds) *is* this project's
answer to "what should this look like" — already decided, already applied
five times. Don't re-litigate it per module.

## Where new screens actually go wrong

The risk isn't the base palette (that's settled) — it's what happens when
you add something the existing modules haven't needed yet: a chart, a
dashboard summary row, a data table, an empty state, a new kind of button.
Left unguided, it's easy to unconsciously reach for whichever generic
pattern a UI framework or an unbriefed AI would default to, which clashes
immediately with the hand-built ledger look sitting right next to it.
Concretely, avoid:

- **Default chart-library styling** — a bar chart in framework-default blue
  (`#3B82F6`-ish), drop-shadowed tooltips, pill-shaped legends. Charts must
  pull from `--gold`, `--rust`, `--green` (and muted variants) the same way
  every other accent in the app does, styled as hairline/flat like the rest
  of the UI, not a bundled chart library's out-of-the-box look.
- **Generic SaaS chrome** — soft drop-shadow card stacks, large fully-rounded
  buttons, gradient CTAs, an unbriefed sans-serif (Inter, system-ui, etc.)
  creeping into headings instead of the serif. If a component looks like it
  came from a generic component library, it will read as bolted-on.
- **Decoration without meaning** — numbered `01 / 02 / 03` badges, icon
  soup, or motion for its own sake. This project's existing structural
  devices (eyebrows, hairlines, the seal mark) already carry the identity;
  don't layer a second, unrelated decorative system on top. Keep any motion
  restrained — a hover state or a subtle reveal, not scroll-triggered
  choreography; excess animation is itself one of the tells of an
  unreviewed AI-generated screen.
- **Generic copy** — "Unlock insights", "Get started today", marketing
  filler. Match the existing modules' plain, functional voice (labels name
  what the user controls, empty states say what to do next, nothing sells).

## Ease of use, not just looks

A screen can match every token above perfectly and still be genuinely hard
to use — that happened for real: Portfolio Tracker's first build (2026-08-09)
matched the visual system correctly but drew direct user complaints on a
phone: text too small to read, the only way to add a holding was typing an
8-field comma-separated line, and the real numbers (holdings, gain/loss)
were buried below several paragraphs of explanation. It took a second pass
to fix. Treat these as load-bearing requirements, not polish, on every
screen from the start:

- **Mobile type must actually be readable.** Nothing in normal reading flow
  (table cells, labels, helper text) should render below ~13-14px on a
  narrow viewport. Add a real `@media (max-width: 760px)` type-size bump if
  the base sizing is denser than that on desktop — don't just shrink padding
  and assume the text is fine. If a data table won't fit a phone width
  without horizontal scrolling, prefer a stacked label/value card layout
  under that breakpoint (see `portfolio/index.html`'s holdings table for the
  pattern) over forcing a cramped scrollable table.
- **Give every data-entry screen a guided, low-friction path.** This
  project's convention is paste-and-parse *and* file upload, not
  form-fields-only (see `financial-os-conventions`) — that rule exists to
  ban forms-only tedium, it was never meant to make bulk-paste the *only*
  option either. For anything a user adds one item at a time (a holding, a
  policy, a goal), pair the bulk paste/CSV path with a simple labeled form
  (proper `<input>`/`<select>` fields, not "remember the comma order") as
  the primary, default-visible way in. Typing a precise multi-field
  comma-separated line on a phone keyboard is real friction — don't make it
  someone's only option.
- **Lead with the numbers, not the explanation.** A user opens a financial
  screen to see a total, a holding, a gain/loss — not to read about how the
  screen works. Put the actual data (summary stats, the primary table)
  immediately after the header. Move explanatory paragraphs, settings, and
  edge-case documentation (known gaps, how a feature works internally)
  behind a collapsed `<details>` or a short one-line hint — detail should be
  one tap away, not something to scroll past to reach the content.
- **Verify this the same way you'd verify anything else here** — real
  headless-browser checks at a real mobile viewport (375×812 is a reasonable
  stand-in for "a phone"), not eyeballing a desktop screenshot and assuming
  it scales down fine.

## Process for any new UI work

1. Open one sibling module (whichever is closest in kind — a dashboard-like
   addition should look at Net Worth, a form-heavy addition at Goals or
   Insurance) and reuse its CSS variables, theme-toggle script, and
   component patterns (`.card`, `.panel-header`, `.btn`, `.field`) directly.
   Don't design a palette from scratch.
2. For anything genuinely new (a chart type, a new kind of summary view),
   sketch it using only the existing tokens, then sanity-check it against
   the "where new screens go wrong" list above before writing final code.
3. If you want deeper craft guidance on typography pairing, motion
   restraint, or writing — beyond just which tokens to use — consult the
   `frontend-design` skill. Use it for *technique*, not for re-deciding the
   palette: this project's brief has already answered the color/type
   question, and per that skill's own rule, an explicit brief always wins
   over its generic defaults.
4. Building a chart or data visualization specifically? The `dataviz`
   skill's form/interaction guidance still applies — just map its palette
   role slots onto `--gold` / `--rust` / `--green` instead of a fresh
   palette, so charts read as part of this app, not an inserted widget.
5. Before calling the work done, check both themes (`data-theme="light"`
   and the dark default) — every module supports both, so a new screen that
   only looks right in one theme isn't finished.
