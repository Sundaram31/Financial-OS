# Financial OS — Desktop (Python)

## Architecture principle (the reason this exists as a separate layer)

Everything in `core/` is **pure Python with zero UI dependency**. A function
in here doesn't know or care whether it's being called from:
- a `pywebview` desktop window (next step)
- a future FastAPI cloud backend
- a test script (see `tests/`)
- a plain Python REPL, for debugging

This is deliberate. It means "deploy to the cloud later" becomes *wrap these
same functions in an API layer*, not *rewrite the tax logic*. The desktop
app and any future multi-user cloud version share this exact code.

## Structure

```
desktop/
  core/               <- pure Python, no UI, ports the JS module logic 1:1
    models.py         <- dataclasses mirroring the JS `profile` object
    residency.py       <- ported so far (Module 01 equivalent)
  tests/
    test_residency.py  <- verified against REAL scenarios from chat sessions,
                           not synthetic examples
```

## Porting convention

Each `core/*.py` file corresponds to one (or a closely related group of)
ITRGenie JS modules. Port order should generally follow the JS module
`order` field, since later modules often depend on earlier ones (e.g.
Foreign Assets' residency gate needs `residency.py` to exist first).

When porting a module:
1. Read the JS source in `itrgenie/index.html` for that module's logic.
2. Translate faithfully — same field names (snake_case from camelCase),
   same thresholds, same edge-case handling. Note any deliberate JS
   comments about tricky bugs (e.g. the 365-day holding-period boundary)
   and preserve the same care in the Python docstring.
3. Write tests using REAL data from past chat sessions where possible
   (see `test_residency.py`'s `test_real_fy2025_26_voyage_gives_nri` for
   the pattern) — a passing test then means "matches a case we already
   hand-verified," not just "matches what I assume is correct."
4. Update this README's structure diagram and `MASTER_ROADMAP.md`.

## Ported so far

- [x] Residency Calculator (`residency.py`) — Module 01 equivalent
- [ ] Prior Years
- [ ] Salary
- [ ] House Property (incl. the occupancy wizard logic)
- [ ] Capital Gains — Equity/MF
- [ ] Foreign Assets (incl. residency gate)
- [ ] Deductions
- [ ] Regime Comparison
- [ ] ... (23 more)

## Running tests

```
cd desktop
python3 tests/test_residency.py
```

## Next steps (not yet built)
1. Continue porting modules, roughly in JS `order` sequence.
2. SQLite storage layer (replaces JS localStorage).
3. `pywebview` wrapper — renders the existing HTML/JS frontend in a native
   window, with a Python bridge for OCR/file-system/encrypted-file access
   that JS alone can't do.
4. PyInstaller packaging for distributable `.exe` (Windows) / `.app` (Mac).
