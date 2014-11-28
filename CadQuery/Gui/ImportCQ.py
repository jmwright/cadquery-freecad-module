"""Adds the ability to open files from disk to the CadQuery FreeCAD module"""
# (c) 2014 Jeremy Wright LGPL v3

import os, FreeCAD, FreeCADGui
from PySide import QtGui

#Distinguish python built-in open function from the one declared here
if open.__module__ == '__builtin__':
    pythonopen = open

def open(filename):
    docname = os.path.splitext(os.path.basename(filename))[0]
    doc = FreeCAD.newDocument(docname)

    #All of the Gui.* calls in the Python console break after opening if we don't do this
    FreeCADGui.doCommand("import FreeCADGui as Gui")

    #Getting the main window will allow us to find the children we need to work with
    mw = FreeCADGui.getMainWindow()

    #We need this so we can load the file into it
    cqCodePane = mw.findChild(QtGui.QPlainTextEdit, "cqCodePane")

    #Pull the text of the CQ script file into our code pane
    cqCodePane.file.open(filename)

    execfile(filename)

    msg = QtGui.QApplication.translate(
            "cqCodeWidget",
            "Opened ",
            None,
            QtGui.QApplication.UnicodeUTF8)
    FreeCAD.Console.PrintMessage("\r\n" + msg + filename)

    return doc