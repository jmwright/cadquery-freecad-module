"""Adds the ability to open files from disk to the CadQuery FreeCAD module"""
# (c) 2014-2016 Jeremy Wright Apache 2.0 License
import os
import sys
import FreeCAD, FreeCADGui
from PySide import QtGui
from PySide import QtCore
import module_locator
from CodeEditor import CodeEditor

#Distinguish python built-in open function from the one declared here
if open.__module__ == '__builtin__':
    pythonopen = open


def AutoExecute():
    """We should be able to pass the CQGui.Commands.CadQueryExecuteScript function directly to the file_reloaded
       connect function, but that causes a segfault in FreeCAD. This function is a work-around for that. This
       function is passed to file_reloaded signal and in turn calls the CadQueryExecuteScript.Activated function."""
    try:
        import CadQuery.Gui.Command
        CadQuery.Gui.Command.CadQueryExecuteScript().Activated()
    except:
        import CQGui.Command
        CQGui.Command.CadQueryExecuteScript().Activated()

def open(filename):
    #All of the CQGui.* calls in the Python console break after opening if we don't do this
    FreeCADGui.doCommand("import FreeCADGui as CQGui")

    # Make sure that we enforce a specific version (2.7) of the Python interpreter
    ver = hex(sys.hexversion)
    interpreter = "python%s.%s" % (ver[2], ver[4])  # => 'python2.7'

    # The extra version numbers won't work on Windows
    if sys.platform.startswith('win'):
        interpreter = 'python'

    # Set up so that we can import from our embedded packages
    module_base_path = module_locator.module_path()
    libs_dir_path = os.path.join(module_base_path, 'Libs')

    # Make sure we get the right libs under the FreeCAD installation
    fc_base_path = os.path.dirname(os.path.dirname(module_base_path))
    fc_lib_path = os.path.join(fc_base_path, 'lib')

    #Getting the main window will allow us to find the children we need to work with
    mw = FreeCADGui.getMainWindow()

    # Grab just the file name from the path/file that's being executed
    docname = os.path.basename(filename)

    # Pull the font size from the FreeCAD-stored settings
    fontSize = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/cadquery-freecad-module").GetInt("fontSize")

    # Set up the code editor
    codePane = CodeEditor()
    codePane.setFont(QtGui.QFont('SansSerif', fontSize))
    codePane.setObjectName("cqCodePane_" + os.path.splitext(os.path.basename(filename))[0])

    mdi = mw.findChild(QtGui.QMdiArea)
    # add a code editor widget to the mdi area
    sub = mdi.addSubWindow(codePane)
    sub.setWindowTitle(docname)
    sub.setWindowIcon(QtGui.QIcon(':/icons/applications-python.svg'))
    sub.show()
    mw.update()

    #Pull the text of the CQ script file into our code pane
    codePane.open(filename)

    msg = QtGui.QApplication.translate(
            "cqCodeWidget",
            "Opened ",
            None)
    FreeCAD.Console.PrintMessage(msg + filename + "\r\n")

    return
