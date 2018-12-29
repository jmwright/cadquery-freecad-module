"""Adds the ability to save a script file to the CadQuery module"""
# (c) 2014-2016 Jeremy Wright Apache 2.0 License

import FreeCAD, FreeCADGui
from PySide import QtGui
import Shared

def export(self, filename):
    save(filename)

def save(filename=None):
    """
    Allows us to save the CQ script file to disk.
    :param filename: The path and file name to save to. If not provided we try to pull it from the code pane itself
    """

    #Grab our code editor so we can interact with it
    cqCodePane = Shared.getActiveCodePane()

    cqCodePane.save(filename)

    msg = QtGui.QApplication.translate(
            "cqCodeWidget",
            "Saved ",
            None)
    FreeCAD.Console.PrintMessage(msg + cqCodePane.get_path() + "\r\n")
