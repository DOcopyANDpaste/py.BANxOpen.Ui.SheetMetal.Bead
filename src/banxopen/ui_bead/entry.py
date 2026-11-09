"""The tool's entry: build the session context and the sheet metal services once per launch, then show the dialog.
Wiring only. The Bead dialog only reads the Sheet Metal Preferences and never assigns a material, so no material
engine is built."""

# NX 2412's Python stubs leave out Session.LibraryUnloadOption.
# pyright: reportAttributeAccessIssue=false

from __future__ import annotations

import NXOpen

from banxopen.foundation.nx import NxDialogText, NxSessionContext, install_nx_logging
from banxopen.foundation.ui import NxMessenger, launch_dialog
from banxopen.sheetmetal.nx import SheetMetalServices
from banxopen.ui_bead.dialog import TITLE, BeadDialog


def main() -> None:
    install_nx_logging(NXOpen.Session.GetSession())
    messenger = NxMessenger(TITLE)
    started = NxSessionContext.try_initialize()
    if not started.ok or started.value is None:
        messenger.show_error(NxDialogText.DEFAULT.could_not_start(TITLE, started.message))
        return
    services = SheetMetalServices.create(started.value)
    if not services.ok or services.value is None:
        messenger.show_error(services.message or NxDialogText.DEFAULT.could_not_start(TITLE, None))
        return
    sheet_metal = services.value
    launch_dialog(lambda: BeadDialog(sheet_metal, messenger), TITLE)


def GetUnloadOption(arg: str) -> int:  # noqa: N802  (the name NX looks for)
    return int(NXOpen.Session.LibraryUnloadOption.Immediately)
