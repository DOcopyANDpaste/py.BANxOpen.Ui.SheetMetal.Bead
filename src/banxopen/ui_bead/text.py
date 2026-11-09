"""The text that exists because of the Bead dialog's layout: its title, block labels and the SPEC tree's columns.

Everything else the dialog shows (the selection list, the preferences label, why Apply is blocked, the warnings, the
Apply message) is worded by `SheetMetalText` and comes in the `BeadView`, so the library says it the same way to every
tool.
"""

from __future__ import annotations

from typing import ClassVar


class UiText:
    DEFAULT: ClassVar[UiText]

    title = "Bead"

    select_bead_feature = "Select Bead Feature"
    select_bead_feature_tip = "Select existing Bead features to update to the chosen SPEC"
    select_curves = "Select Curves or Sketch"
    select_curves_tip = "Each connected chain of curves becomes one bead; draw a sketch on the fly if needed"

    column_spec = "SPEC"
    column_radius = "R"
    column_width = "W"
    column_height = "H"
    column_die_radius = "P RAD"
    column_thickness = "t"


UiText.DEFAULT = UiText()
