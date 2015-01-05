"""Adds all of the commands that are used for the menus of the CadQuery module"""
# (c) 2014 Jeremy Wright LGPL v3

import imp, os, sys, tempfile
import FreeCAD, FreeCADGui
from PySide import QtGui
import ExportCQ, ImportCQ
import module_locator
import Settings

#Distinguish python built-in open function from the one declared here
if open.__module__ == '__builtin__':
    pythonopen = open


def clearActiveDocument():
    """Clears the currently active 3D view so that we can re-render"""

    doc = FreeCAD.ActiveDocument

    #Make sure we have an active document to work with
    if doc is not None:
        for obj in doc.Objects:
            doc.removeObject(obj.Label)

class CadQueryClearOutput:
    """Allows the user to clear the reports view when it gets overwhelmed with output"""

    def GetResources(self):
        return {"MenuText": "Clear Output",
                "ToolTip": "Clears the script output from the Reports view"}

    def IsActive(self):
        return True

    def Activated(self):
        #Grab our code editor so we can interact with it
        mw = FreeCADGui.getMainWindow()

        reportView = mw.findChild(QtGui.QDockWidget, "Report view")

        #Clear the view because it gets overwhelmed sometimes and won't scroll to the bottom
        reportView.widget().clear()


class CadQueryCloseScript:
    """Allows the user to close a file without saving"""

    def GetResources(self):
        return {"MenuText": "Close Script",
                "ToolTip": "Closes the CadQuery script"}

    def IsActive(self):
        return True
        # if FreeCAD.ActiveDocument is None:
        #     return False
        # else:
        #     return True

    def Activated(self):
        #Grab our code editor so we can interact with it
        mw = FreeCADGui.getMainWindow()
        cqCodePane = mw.findChild(QtGui.QPlainTextEdit, "cqCodePane")

        #If there's nothing open in the code pane, we don't need to close it
        if len(cqCodePane.file.path) == 0:
            return

        #Check to see if we need to save the script
        if cqCodePane.dirty:
            reply = QtGui.QMessageBox.question(cqCodePane, "Save CadQuery Script", "Save script before closing?",
                                               QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)

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
                if filename is not None:
                    ExportCQ.save(filename)

        #Close the matching 3D view if it's open
        if cqCodePane.file.path is not None:
            docname = os.path.splitext(os.path.basename(cqCodePane.file.path))[0]

            try:
                FreeCAD.closeDocument(docname)
            except:
                #Assume that the document has already been closed
                pass

        #Clear our script and whatever was rendered by it out
        cqCodePane.file.close()


class CadQueryExecuteScript:
    """CadQuery's command to execute a script file"""

    def GetResources(self):
        return {"MenuText": "Execute Script",
                "Accel": "F2",
                "ToolTip": "Executes the CadQuery script",
                "Pixmap": ":/icons/macro-execute.svg"}

    def IsActive(self):
        return True

    def Activated(self):
        #Grab our code editor so we can interact with it
        mw = FreeCADGui.getMainWindow()
        cqCodePane = mw.findChild(QtGui.QPlainTextEdit, "cqCodePane")

        #Clear the old render before re-rendering
        clearActiveDocument()

        #Save our code to a tempfile and render it
        tempFile = tempfile.NamedTemporaryFile(delete=False)
        tempFile.write(cqCodePane.toPlainText())
        tempFile.close()
        FreeCAD.Console.PrintMessage("\r\n")

        docname = os.path.splitext(os.path.basename(cqCodePane.file.path))[0]

        #If the matching 3D view has been closed, we need to open a new one
        try:
           FreeCAD.getDocument(docname)
        except:
            FreeCAD.newDocument(docname)


        #We import this way because using execfile() causes non-standard script execution in some situations
        imp.load_source('temp.module', tempFile.name)

        msg = QtGui.QApplication.translate(
            "cqCodeWidget",
            "Executed ",
            None,
            QtGui.QApplication.UnicodeUTF8)
        FreeCAD.Console.PrintMessage("\r\n" + msg + cqCodePane.file.path)


class CadQueryNewScript:
    """CadQuery's command to start a new script file."""
    def GetResources(self):
        return {"MenuText": "New Script",
                "Accel": "Alt+N",
                "ToolTip": "Starts a new CadQuery script",
                "Pixmap": ":/icons/document-new.svg"}

    def IsActive(self):
        return True

    def Activated(self):
        #We need to close any file that's already open in the editor window
        CadQueryCloseScript().Activated()

        module_base_path = module_locator.module_path()
        templ_dir_path = os.path.join(module_base_path, 'Templates')

        #Use the library that FreeCAD can use as well to open CQ files
        ImportCQ.open(os.path.join(templ_dir_path, 'script_template.py'))


class CadQueryOpenScript:
    """CadQuery's command to open a script file."""
    previousPath = None

    def GetResources(self):
        return {"MenuText": "Open Script",
                "Accel": "Alt+O",
                "ToolTip": "Opens a CadQuery script from disk",
                "Pixmap": ":/icons/document-open.svg"}

    def IsActive(self):
        return True

    def Activated(self):
        #So we can open the "Open File" dialog
        mw = FreeCADGui.getMainWindow()

        #Try to keep track of the previous path used to open as a convenience to the user
        if self.previousPath is None:
            #Start off defaulting to the Examples directory
            module_base_path = module_locator.module_path()
            exs_dir_path = os.path.join(module_base_path, 'Examples')

            self.previousPath = exs_dir_path

        filename = QtGui.QFileDialog.getOpenFileName(mw, mw.tr("Open CadQuery Script"), self.previousPath,
                                                     mw.tr("CadQuery Files (*.py)"))

        #Make sure the user didn't click cancel
        if filename[0]:
            #We need to close any file that's already open in the editor window
            CadQueryCloseScript().Activated()

            self.previousPath = filename[0]

            #Append this script's directory to sys.path
            sys.path.append(os.path.dirname(filename[0]))

            #We've created a library that FreeCAD can use as well to open CQ files
            ImportCQ.open(filename[0])

            docname = os.path.splitext(os.path.basename(filename[0]))[0]
            FreeCAD.newDocument(docname)

            #Execute the script
            CadQueryExecuteScript().Activated()

            #Get a nice view of our model
            FreeCADGui.activeDocument().activeView().viewAxometric()
            FreeCADGui.SendMsgToActiveView("ViewFit")


class CadQuerySaveScript:
    """CadQuery's command to save a script file"""

    def GetResources(self):
        return {"MenuText": "Save Script",
                "Accel": "Alt+S",
                "ToolTip": "Saves the CadQuery script to disk",
                "Pixmap": ":/icons/document-save.svg"}

    def IsActive(self):
        return True

    def Activated(self):
        #Grab our code editor so we can interact with it
        mw = FreeCADGui.getMainWindow()
        cqCodePane = mw.findChild(QtGui.QPlainTextEdit, "cqCodePane")

        #If the code pane doesn't have a filename, we need to present the save as dialog
        if len(cqCodePane.file.path) == 0 or os.path.basename(cqCodePane.file.path) == 'script_template.py' \
                or os.path.split(cqCodePane.file.path)[-2].endswith('Examples'):
            FreeCAD.Console.PrintError("\r\nYou cannot save over a blank file, example file or template file.")

            CadQuerySaveAsScript().Activated()

            return

        #Rely on our export library to help us save the file
        ExportCQ.save()

        #Execute the script if the user has asked for it
        if Settings.execute_on_save:
            CadQueryExecuteScript().Activated()

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

    def Activated(self):
        #So we can open the save-as dialog
        mw = FreeCADGui.getMainWindow()
        cqCodePane = mw.findChild(QtGui.QPlainTextEdit, "cqCodePane")

        #Try to keep track of the previous path used to open as a convenience to the user
        if self.previousPath is None:
            self.previousPath = "/home/"

        filename = QtGui.QFileDialog.getSaveFileName(mw, mw.tr("Save CadQuery Script As"), self.previousPath,
                                                     mw.tr("CadQuery Files (*.py)"))

        self.previousPath = filename[0]

        #Make sure the user didn't click cancel
        if filename[0]:
            #Close the 3D view for the original script if it's open
            try:
                docname = os.path.splitext(os.path.basename(cqCodePane.file.path))[0]
                FreeCAD.closeDocument(docname)
            except:
                #Assume that there was no 3D view to close
                pass

            #Save the file before closing the original and the re-rendering the new one
            ExportCQ.save(filename[0])
            CadQueryExecuteScript().Activated()
