"""CadQuery GUI init module for FreeCAD
   This adds a workbench with a scripting editor to FreeCAD's GUI."""
# (c) 2014-2015 Jeremy Wright LGPL v3

import FreeCAD, FreeCADGui
from Gui.Command import *
import CadQuery_rc


class CadQueryWorkbench (Workbench):
    """CadQuery workbench for FreeCAD"""
    MenuText = "CadQuery"
    ToolTip = "CadQuery workbench"
    Icon = ":/icons/CQ_Logo.svg"

    #Keeps track of which workbenches we have hidden so we can reshow them
    closedWidgets = []

    def Initialize(self):
        import os

        #Need to set this for PyQode
        os.environ['QT_API'] = 'pyside'

        #Turn off logging for now
        #import logging
        #logging.basicConfig(filename='C:\\Users\\Jeremy\\Documents\\', level=logging.DEBUG)
        #logging.basicConfig(filename='/home/jwright/Documents/log.txt', level=logging.DEBUG)
        submenu = []

        dirs = self.ListExamples()

        # Step through and add an Examples submenu item for each example
        for curFile in dirs:
            submenu.append(str(curFile))

        #We have our own CQ menu that's added when the user chooses our workbench
        self.appendMenu('CadQuery', ['CadQueryNewScript', 'CadQueryOpenScript', 'CadQuerySaveScript',
                                     'CadQuerySaveAsScript', 'CadQueryCloseScript'])
        self.appendMenu(['CadQuery', 'Examples'], submenu)
        self.appendMenu('CadQuery', ['Separator', 'CadQueryExecuteScript', 'CadQueryClearOutput'])

    def Activated(self):
        import os, sys
        import module_locator
        from Gui import Command, ImportCQ
        import Settings

        #Set up so that we can import from our embedded packages
        module_base_path = module_locator.module_path()
        libs_dir_path = os.path.join(module_base_path, 'Libs')
        sys.path.insert(0, libs_dir_path)

        # Tack on our CadQuery library git subtree
        cq_lib_path = os.path.join(libs_dir_path, 'cadquery-lib')
        sys.path.insert(1, cq_lib_path)

        #Make sure we get the right libs under the FreeCAD installation
        fc_base_path = os.path.dirname(os.path.dirname(module_base_path))
        fc_lib_path = os.path.join(fc_base_path, 'lib')
        fc_bin_path = os.path.join(fc_base_path, 'bin')

        #Make sure that the directories exist before we add them to sys.path
        #This could cause problems or solve them by overriding what CQ is setting for the paths
        if os.path.exists(fc_lib_path):
            sys.path.insert(1, fc_lib_path)
        if os.path.exists(fc_bin_path):
            sys.path.insert(1, fc_bin_path)

        import cadquery
        from pyqode.core.modes import FileWatcherMode
        from pyqode.python.widgets import PyCodeEdit
        from PySide import QtGui, QtCore

        msg = QtGui.QApplication.translate(
            "cqCodeWidget",
            "CadQuery " + cadquery.__version__ + "\r\n"
            "CadQuery is a parametric scripting language "
            "for creating and traversing CAD models\r\n"
            "Author: David Cowden\r\n"
            "License: LGPL\r\n"
            "Website: https://github.com/dcowden/cadquery\r\n",
            None,
            QtGui.QApplication.UnicodeUTF8)
        FreeCAD.Console.PrintMessage(msg)

        #Make sure that we enforce a specific version (2.7) of the Python interpreter
        ver = hex(sys.hexversion)
        interpreter = "python%s.%s" % (ver[2], ver[4])  # => 'python2.7'

        #If the user doesn't have Python 2.7, warn them
        if interpreter != 'python2.7':
            msg = QtGui.QApplication.translate(
                "cqCodeWidget",
                "Please install Python 2.7",
                None,
                QtGui.QApplication.UnicodeUTF8)
            FreeCAD.Console.PrintError(msg + "\r\n")

        #The extra version numbers won't work on Windows
        if sys.platform.startswith('win'):
            interpreter = 'python'

        #Getting the main window will allow us to start setting things up the way we want
        mw = FreeCADGui.getMainWindow()

        dockWidgets = mw.findChildren(QtGui.QDockWidget)

        for widget in dockWidgets:
            if widget.objectName() == "Report view":
                widget.setVisible(True)

        #Add a new widget here that's a simple text area to begin with. It will become the CQ coding area
        cqCodeWidget = QtGui.QDockWidget("CadQuery Code View")
        cqCodeWidget.setObjectName("cqCodeView")
        mw.addDockWidget(QtCore.Qt.LeftDockWidgetArea, cqCodeWidget)

        #Set up the text area for our CQ code
        server_path = os.path.join(module_base_path, 'cq_server.py')

        #Windows needs some extra help with paths
        if sys.platform.startswith('win'):
            codePane = PyCodeEdit(server_script=server_path, interpreter=interpreter
                                  , args=['-s', fc_lib_path, libs_dir_path])
        else:
            codePane = PyCodeEdit(server_script=server_path, interpreter=interpreter
                                  , args=['-s', libs_dir_path])

        # Allow easy use of an external editor
        if Settings.use_external_editor:
            codePane.modes.append(FileWatcherMode())
            codePane.modes.get(FileWatcherMode).file_reloaded.connect(self.AutoExecute)
            codePane.modes.get(FileWatcherMode).auto_reload = True

        codePane.setObjectName("cqCodePane")

        #Add the text area to our dock widget
        cqCodeWidget.setWidget(codePane)

        #Set up the paths to allow us to open and execute our introduction example
        #example_path = os.path.join(module_base_path, 'Examples')
        #example_path = os.path.join(example_path, 'Ex000_Introduction.py')

        # TODO: Enable this for FreeCAD 0.16 or greater
        # Make sure we get the correct MdiArea object
        # for child in mw.children():
        #     if child.__class__ == QtGui.QMdiArea:
        #         mdiArea = child
        #
        # # Set up the editor in a new subwindow
        # #sub_window = QtGui.QMdiSubWindow(mw.centralWidget())
        # sub_window = QtGui.QMdiSubWindow(mdiArea)
        # #sub_window.setWidget(codePane)
        # sub_window.setWidget(QtGui.QPlainTextEdit())
        # sub_window.setWindowTitle('Ex000_Introduction.py')
        # sub_window.setWindowIcon(QtGui.QIcon(':/icons/applications-python.svg'))
        #
        # #mw.centralWidget().addSubWindow(sub_window)
        # mdiArea.addSubWindow(sub_window)

        # Set up the paths to allow us to open the template
        template_path = os.path.join(module_base_path, 'Templates')
        template_path = os.path.join(template_path, 'script_template.py')

        ImportCQ.open(template_path)
        docname = os.path.splitext(os.path.basename(template_path))[0]
        #FreeCAD.newDocument(docname)
        #Command.CadQueryExecuteScript().Activated()

        #Get a nice view of our example
        #FreeCADGui.activeDocument().activeView().viewAxometric()
        #FreeCADGui.SendMsgToActiveView("ViewFit")

    def AutoExecute(self):
        """We should be able to pass the Gui.Commands.CadQueryExecuteScript function directly to the file_reloaded
           connect function, but that causes a segfault in FreeCAD. This function is a work-around for that. This
           function is passed to file_reloaded signal and in turn calls the CadQueryExecuteScript.Activated function."""
        import Gui.Command

        Gui.Command.CadQueryExecuteScript().Activated()

    def Deactivated(self):
        import Gui.Command
        from PySide import QtGui

        # msg = QtGui.QApplication.translate(
        #         "cqCodeWidget",
        #         "\r\nCadQuery Workbench Deactivated\r\n",
        #         None,
        #         QtGui.QApplication.UnicodeUTF8)
        #
        # #Put the UI back the way we found it
        # FreeCAD.Console.PrintMessage(msg)

        #Getting the main window will allow us to start setting things up the way we want
        mw = FreeCADGui.getMainWindow()

        cqCodePane = mw.findChild(QtGui.QPlainTextEdit, "cqCodePane")
        cqCodePane.close()
        cqCodePane.setParent(None)

        dockWidgets = mw.findChildren(QtGui.QDockWidget)

        for widget in dockWidgets:
            if widget.objectName() == "cqCodeView":
                mw.removeDockWidget(widget)

    @staticmethod
    def ListExamples():
        import os
        import module_locator

        dirs = []

        # List all of the example files in an order that makes sense
        module_base_path = module_locator.module_path()
        exs_dir_path = os.path.join(module_base_path, 'Examples')
        dirs = os.listdir(exs_dir_path)
        dirs.sort()

        return dirs

FreeCADGui.addCommand('CadQueryNewScript', CadQueryNewScript())
FreeCADGui.addCommand('CadQueryOpenScript', CadQueryOpenScript())
FreeCADGui.addCommand('CadQuerySaveScript', CadQuerySaveScript())
FreeCADGui.addCommand('CadQuerySaveAsScript', CadQuerySaveAsScript())
FreeCADGui.addCommand('CadQueryExecuteScript', CadQueryExecuteScript())
FreeCADGui.addCommand('CadQueryCloseScript', CadQueryCloseScript())
FreeCADGui.addCommand('CadQueryClearOutput', CadQueryClearOutput())

# Step through and add an Examples submenu item for each example
dirs = CadQueryWorkbench.ListExamples()
for curFile in dirs:
    FreeCADGui.addCommand(curFile, CadQueryExecuteExample(curFile))

FreeCADGui.addWorkbench(CadQueryWorkbench())
