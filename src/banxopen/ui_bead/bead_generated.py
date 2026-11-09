#==============================================================================
#  WARNING!!  This file is overwritten by the Block UI Styler while generating
#  the automation code. Any modifications to this file will be lost after
#  generating the code again.
#
#       Filename:  bead_generated.py   (Styler output: BLOCKUI_BEAD.py, renamed)
#
#  TRANSCRIBED, NOT YET GENERATED: written by hand from the C# Styler output
#  (BLOCKUI_BEAD.cs, Designcenter 2606) in the shape of NX 2412's Python
#  template (UGOPEN/SampleNXOpenApplications/Python/BlockStyler). Regenerate it
#  from application/BLOCKUI_BEAD.dlx with the Styler's Python language and
#  overwrite this file; dialog.py needs no change if the block IDs and
#  callbacks are the same.
#==============================================================================
import NXOpen
import NXOpen.BlockStyler


class BLOCKUI_BEAD:
    def __init__(self):
        try:
            self.theSession = NXOpen.Session.GetSession()
            self.theUI = NXOpen.UI.GetUI()
            self.theDlxFileName = "BLOCKUI_BEAD.dlx"
            self.theDialog = self.theUI.CreateDialog(self.theDlxFileName)
            self.theDialog.AddApplyHandler(self.apply_cb)
            self.theDialog.AddOkHandler(self.ok_cb)
            self.theDialog.AddUpdateHandler(self.update_cb)
            self.theDialog.AddCancelHandler(self.cancel_cb)
            self.theDialog.AddInitializeHandler(self.initialize_cb)
            self.theDialog.AddDialogShownHandler(self.dialogShown_cb)
            self.group0 = None # Block type: Group
            self.super_section0 = None # Block type: Super Section
            self.selection0 = None # Block type: Selection
            self.btn_ClearAll = None # Block type: Button
            self.list_SelectedObjects = None # Block type: List Box
            self.group1 = None # Block type: Group
            self.enum_BABead = None # Block type: Enumeration
            self.BeadOptions = None # Block type: Tree Control
            self.separator0 = None # Block type: Separator
            self.double_R = None # Block type: Double
            self.double_W = None # Block type: Double
            self.double_H = None # Block type: Double
            self.double_PRAD = None # Block type: Double
            self.direction0 = None # Block type: Reverse Direction
            self.BeadImage = None # Block type: Drawing Area
            self.table = None # Block type: TableLayout
            self.togglePreview = None # Block type: Toggle
            self.label_currentPref = None # Block type: Label
        except Exception as ex:
            raise ex

    def Launch(self):
        dialogResponse = None
        try:
            dialogResponse = self.theDialog.Launch()
        except Exception as ex:
            self.theUI.NXMessageBox.Show("Block Styler", NXOpen.NXMessageBox.DialogType.Error, str(ex))
        return dialogResponse

    def Dispose(self):
        if self.theDialog != None:
            self.theDialog.Dispose()
            self.theDialog = None

    def initialize_cb(self):
        try:
            self.group0 = self.theDialog.TopBlock.FindBlock("group0")
            self.super_section0 = self.theDialog.TopBlock.FindBlock("super_section0")
            self.selection0 = self.theDialog.TopBlock.FindBlock("selection0")
            self.btn_ClearAll = self.theDialog.TopBlock.FindBlock("btn_ClearAll")
            self.list_SelectedObjects = self.theDialog.TopBlock.FindBlock("list_SelectedObjects")
            self.group1 = self.theDialog.TopBlock.FindBlock("group1")
            self.enum_BABead = self.theDialog.TopBlock.FindBlock("enum_BABead")
            self.BeadOptions = self.theDialog.TopBlock.FindBlock("BeadOptions")
            self.separator0 = self.theDialog.TopBlock.FindBlock("separator0")
            self.double_R = self.theDialog.TopBlock.FindBlock("double_R")
            self.double_W = self.theDialog.TopBlock.FindBlock("double_W")
            self.double_H = self.theDialog.TopBlock.FindBlock("double_H")
            self.double_PRAD = self.theDialog.TopBlock.FindBlock("double_PRAD")
            self.direction0 = self.theDialog.TopBlock.FindBlock("direction0")
            self.BeadImage = self.theDialog.TopBlock.FindBlock("BeadImage")
            self.table = self.theDialog.TopBlock.FindBlock("table")
            self.togglePreview = self.theDialog.TopBlock.FindBlock("togglePreview")
            self.label_currentPref = self.theDialog.TopBlock.FindBlock("label_currentPref")
        except Exception as ex:
            self.theUI.NXMessageBox.Show("Block Styler", NXOpen.NXMessageBox.DialogType.Error, str(ex))

    def dialogShown_cb(self):
        try:
            pass
        except Exception as ex:
            self.theUI.NXMessageBox.Show("Block Styler", NXOpen.NXMessageBox.DialogType.Error, str(ex))

    def apply_cb(self):
        errorCode = 0
        try:
            pass
        except Exception as ex:
            errorCode = 1
            self.theUI.NXMessageBox.Show("Block Styler", NXOpen.NXMessageBox.DialogType.Error, str(ex))
        return errorCode

    def update_cb(self, block):
        try:
            if block == self.super_section0:
                pass
            elif block == self.selection0:
                pass
            elif block == self.btn_ClearAll:
                pass
            elif block == self.list_SelectedObjects:
                pass
            elif block == self.enum_BABead:
                pass
            elif block == self.separator0:
                pass
            elif block == self.double_R:
                pass
            elif block == self.double_W:
                pass
            elif block == self.double_H:
                pass
            elif block == self.double_PRAD:
                pass
            elif block == self.direction0:
                pass
            elif block == self.BeadImage:
                pass
            elif block == self.togglePreview:
                pass
            elif block == self.label_currentPref:
                pass
        except Exception as ex:
            self.theUI.NXMessageBox.Show("Block Styler", NXOpen.NXMessageBox.DialogType.Error, str(ex))
        return 0

    def ok_cb(self):
        errorCode = 0
        try:
            errorCode = self.apply_cb()
        except Exception as ex:
            errorCode = 1
            self.theUI.NXMessageBox.Show("Block Styler", NXOpen.NXMessageBox.DialogType.Error, str(ex))
        return errorCode

    def cancel_cb(self):
        try:
            pass
        except Exception as ex:
            self.theUI.NXMessageBox.Show("Block Styler", NXOpen.NXMessageBox.DialogType.Error, str(ex))
        return 0

    def GetBlockProperties(self, blockID):
        try:
            return self.theDialog.GetBlockProperties(blockID)
        except Exception as ex:
            self.theUI.NXMessageBox.Show("Block Styler", NXOpen.NXMessageBox.DialogType.Error, str(ex))
        return None


def main():
    theBLOCKUI_BEAD = None
    try:
        theBLOCKUI_BEAD = BLOCKUI_BEAD()
        theBLOCKUI_BEAD.Launch()
    except Exception as ex:
        NXOpen.UI.GetUI().NXMessageBox.Show("Block Styler", NXOpen.NXMessageBox.DialogType.Error, str(ex))
    finally:
        if theBLOCKUI_BEAD != None:
            theBLOCKUI_BEAD.Dispose()


if __name__ == "__main__":
    main()
