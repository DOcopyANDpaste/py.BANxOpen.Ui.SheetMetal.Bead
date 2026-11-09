"""Mode: interactive. Reads the blocks into `BeadControls`, calls one `BeadTool` gesture and renders the `BeadView`
it returns. Every decision (which SPECs are offered, what blocks Apply, the pre-fill, the wording) is the library's;
the presenter owns only the control values, among them the row checked in the SPEC tree."""

from __future__ import annotations

import logging
from collections.abc import Callable, Sequence
from typing import Any, Protocol

from banxopen.foundation import OperationResult
from banxopen.foundation.ui import CHECKED, UNCHECKED, Messenger, TreeRow
from banxopen.sheetmetal import BeadControls, BeadSpecRow, BeadView, SpecPreview, format_thickness
from banxopen.ui_bead.text import UiText

_log = logging.getLogger(__name__)

Column = tuple[int, str, int]
Direction = tuple[tuple[float, float, float], tuple[float, float, float]]


class BlockContents(Protocol):
    @property
    def bead_features(self) -> Sequence[Any]: ...
    @property
    def curve_sections(self) -> Sequence[Any]: ...


class Tool(Protocol):
    """What the dialog uses of `banxopen.sheetmetal.nx.BeadTool`. Selection objects are opaque here."""

    def open(self, controls: BeadControls) -> BeadView: ...
    def selection_changed(
        self, curve_block_objects: Sequence[Any], feature_block_objects: Sequence[Any], controls: BeadControls
    ) -> BeadView: ...
    def controls_changed(self, controls: BeadControls, *, bead_spec_changed: bool = False) -> BeadView: ...
    def delete_lines(self, indices: Sequence[int]) -> BlockContents: ...
    def apply(self, controls: BeadControls) -> OperationResult[str]: ...
    def close(self) -> None: ...


class View(Protocol):
    """What the presenter needs of the dialog's blocks. `BeadDialogView` is the NX one."""

    def mark_shown(self) -> None: ...
    def bead_spec_names(self) -> tuple[str, ...]: ...
    def bead_spec(self) -> str | None: ...
    def set_bead_spec(self, name: str) -> None: ...
    def flipped(self) -> bool: ...
    def preview_on(self) -> bool: ...
    def curve_objects(self) -> list[Any]: ...
    def feature_objects(self) -> list[Any]: ...
    def set_block_contents(self, features: Sequence[Any], sections: Sequence[Any]) -> None: ...
    def clear_selection(self) -> None: ...
    def show_specs(self, columns: Sequence[Column], rows: Sequence[TreeRow[BeadSpecRow]]) -> None: ...
    def check_spec(self, picked: BeadSpecRow | None) -> None: ...
    def set_selection_lines(self, lines: Sequence[str]) -> None: ...
    def set_preference_summary(self, text: str) -> None: ...
    def set_spec_preview(self, preview: SpecPreview | None) -> None: ...
    def set_direction(self, direction: Direction | None) -> None: ...


def same_spec(a: BeadSpecRow | None, b: BeadSpecRow | None) -> bool:
    """By workbook and SPEC id: two of a Standard's bead SPEC workbooks could carry the same SPEC id."""
    return (
        a is not None
        and b is not None
        and a.spec_id.casefold() == b.spec_id.casefold()
        and a.workbook_name.casefold() == b.workbook_name.casefold()
    )


def spec_columns(text: UiText) -> tuple[Column, ...]:
    """Column 0 carries the checkbox and the SPEC id together: NX draws a node's state icon at its label."""
    return (
        (0, text.column_spec, 140),
        (1, text.column_radius, 60),
        (2, text.column_width, 60),
        (3, text.column_height, 60),
        (4, text.column_die_radius, 60),
        (5, text.column_thickness, 60),
    )


def spec_rows(view: BeadView) -> tuple[TreeRow[BeadSpecRow], ...]:
    """The SPEC rows, the picked one checked, the ones kept only for a selected bead in the warning colour."""
    picked = view.controls.picked_spec
    return tuple(
        TreeRow(
            spec.spec_id,
            spec,
            {
                1: format_thickness(spec.radius_and_rad_s),
                2: format_thickness(spec.width),
                3: format_thickness(spec.height),
                4: format_thickness(spec.die_radius_p),
                5: format_thickness(spec.thickness),
            },
            state=CHECKED if same_spec(spec, picked) else UNCHECKED,
            warning=spec in view.kept_for_beads,
        )
        for spec in view.spec_rows
    )


class BeadPresenter:
    def __init__(self, tool: Tool, view: View, messenger: Messenger, text: UiText | None = None) -> None:
        self._tool = tool
        self._view = view
        self._messenger = messenger
        self._text = text or UiText.DEFAULT
        self._picked: BeadSpecRow | None = None
        self._shown = False
        self._last: BeadView | None = None
        self._tree: tuple[tuple[BeadSpecRow, ...], frozenset[BeadSpecRow]] | None = None
        self._info: str | None = None

    # ---- Dialog callbacks ----

    def on_initialize(self) -> None:
        """Reads the part. The SPEC tree waits for `on_shown`: NX refuses tree columns until the dialog is shown, and so
        does the message the view may carry."""
        self._guard("initialize", lambda: self._render(self._tool.open(self._controls()), notify=False))
        self._info = self._last.info if self._last is not None else None

    def on_shown(self) -> None:
        self._view.mark_shown()
        self._shown = True
        self._tree = None  # a Reset rebuilds the dialog, and the tree comes back empty
        self._guard("dialog shown", self._selection_changed)
        info, self._info = self._info, None
        if info:
            self._messenger.show_result(OperationResult.success(), info)

    def on_selection_changed(self) -> None:
        """Either selection block, including a sketch drawn on the fly in the curve block finishing or cancelling."""
        self._guard("selection", self._selection_changed)

    def on_clear(self) -> None:
        def clear() -> None:
            self._view.clear_selection()
            self._selection_changed()

        self._guard("Clear Selection", clear)

    def on_bead_spec_changed(self) -> None:
        self._guard(
            "bead SPEC",
            lambda: self._render(self._tool.controls_changed(self._controls(), bead_spec_changed=True)),
        )

    def on_controls_changed(self) -> None:
        """The direction or Show Preview."""
        self._guard("direction / preview", lambda: self._render(self._tool.controls_changed(self._controls())))

    def on_spec_checked(self, row: BeadSpecRow | None) -> None:
        """Radio-like: exactly one row is checked once any is, so clicking the checked row again is not a deselect. A
        click that resolves to no row leaves the pick alone."""

        def check() -> None:
            if row is not None:
                self._picked = row
            self._view.check_spec(self._picked)
            if row is not None:
                self._render(self._tool.controls_changed(self._controls()))

        self._guard("SPEC tree check", check)

    def on_lines_deleted(self, indices: Sequence[int]) -> None:
        """The selection list's delete button: the lines' beads leave both selection blocks."""

        def delete() -> None:
            if not indices:
                return
            contents = self._tool.delete_lines(indices)
            self._view.set_block_contents(contents.bead_features, contents.curve_sections)
            self._selection_changed()

        self._guard("delete from selection", delete)

    def on_apply(self) -> int:
        """Nonzero keeps the dialog open. OK runs this too."""
        result = self._tool.apply(self._controls())
        self._messenger.show_result(result, result.value)
        if not result.ok:
            return 1
        self._selection_changed()  # the part was read again
        return 0

    def on_close(self) -> None:
        """However the dialog closed: takes the preview down."""
        self._tool.close()

    # ---- Helpers ----

    def _controls(self) -> BeadControls:
        view = self._view
        return BeadControls(
            bead_spec_names=view.bead_spec_names(),
            bead_spec=view.bead_spec(),
            picked_spec=self._picked,
            flipped=view.flipped(),
            preview_on=view.preview_on(),
        )

    def _selection_changed(self) -> None:
        view = self._view
        self._render(self._tool.selection_changed(view.curve_objects(), view.feature_objects(), self._controls()))

    def _render(self, bead_view: BeadView, *, notify: bool = True) -> None:
        view, controls = self._view, bead_view.controls
        self._last = bead_view
        # The library may have pre-filled the bead SPEC and the row from the selected beads.
        if controls.bead_spec is not None and controls.bead_spec != view.bead_spec():
            view.set_bead_spec(controls.bead_spec)
        self._picked = controls.picked_spec
        if self._shown:
            tree = (bead_view.spec_rows, bead_view.kept_for_beads)
            if tree != self._tree:
                view.show_specs(spec_columns(self._text), spec_rows(bead_view))
                self._tree = tree
            else:
                view.check_spec(self._picked)
        view.set_selection_lines(bead_view.selection_lines)
        view.set_preference_summary(bead_view.preference_summary)
        view.set_spec_preview(bead_view.spec_preview)
        view.set_direction(bead_view.direction)
        if notify and bead_view.info:
            self._messenger.show_result(OperationResult.success(), bead_view.info)

    def _guard(self, what: str, action: Callable[[], None]) -> None:
        """An error is logged in full and the dialog redrawn from the last view: one failure half-way through a refresh
        must not leave the SPEC tree empty or out of step with what Apply would build."""
        try:
            action()
        except Exception:  # noqa: BLE001  (boundary: an NX callback; the dialog recovers instead of going dead)
            _log.exception("[%s] failed; the dialog is being redrawn from its last state. Please report this.", what)
            self._recover()

    def _recover(self) -> None:
        if self._last is None:
            return
        try:
            self._tree = None
            self._render(self._last, notify=False)
        except Exception:  # noqa: BLE001
            _log.exception("Redrawing the dialog after an error failed too.")
