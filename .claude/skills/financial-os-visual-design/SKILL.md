---
name: financial-os-visual-design
description: Required visual identity for every screen in the Financial-OS repo (Sundaram31/Financial-OS), and how to keep new screens from drifting into the generic "obviously AI-generated" look. Use this whenever building a NEW module's UI, redesigning an existing one, or adding any visual element (charts, dashboards, cards, buttons, empty states) to itrgenie/, networth/, goals/, loans/, insurance/, or a new module directory. Trigger this even if the user just says "build" or "add a screen for X" without mentioning design — every module in this repo is a real screen the user looks at, not throwaway output, so it must look professional and deliberately branded, never like a default AI-generated template.
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
