import tempfile
import FreeCAD, FreeCADGui
from PySide import QtGui
import ExportCQ, ImportCQ, CadQuery_rc

#Distinguish python built-in open function from the one declared here
if open.__module__ == '__builtin__':
    pythonopen = open


def clearAll():
    doc = FreeCAD.ActiveDocument

    #Make sure we have an active document to work with
    if doc is not None:
        for obj in doc.Objects:
            doc.removeObject(obj.Label)


class CadQueryCloseScript:
    """Allows the user to close a file without saving"""

    def GetResources(self):
        return {"MenuText": "Close Script",
                "ToolTip": "Closes the CadQuery script"}

    def IsActive(self):
        return True

    def Activated(self):
         #Getting the main window will allow us to find the children we need to work with
        mw = FreeCADGui.getMainWindow()

        #We need this so we can load the file into it
        cqCodePane = mw.findChild(QtGui.QPlainTextEdit, "cqCodePane")

        reply = QtGui.QMessageBox.question(cqCodePane, "QMessageBox.question()", "Save script before closing?", QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)

        if reply == QtGui.QMessageBox.Cancel:
            return

        if reply == QtGui.QMessageBox.Yes:
            #If we've got a file name already save it there, otherwise give a save-as dialog
            if len(cqCodePane.file.path) == 0:
                filename = QtGui.QFileDialog.getSaveFileName(mw, mw.tr("Save CadQuery Script As"), "/home/",
                                                             mw.tr("CadQuery Files (*.py)"))
            else:
                filename = cqCodePane.file.path

            #Make sure we got a valid file name
            if filename == None:
                ExportCQ.save(filename)

        #Clear our script and whatever was rendered by it out
        cqCodePane.file.close()
        clearAll()


class CadQueryExecuteScript:
    """CadQuery's command to execute a script file"""

    def GetResources(self):
        return {"MenuText": "Execute Script",
                "Accel": "F2",
                "ToolTip": "Executes the CadQuery script",
                "Pixmap": ":/icons/macro-execute.svg"}

    def IsActive(self):
        return True
        # if FreeCAD.ActiveDocument is None:
        #     return False
        # else:
        #     return True

    def Activated(self):
        #Getting the main window will allow us to find the children we need to work with
        mw = FreeCADGui.getMainWindow()

        #We need this so we can load the file into it
        cqCodePane = mw.findChild(QtGui.QPlainTextEdit, "cqCodePane")

        clearAll()

        #Save our code to a tempfile and render it
        tempFile = tempfile.NamedTemporaryFile(delete=False)
        tempFile.write(cqCodePane.toPlainText())
        tempFile.close()
        FreeCAD.Console.PrintMessage("\r\n")
        execfile(tempFile.name)

        msg = QtGui.QApplication.translate(
            "cqCodeWidget",
            "Executed ",
            None,
            QtGui.QApplication.UnicodeUTF8)
        FreeCAD.Console.PrintMessage("\r\n" + msg + cqCodePane.file.path)


class CadQueryOpenScript():
    """CadQuery's command to open a script file."""
    previousPath = None

    def GetResources(self):
        return {"MenuText": "Open Script",
                "Accel": "Alt+O",
                "ToolTip": "Opens a CadQuery script from disk",
                "Pixmap": ":/icons/document-open.svg"}

    def IsActive(self):
        return True
        # if FreeCAD.ActiveDocument is None:
        #     return False
        # else:
        #     return True

    def Activated(self):
        mw = FreeCADGui.getMainWindow()

        #Try to keep track of the previous path used to open as a convenience to the user
        if self.previousPath is None:
            self.previousPath = "/home/"

        filename = QtGui.QFileDialog.getOpenFileName(mw, mw.tr("Open CadQuery Script"), self.previousPath,
                                                     mw.tr("CadQuery Files (*.py)"))

        self.previousPath = filename[0]

        #Make sure the user didn't click cancel
        if filename[0]:
            #We've created a library that FreeCAD can use as well to open CQ files
            ImportCQ.open(filename[0])


class CadQuerySaveScript:
    """CadQuery's command to save a script file"""

    def GetResources(self):
        return {"MenuText": "Save Script",
                "Accel": "Alt+S",
                "ToolTip": "Saves the CadQuery script to disk",
                "Pixmap": ":/icons/document-save.svg"}

    def IsActive(self):
        return True
        # if FreeCAD.ActiveDocument is None:
        #     return False
        # else:
        #     return True

    def Activated(self):
        #Rely on our export library to help us save the file
        ExportCQ.save()

class CadQuerySaveAsScript:
    """CadQuery's command to save-as a script file"""
    previousPath = None

    def GetResources(self):
        return {"MenuText": "Save Script As",
                "Accel": "",
                "ToolTip": "Saves the CadQuery script to disk in a location other than the original",
                "Pixmap": ":/icons/document-save-as.svg"}

    def IsActive(self):
        return True
        # if FreeCAD.ActiveDocument is None:
        #     return False
        # else:
        #     return True

    def Activated(self):
        mw = FreeCADGui.getMainWindow()

        #Try to keep track of the previous path used to open as a convenience to the user
        if self.previousPath is None:
            self.previousPath = "/home/"

        filename = QtGui.QFileDialog.getSaveFileName(mw, mw.tr("Save CadQuery Script As"), self.previousPath,
                                                     mw.tr("CadQuery Files (*.py)"))

        self.previousPath = filename[0]

        #Make sure the user didn't click cancel
        if filename[0]:
            #Save the file before the re-render
            ExportCQ.save(filename[0])
            execfile(filename[0])