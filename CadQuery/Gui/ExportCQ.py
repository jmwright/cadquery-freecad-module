import FreeCAD, FreeCADGui
from PySide import QtGui

def export(self, filename):
    save(filename)

def save(filename=None):
    """
    Allows us to save the CQ script file to disk.
    :param filename: The path and file name to save to. If not provided we try to pull it from the code pane itself
    """

    #Getting the main window will allow us to find the children we need to work with
    mw = FreeCADGui.getMainWindow()

    #We need this so we can load the file into it
    cqCodePane = mw.findChild(QtGui.QPlainTextEdit, "cqCodePane")

    #If we weren't provided a file name, we need to find it from the text field
    if filename is None:
        cqCodePane.file.save()
    else:
        cqCodePane.file.save(filename)

    msg = QtGui.QApplication.translate(
            "cqCodeWidget",
            "Saved ",
            None,
            QtGui.QApplication.UnicodeUTF8)
    FreeCAD.Console.PrintMessage("\r\n" + msg + cqCodePane.file.path)
