"""The presenter turns blocks into BeadControls, calls one BeadTool gesture and renders the view; no decisions."""

from dataclasses import dataclass, replace

from banxopen.foundation import OperationResult
from banxopen.foundation.ui import CHECKED, UNCHECKED
from banxopen.sheetmetal import BeadControls, BeadSpecRow, BeadView, SpecPreview
from banxopen.ui_bead.presenter import BeadPresenter, same_spec, spec_rows


def spec(spec_id: str, thickness: float = 0.02, workbook: str = "B1005010") -> BeadSpecRow:
    return BeadSpecRow("BAPS", workbook, spec_id, 0.245, 0.625, 0.625, 0.18751, thickness)


A = spec("B1005010-1")
B = spec("B1005010-2", 0.032)


def bead_view(controls: BeadControls, *rows: BeadSpecRow, info=None, kept=frozenset(), lines=("New bead",)) -> BeadView:
    picked = controls.picked_spec
    return BeadView(
        controls=controls,
        spec_rows=rows,
        kept_for_beads=frozenset(kept),
        spec_preview=SpecPreview(picked.radius_and_rad_s, picked.width, picked.height, picked.die_radius_p)
        if picked
        else None,
        selection_lines=lines,
        preference_summary="Sheet Metal Preferences: 2024-O_0.020, t 0.02",
        mode="New",
        blocking=None,
        warnings=None,
        info=info,
        direction=((0.0, 0.0, 0.0), (0.0, 0.0, 1.0)) if lines else None,
    )


@dataclass
class Contents:
    bead_features: tuple
    curve_sections: tuple


class FakeTool:
    def __init__(self, rows=(A, B)):
        self.rows = rows
        self.calls: list[tuple] = []
        self.open_info: str | None = None
        self.prefill: BeadSpecRow | None = None
        self.apply_result: OperationResult[str] = OperationResult.success("Bead(s) created/updated.")
        self.closed = False
        self.fail_next = False

    def _view(self, controls, info=None):
        if self.fail_next:
            self.fail_next = False
            raise RuntimeError("boom")
        if self.prefill is not None:
            controls = replace(controls, picked_spec=self.prefill, bead_spec="B1005010")
        return bead_view(controls, *self.rows, info=info)

    def open(self, controls):
        self.calls.append(("open", controls))
        return self._view(controls, self.open_info)

    def selection_changed(self, curve_block_objects, feature_block_objects, controls):
        self.calls.append(("selection_changed", tuple(curve_block_objects), tuple(feature_block_objects), controls))
        return self._view(controls)

    def controls_changed(self, controls, *, bead_spec_changed=False):
        self.calls.append(("controls_changed", controls, bead_spec_changed))
        return self._view(controls, "No row matches" if bead_spec_changed else None)

    def delete_lines(self, indices):
        self.calls.append(("delete_lines", tuple(indices)))
        return Contents(("feature",), ("section",))

    def apply(self, controls):
        self.calls.append(("apply", controls))
        return self.apply_result

    def close(self):
        self.closed = True


class FakeView:
    def __init__(self):
        self.shown = False
        self.radio = "B1005010"
        self.flip = False
        self.preview = False
        self.curves = ["c1"]
        self.features: list = []
        self.tree: list | None = None
        self.tree_builds = 0
        self.checked: list = []
        self.lines: list[str] = []
        self.summary = ""
        self.preview_values = None
        self.direction = None

    def mark_shown(self):
        self.shown = True

    def bead_spec_names(self):
        return ("B1005010", "S5010")

    def bead_spec(self):
        return self.radio

    def set_bead_spec(self, name):
        self.radio = name

    def flipped(self):
        return self.flip

    def preview_on(self):
        return self.preview

    def curve_objects(self):
        return list(self.curves)

    def feature_objects(self):
        return list(self.features)

    def set_block_contents(self, features, sections):
        self.features, self.curves = list(features), list(sections)

    def clear_selection(self):
        self.set_block_contents((), ())

    def show_specs(self, columns, rows):
        self.tree = list(rows)
        self.tree_builds += 1

    def check_spec(self, picked):
        self.checked.append(picked)

    def set_selection_lines(self, lines):
        self.lines = list(lines)

    def set_preference_summary(self, text):
        self.summary = text

    def set_spec_preview(self, preview):
        self.preview_values = preview

    def set_direction(self, direction):
        self.direction = direction


class FakeMessenger:
    def __init__(self, answer=True):
        self.shown: list[tuple[OperationResult, str | None]] = []

    def show_result(self, result, success_message=None):
        self.shown.append((result, success_message))

    def ask(self, question):
        return True


def started(tool=None):
    tool, view, messenger = tool or FakeTool(), FakeView(), FakeMessenger()
    presenter = BeadPresenter(tool, view, messenger)
    presenter.on_initialize()
    presenter.on_shown()
    return presenter, tool, view, messenger


def test_initialize_reads_the_part_and_dialog_shown_fills_the_tree():
    tool, view, messenger = FakeTool(), FakeView(), FakeMessenger()
    p = BeadPresenter(tool, view, messenger)

    p.on_initialize()
    assert view.tree_builds == 0  # NX refuses tree columns before the dialog is shown
    assert view.summary.startswith("Sheet Metal Preferences")

    p.on_shown()
    assert view.tree is not None
    assert [r.text for r in view.tree] == ["B1005010-1", "B1005010-2"]
    assert tool.calls[0][0] == "open" and tool.calls[1][0] == "selection_changed"
    assert tool.calls[1][1] == ("c1",)


def test_the_message_from_open_is_shown_once_the_dialog_is_up():
    tool = FakeTool()
    tool.open_info = "Bead SPEC 'B1005010' offers no SPECs"
    _, _, _, messenger = started(tool)

    assert [m for _, m in messenger.shown] == ["Bead SPEC 'B1005010' offers no SPECs"]


def test_the_controls_carry_the_blocks_and_the_checked_row():
    p, tool, view, _ = started()
    view.flip, view.preview = True, True

    p.on_spec_checked(B)

    _, controls, _ = tool.calls[-1]
    assert controls == BeadControls(("B1005010", "S5010"), "B1005010", B, True, True)
    assert view.checked[-1] is B


def test_a_click_that_resolves_to_no_row_keeps_the_pick():
    p, tool, view, _ = started()
    p.on_spec_checked(A)
    calls = len(tool.calls)

    p.on_spec_checked(None)

    assert view.checked[-1] is A
    assert len(tool.calls) == calls  # nothing changed, nothing asked


def test_the_tree_is_only_rebuilt_when_its_rows_change():
    p, _, view, _ = started()
    builds = view.tree_builds

    p.on_controls_changed()

    assert view.tree_builds == builds
    assert view.checked  # the check is re-asserted instead


def test_the_library_prefill_is_written_back_to_the_blocks():
    tool = FakeTool()
    p, _, view, _ = started(tool)
    view.radio = "S5010"
    tool.prefill = B

    p.on_selection_changed()

    assert view.radio == "B1005010"
    assert view.checked[-1] is B  # same rows: the check is moved, the tree is not rebuilt


def test_spec_rows_check_the_picked_row_and_warn_on_kept_ones():
    view = bead_view(BeadControls(picked_spec=A), A, B, kept=frozenset({B}))

    rows = spec_rows(view)

    assert [r.state for r in rows] == [CHECKED, UNCHECKED]
    assert [r.warning for r in rows] == [False, True]
    assert rows[0].columns[4] == "0.1875"  # 0.#### as the C# dialog showed it


def test_the_same_spec_id_in_another_workbook_is_another_row():
    assert same_spec(A, spec("b1005010-1"))
    assert not same_spec(A, spec("B1005010-1", workbook="B1005010_rev2"))


def test_a_new_bead_spec_shows_the_librarys_message():
    p, tool, _, messenger = started()

    p.on_bead_spec_changed()

    assert tool.calls[-1][2] is True
    assert messenger.shown[-1][1] == "No row matches"


def test_deleting_lines_sets_both_blocks_from_the_tool_then_refreshes():
    p, tool, view, _ = started()

    p.on_lines_deleted([0])

    assert tool.calls[-2] == ("delete_lines", (0,))
    assert view.features == ["feature"] and view.curves == ["section"]
    assert tool.calls[-1][0] == "selection_changed"


def test_clear_empties_both_blocks():
    p, tool, _, _ = started()

    p.on_clear()

    assert tool.calls[-1][1:3] == ((), ())


def test_apply_shows_the_librarys_message_and_rereads():
    p, tool, _, messenger = started()

    assert p.on_apply() == 0

    result, message = messenger.shown[-1]
    assert result.ok and message == "Bead(s) created/updated."
    assert tool.calls[-1][0] == "selection_changed"


def test_a_blocked_apply_keeps_the_dialog_open_with_the_librarys_reason():
    tool = FakeTool()
    tool.apply_result = OperationResult.fail("BEAD_APPLY_BLOCKED", "Choose a SPEC from the bead options first.")
    p, _, _, messenger = started(tool)

    assert p.on_apply() == 1
    assert messenger.shown[-1][0].message == "Choose a SPEC from the bead options first."


def test_a_failing_gesture_redraws_from_the_last_view():
    tool = FakeTool()
    p, _, view, _ = started(tool)
    builds = view.tree_builds
    tool.fail_next = True

    p.on_selection_changed()

    assert view.tree_builds == builds + 1  # the tree is rebuilt, not left empty


def test_close_takes_the_preview_down():
    p, tool, _, _ = started()

    p.on_close()

    assert tool.closed
