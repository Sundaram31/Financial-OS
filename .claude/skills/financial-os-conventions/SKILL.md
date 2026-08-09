---
name: financial-os-conventions
description: House rules for working in the Financial-OS repo (Sundaram31/Financial-OS) — a personal finance web app built module by module (ITRGenie, Net Worth, Goals, Loans, Insurance, and more to come). Use this at the START of any session that touches this repo, before reading code or making changes, to know what's already decided and where things stand. Also use it whenever adding a feature, fixing a bug, building a new module, or otherwise editing anything under itrgenie/, networth/, goals/, loans/, insurance/, or desktop/ — it defines the zero-dependency/offline/local-storage design invariants every module must follow, the shared cross-module data contracts, and the exact files that must be updated before a session touching a module ends (module PROGRESS.md, INDEX.md's status table, and MASTER_ROADMAP.md's status log for roadmap-level changes). Trigger this even if the user doesn't mention the skill by name — any request to build, change, debug, or extend something in this repo implies it.
---

# Financial-OS project conventions

This repo has no single maintainer session — it's worked on across many
separate chats and Claude Code sessions over time, sometimes months apart.
Nothing survives between sessions except what's written into the repo
itself. That's the reason every rule below exists: they're what makes a
brand-new session, with zero memory of past conversations, pick up exactly
where the last one left off instead of re-deciding things or drifting from
the existing design.

## 1. Read before you write

Before making any change, read in this order:

1. `INDEX.md` — the module status table. Tells you what exists, what's
   live, what's a gap, and when each module was last touched.
2. The `PROGRESS.md` of whichever module(s) you're about to touch (e.g.
   `networth/PROGRESS.md`). This holds the module's actual build history,
   known gaps, and design invariants — often with more nuance than the
   one-line status in INDEX.md.
3. `MASTER_ROADMAP.md` if the task is roadmap-level (new module, phase
   sequencing, cross-module data flow) rather than a fix inside one module.
   Its status log at the bottom is the closest thing this project has to a
   session-by-session diary — read recent entries for context before
   assuming something is undecided.

If a decision, number, or design choice isn't written down in one of these
three files, treat it as **not decided** — don't infer it from a past chat
you can't actually see, and don't guess. Several entries in
`MASTER_ROADMAP.md`'s status log are corrections/retractions of exactly
this failure mode (a figure or classification stated confidently, then
retracted because it couldn't be verified against a real document). Prefer
"flagged as unconfirmed" over a wrong confident answer.

## 2. Design invariants every module follows

Unless a module's own `PROGRESS.md` documents a deliberate, explained
exception, every module in this repo (existing or new) follows these —
they're what makes the app one coherent system instead of five unrelated
tools that happen to share a repo:

- **Zero external dependencies, fully offline after load.** No CDN
  scripts, no runtime network calls. When a library is genuinely needed
  (e.g. SheetJS/PDF.js for ITRGenie's file parsing), self-host it in the
  module's own `lib/` folder rather than pulling from a CDN.
- **Nothing the user enters ever leaves the browser.** This is the app's
  stated privacy promise (see `README.md`). A new feature that silently
  adds a network call or third-party service breaks that promise — don't.
- **Paste-and-parse *and* file upload**, not form-fields-only, for data
  entry. Users are pasting bank/broker statement text or uploading
  CSV/TXT/Excel exports; match the existing parser pattern rather than
  inventing a form-only flow.
- **Shared theme, separate data.** Every module reads/writes the same
  `itrgenie_theme` localStorage key so the light/dark toggle is consistent
  site-wide — but each module owns its *own* data storage key (e.g.
  `networth_data_v1`). Never fold one module's data into another's key.
- **Conform to existing cross-module data contracts** rather than
  inventing a parallel shape. Check `MASTER_ROADMAP.md`'s "Cross-module
  data contracts" section first — e.g. net worth inputs are
  `{category, label, value, asOf}[]`, capital gains rows are
  `{symbol, buydate, selldate, buyprice, sellprice, qty, assetType}[]`. A
  new module that produces or consumes this kind of data should slot into
  the existing shape so the eventual synthesis layer (see roadmap) can
  actually join data across modules.
- **Root-cause fixes over patches, real documents over guesses.** When you
  find a bug or gap, prefer fixing the underlying misclassification or
  missing logic (see: the House Property occupancy wizard, the Foreign
  Assets residency gate in `MASTER_ROADMAP.md`) over a surface patch. When
  something is ambiguous — which file is current, what a number should be
  — get the real document or ask, rather than guessing and stating it as
  fact.

## 3. Before a session that touched a module ends

This is a hard rule from `INDEX.md` ("Rule going forward") — treat it as
part of finishing the task, not an optional extra step:

1. Update that module's `PROGRESS.md` — follow the existing per-module
   style (see `networth/PROGRESS.md` for the pattern: "What this is",
   dated "Built"/"Updated" sections, "Known gap", "Design invariants").
   Add a new dated entry rather than rewriting history.
2. Update `INDEX.md`'s module status table — bump the "Last touched" date
   for that module (and the status text if it changed).
3. Update `MASTER_ROADMAP.md`'s status log — **only** if the change is
   roadmap-level: a new module, a phase/priority shift, a new or changed
   cross-module data contract, or a decision future sessions need to know
   about. A small in-module fix doesn't need a roadmap entry — that's what
   the module's own `PROGRESS.md` is for.

These land as normal git commits (this repo lives on GitHub specifically
so updates don't require manual upload/delete cycles) — no separate
publishing step.
