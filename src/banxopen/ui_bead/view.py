"""Every block ID of BLOCKUI_BEAD.dlx and every block read and write. When the Styler renames a block, only this file
changes. Implements the presenter's `View`, and turns the SPEC tree's checkbox and the selection list's delete button
(whose events do not reach update_cb) into presenter calls."""

# NX 2412's Python stubs declare instance methods without `self`, type enum members as int and give collections
# no __iter__; these rules would only report those stub defects here. Everything else is still checked.
# pyright: reportAttributeAccessIssue=false, reportArgumentType=false, reportReturnType=false
# pyright: reportCallIssue=false, reportGeneralTypeIssues=false, reportOptionalMemberAccess=false

from __future__ import annotations

import logging
from collections.abc import Callable, Sequence
from typing import Any

import NXOpen
import NXOpen.BlockStyler

from banxopen.foundation.nx import NxDialogText
from banxopen.foundation.ui import CHECKED, UNCHECKED, NxMessenger, TreeBinding, TreeRow, TreeUnavailableError
from banxopen.sheetmetal import BeadSpecRow, SpecPreview
from banxopen.ui_bead.presenter import BeadPresenter, Column, Direction, same_spec
from banxopen.ui_bead.text import UiText

_log = logging.getLogger(__name__)

# ---- Block IDs, verbatim from BLOCKUI_BEAD.dlx (see docs/bead-dialog-blocks.md) ----
CURVES = "super_section0"
BEAD_FEATURES = "selection0"
CLEAR_BUTTON = "btn_ClearAll"
SELECTION_LIST = "list_SelectedObjects"
PREFERENCE_LABEL = "label_currentPref"
BEAD_SPEC_ENUM = "enum_BABead"
SPEC_TREE = "BeadOptions"
RADIUS = "double_R"
WIDTH = "double_W"
HEIGHT = "double_H"
DIE_RADIUS = "double_PRAD"
DIRECTION = "direction0"
PREVIEW_TOGGLE = "togglePreview"


class BeadDialogView:
    def __init__(self, dialog: NXOpen.BlockStyler.BlockDialog, text: UiText) -> None:
        """Construct from initialize_cb, which is where the blocks exist. A Reset re-runs initialize_cb, so this is
        built again then, with the tree not ready until the dialog is shown."""
        self._top = dialog.TopBlock
        self._text = text
        self._shown = False
        self._curves = self._find(CURVES)
        self._features = self._find(BEAD_FEATURES)
        self._list = self._find(SELECTION_LIST)
        self._preference_label = self._find(PREFERENCE_LABEL)
        self._bead_spec = self._find(BEAD_SPEC_ENUM)
        self._tree = self._find(SPEC_TREE)
        self._doubles = [self._find(i) for i in (RADIUS, WIDTH, HEIGHT, DIE_RADIUS)]
        self._direction = self._find(DIRECTION)
        self._preview = self._find(PREVIEW_TOGGLE)
        self._specs: TreeBinding[BeadSpecRow] | None = TreeBinding(self._tree) if self._tree is not None else None
        self._last_specs: tuple[Sequence[Column], Sequence[TreeRow[BeadSpecRow]]] | None = None

    @staticmethod
    def update_of(block: NXOpen.BlockStyler.UIBlock) -> str | None:
        """The block an update_cb is about, by ID."""
        return block.Name

    def connect(self, presenter: BeadPresenter) -> None:
        """Block setup the .dlx cannot carry, set here so a regeneration cannot lose it, and the handlers registered on
        the blocks themselves. Each setting on its own: one NX refuses must not skip the rest, above all the filter."""
        features, curves, selection_list = self._features, self._curves, self._list
        text = self._text
        if features is not None:
            # Many-select, solid features only: a bead is one, and this keeps sketch, curve and datum features out
            # before the pick. NX has no Bead-only filter, so the library leaves out other solid features.
            _try("selection0 select mode", lambda: setattr(features, "SelectModeAsString", "Multiple"))
            _try("selection0 label", lambda: setattr(features, "LabelString", text.select_bead_feature))
            _try("selection0 tooltip", lambda: setattr(features, "ToolTip", text.select_bead_feature_tip))

            def solid_features_only() -> None:
                features.ClearFilter()
                features.AddFilterMember(NXOpen.Select.FilterMember.SolidFeature)

            _try("selection0 filter", solid_features_only)
        if curves is not None:
            _try("super_section0 label", lambda: setattr(curves, "LabelString", text.select_curves))
            _try("super_section0 tooltip", lambda: setattr(curves, "ToolTip", text.select_curves_tip))
        if selection_list is not None:
            _try("list_SelectedObjects delete button", lambda: setattr(selection_list, "ShowDeleteButton", True))

            def on_delete(list_box: Any) -> int:
                presenter.on_lines_deleted(list(list_box.GetSelectedItems()))
                return 0

            _try("list_SelectedObjects delete handler", lambda: selection_list.SetDeleteHandler(_guarded(on_delete, 0)))
        specs = self._specs
        if specs is not None and self._tree is not None:
            # Tree events do not route through update_cb. The handler fires on a click of the state icon, not on
            # SetState.
            self._tree.SetOnStateChangeHandler(
                _guarded(lambda _tree, node, _state: presenter.on_spec_checked(specs.resolve(node)), None)
            )

    def mark_shown(self) -> None:
        """From here on the tree accepts columns and rows."""
        self._shown = True

    # ---- Bead SPEC radio: its members are the .dlx's, so a third SPEC is a Styler edit and a workbook ----

    def bead_spec_names(self) -> tuple[str, ...]:
        return tuple(self._bead_spec.GetEnumMembers()) if self._bead_spec is not None else ()

    def bead_spec(self) -> str | None:
        return self._bead_spec.ValueAsString if self._bead_spec is not None else None

    def set_bead_spec(self, name: str) -> None:
        if self._bead_spec is not None:
            self._bead_spec.ValueAsString = name

    def flipped(self) -> bool:
        """False when the block is missing: beads are then built to the section's normal side."""
        return bool(self._direction.Flip) if self._direction is not None else False

    def preview_on(self) -> bool:
        return bool(self._preview.Value) if self._preview is not None else False

    # ---- Selection blocks ----

    def curve_objects(self) -> list[Any]:
        return list(self._curves.GetSelectedObjects()) if self._curves is not None else []

    def feature_objects(self) -> list[Any]:
        return list(self._features.GetSelectedObjects()) if self._features is not None else []

    def set_block_contents(self, features: Sequence[Any], sections: Sequence[Any]) -> None:
        """Features first: should the curve block refuse its Sections, the feature block is still up to date. The curve
        block takes Sections, not curves ("Invalid object type")."""
        if self._features is not None:
            self._features.SetSelectedObjects(list(features))
        if self._curves is not None:
            self._curves.SetSelectedObjects(list(sections))

    def clear_selection(self) -> None:
        self.set_block_contents((), ())

    def set_selection_lines(self, lines: Sequence[str]) -> None:
        if self._list is not None:
            self._list.SetListItems(list(lines))

    # ---- SPEC tree ----

    def show_specs(self, columns: Sequence[Column], rows: Sequence[TreeRow[BeadSpecRow]]) -> None:
        self._last_specs = (columns, rows)
        if not self._shown or self._tree is None or self._specs is None:
            return
        # Asked of the tree, not remembered: a Reset brings the same tree back with no columns.
        if self._tree.NumberOfColumns == 0:
            for column_id, title, width in columns:
                self._tree.InsertColumn(column_id, title, width)
                self._tree.SetColumnResizePolicy(column_id, NXOpen.BlockStyler.Tree.ColumnResizePolicy.ConstantWidth)
        try:
            self._specs.show(rows, expand_roots=False)
        except TreeUnavailableError as ex:
            _log.warning("The bead SPEC tree could not be rebuilt: %s", ex)

    def check_spec(self, picked: BeadSpecRow | None) -> None:
        """Exactly one row checked, the rest not. A tree whose nodes went with a cancelled sketch's rollback is shown
        again instead of written through."""
        specs = self._specs
        if specs is None:
            return
        if specs.is_stale():
            _log.warning("The bead SPEC tree no longer held its rows (e.g. after a cancelled sketch); rebuilding it.")
            if self._last_specs is not None:
                self.show_specs(*self._last_specs)
            return
        specs.set_states(lambda row: CHECKED if same_spec(row, picked) else UNCHECKED)

    # ---- Read-only values ----

    def set_preference_summary(self, text: str) -> None:
        if self._preference_label is not None:
            self._preference_label.Label = text

    def set_spec_preview(self, preview: SpecPreview | None) -> None:
        """The .dlx ships these insensitive; ReadOnlyValue keeps them read-only should a regeneration lose that."""
        values = (
            (preview.radius, preview.width, preview.height, preview.die_radius) if preview else (0.0, 0.0, 0.0, 0.0)
        )
        for block, value in zip(self._doubles, values, strict=True):
            if block is not None:
                block.Value = value
                block.ReadOnlyValue = True

    def set_direction(self, direction: Direction | None) -> None:
        """Places the arrow, or hides the block when there is nothing to point at."""
        block = self._direction
        if block is None:
            return
        if direction is None:
            block.Show = False
            return
        (ox, oy, oz), (dx, dy, dz) = direction
        block.Origin = NXOpen.Point3d(ox, oy, oz)
        block.Direction = NXOpen.Vector3d(dx, dy, dz)
        block.Show = True

    # ---- Lookup ----

    def _find(self, block_id: str) -> Any:
        try:
            block = self._top.FindBlock(block_id)
        except Exception as ex:  # noqa: BLE001  (any failure means the block is unavailable)
            _log.warning(
                "Dialog block '%s' could not be resolved (%s); the features that use it are off.", block_id, ex
            )
            return None
        if block is None:
            _log.warning("Dialog block '%s' is missing; the features that use it are off.", block_id)
        return block


def _try(what: str, action: Callable[[], object]) -> None:
    """One piece of block setup. A failure only leaves a block looking or filtering differently: logged, not shown."""
    try:
        action()
    except Exception as ex:  # noqa: BLE001
        _log.warning("%s not applied: %s", what, ex)


def _guarded(handler: Callable[..., Any], fallback: Any) -> Callable[..., Any]:
    """A block handler whose errors are logged and shown rather than thrown."""

    def run(*args: Any) -> Any:
        try:
            return handler(*args)
        except Exception as ex:  # noqa: BLE001  (boundary: the last line of defence for an NX callback)
            _log.exception("A bead dialog block handler failed")
            NxMessenger(UiText.DEFAULT.title).show_error(NxDialogText.DEFAULT.handler_failed("Bead", str(ex)))
            return fallback

    return run
