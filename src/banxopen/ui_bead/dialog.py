"""The Styler dialog, rewired by overriding its callbacks: the generated file is never edited. Each override is one
delegation to the presenter. OK needs none: the generated ok_cb calls apply_cb."""

# The Styler-generated base class is untyped Python: pyright infers its attributes as None and its callbacks as
# returning None. These rules would only report that inference here.
# pyright: reportOptionalMemberAccess=false, reportIncompatibleMethodOverride=false, reportArgumentType=false

from __future__ import annotations

from banxopen.foundation.ui import NxMessenger, ui_callback
from banxopen.sheetmetal.nx import BeadTool, SheetMetalServices
from banxopen.ui_bead import view as blocks
from banxopen.ui_bead.bead_generated import BLOCKUI_BEAD
from banxopen.ui_bead.presenter import BeadPresenter
from banxopen.ui_bead.text import UiText
from banxopen.ui_bead.view import BeadDialogView

TITLE = UiText.DEFAULT.title


class BeadDialog(BLOCKUI_BEAD):
    """Mode: interactive."""

    def __init__(self, services: SheetMetalServices, messenger: NxMessenger, text: UiText | None = None) -> None:
        self._tool = BeadTool.create(services)
        self._messenger = messenger
        self._text = text or UiText.DEFAULT
        self._presenter: BeadPresenter | None = None
        super().__init__()  # generated: creates the dialog and registers its callbacks

    @ui_callback(TITLE)
    def initialize_cb(self) -> int:
        super().initialize_cb()  # generated: finds the blocks
        view = BeadDialogView(self.theDialog, self._text)
        self._presenter = BeadPresenter(self._tool, view, self._messenger, self._text)
        view.connect(self._presenter)
        self._presenter.on_initialize()
        return 0

    @ui_callback(TITLE)
    def dialogShown_cb(self) -> int:  # noqa: N802  (Styler name)
        self._p.on_shown()
        return 0

    @ui_callback(TITLE)
    def update_cb(self, block: object) -> int:
        match BeadDialogView.update_of(block):  # type: ignore[arg-type]  # a UIBlock
            case blocks.CURVES | blocks.BEAD_FEATURES:
                self._p.on_selection_changed()
            case blocks.CLEAR_BUTTON:
                self._p.on_clear()
            case blocks.BEAD_SPEC_ENUM:
                self._p.on_bead_spec_changed()
            case blocks.DIRECTION | blocks.PREVIEW_TOGGLE:
                self._p.on_controls_changed()
            case _:
                pass
        return 0

    @ui_callback(TITLE)
    def apply_cb(self) -> int:
        return self._p.on_apply()

    def Dispose(self) -> None:  # noqa: N802  (Styler name)
        """However the dialog closed: the tool takes any live preview down first."""
        try:
            self._tool.close()
        finally:
            super().Dispose()

    @property
    def _p(self) -> BeadPresenter:
        assert self._presenter is not None, "initialize_cb runs before any other callback"
        return self._presenter
