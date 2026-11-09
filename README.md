# BANxOpen.Ui.SheetMetal.Bead (Python)

The NX Block UI dialog that builds bead features, and updates existing ones, to a bead SPEC. It is the Python port of
the C# `BANxOpen.Ui.SheetMetal.Bead` (NX 2412, CPython 3.11).

Every decision is the library's: `BeadTool` in [BANxOpen.SheetMetal](https://github.com/DOcopyANDpaste/py.BANxOpen.SheetMetal) decides:
- which SPECs are offered;
- what blocks Apply, and the warnings;
- the pre-fill from selected beads;
- the selection list and the preferences label;
- how beads are built, named, stamped and given their requirement.

This repo reads the blocks into `BeadControls`, calls one `BeadTool` gesture, and draws the `BeadView` it returns.

## Layout

| File | Role | NX |
|---|---|---|
| `presenter.py` | Blocks → `BeadControls` → one `BeadTool` gesture → render the `BeadView`; owns the checked SPEC row | no |
| `text.py` | The block labels and the SPEC tree's columns (`UiText`) | no |
| `view.py` | Every block ID and block read and write; the SPEC checkbox tree; the list's delete button | yes |
| `dialog.py` | Subclass of the generated dialog: each callback is one delegation | yes |
| `entry.py`, `application/Bead.py` | Wiring, and the three-line file NX runs | yes |
| `bead_generated.py` | The Styler's output. Never edited | yes |

[docs/bead-dialog-blocks.md](docs/bead-dialog-blocks.md) has the block roster and what each block does, the
read-only Sheet Metal Preferences, the requirements written on Apply, and the checkbox tree.

## Changing messages

Everything the dialog says, apart from its block labels and column titles, is `SheetMetalText` (BANxOpen.SheetMetal).
That covers the selection lines, the preferences label, why Apply is blocked, the warnings, the "no SPEC matches"
message and the Apply message. The Material Assignment dialog shares that wording. Message box titles and the
unexpected-error text are `NxDialogText` (BANxOpen.Foundation).

## Running in NX

1. Put the repos' `src` folders on `UGII_PYTHONPATH` and this repo's `application` folder on the dialog search path.
2. Alt+F8, `application\Bead.py`. With `BANXOPEN_DEV=1` the packages are reloaded on every run.

`bead_generated.py` was transcribed from the C# Styler output, not generated. Regenerate it from
`BLOCKUI_BEAD.dlx` with the Styler's Python language, rename it, and overwrite it.

### Smoke checklist

1. Open a sheet metal part with one sheet metal body. The preferences label shows its Sheet Metal Preferences, and the
   SPEC tree lists the rows they allow.
2. Select a chain of curves. The list shows "New bead", and the direction arrow sits on the first curve.
3. Check a SPEC row. R / W / H / P RAD show its values. Show Preview previews the bead, and flipping the direction
   flips it.
4. Apply. The bead is built, named and stamped, and **one** Ctrl+Z takes it back together with its requirement.
5. Select an existing bead. The radio and the checked row follow it, and Apply rebuilds it.
6. Delete a line from the list. Its curves or feature leave the selection.
7. Draw a sketch on the fly in the curve block, then cancel it. The dialog keeps working, and the SPEC tree is not
   empty.
8. Close the dialog with a preview showing. The preview goes. After closing, the syslog has no errors.

## Development

```powershell
uv venv --python 3.11
uv pip install -e ".[dev]"
New-Item -ItemType Junction -Path .\typings -Target "$env:UGII_BASE_DIR\UGOPEN\pythonStubs"

.venv\Scripts\ruff check . ; .venv\Scripts\pyright ; .venv\Scripts\lint-imports ; .venv\Scripts\python -m pytest --cov
```
