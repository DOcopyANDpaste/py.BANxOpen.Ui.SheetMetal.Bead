"""Type-only: pyright checks that the real NX classes are what the presenter's protocols say. dialog.py cannot be
relied on for this, since the untyped generated base class turns argument checks off there."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from banxopen.foundation.ui import Messenger, NxMessenger
    from banxopen.sheetmetal.nx import BeadTool
    from banxopen.ui_bead.presenter import Tool, View
    from banxopen.ui_bead.view import BeadDialogView

    def _tool(tool: BeadTool) -> Tool:
        return tool

    def _view(view: BeadDialogView) -> View:
        return view

    def _messenger(messenger: NxMessenger) -> Messenger:
        return messenger
