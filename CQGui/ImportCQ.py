"""Adds the ability to open files from disk to the CadQuery FreeCAD module"""
# (c) 2014-2016 Jeremy Wright Apache 2.0 License
import os
import sys
import FreeCAD, FreeCADGui
from PySide import QtGui
import module_locator
import Settings

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

    # CadQuery now supports Python 3
    # If the user doesn't have Python 2.7, warn them
    # if interpreter != 'python2.7':
    #     msg = QtGui.QApplication.translate(
    #         "cqCodeWidget",
    #         "Please install Python 2.7",
    #         None)
    #     FreeCAD.Console.PrintError(msg + "\r\n")

    # The extra version numbers won't work on Windows
    if sys.platform.startswith('win'):
        interpreter = 'python'

    # Set up so that we can import from our embedded packages
    module_base_path = module_locator.module_path()
    libs_dir_path = os.path.join(module_base_path, 'Libs')

    from pyqode.core.modes import FileWatcherMode
    from pyqode.core.modes import RightMarginMode
    from pyqode.python.widgets import PyCodeEdit

    # Make sure we get the right libs under the FreeCAD installation
    fc_base_path = os.path.dirname(os.path.dirname(module_base_path))
    fc_lib_path = os.path.join(fc_base_path, 'lib')

    #Getting the main window will allow us to find the children we need to work with
    mw = FreeCADGui.getMainWindow()

    # Grab just the file name from the path/file that's being executed
    docname = os.path.basename(filename)

    # Set up the text area for our CQ code
    server_path = os.path.join(module_base_path, 'cq_server.py')

    # Windows needs some extra help with paths
    if sys.platform.startswith('win'):
        codePane = PyCodeEdit(server_script=server_path, interpreter=interpreter
                              , args=['-s', fc_lib_path, libs_dir_path])
    else:
        codePane = PyCodeEdit(server_script=server_path, interpreter=interpreter
                              , args=['-s', libs_dir_path])

    # Allow easy use of an external editor
    if Settings.use_external_editor:
        codePane.modes.append(FileWatcherMode())
        codePane.modes.get(FileWatcherMode).file_reloaded.connect(AutoExecute)
        codePane.modes.get(FileWatcherMode).auto_reload = True

    # Set the margin to be at 119 characters instead of 79
    codePane.modes.get(RightMarginMode).position = Settings.max_line_length

    # Set the font size of the Python editor
    codePane.font_size = Settings.font_size

    codePane.setObjectName("cqCodePane_" + os.path.splitext(os.path.basename(filename))[0])

    mdi = mw.findChild(QtGui.QMdiArea)
    # add a widget to the mdi area
    sub = mdi.addSubWindow(codePane)
    sub.setWindowTitle(docname)
    sub.setWindowIcon(QtGui.QIcon(':/icons/applications-python.svg'))
    sub.show()
    mw.update()

    #Pull the text of the CQ script file into our code pane
    codePane.file.open(filename)

    msg = QtGui.QApplication.translate(
            "cqCodeWidget",
            "Opened ",
            None)
    FreeCAD.Console.PrintMessage(msg + filename + "\r\n")

    return
