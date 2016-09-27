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
        from PySide import QtGui, QtCore

        msg = QtGui.QApplication.translate(
            "cqCodeWidget",
            "CadQuery " + cadquery.__version__ + "\r\n"
            "CadQuery is a parametric scripting language "
            "for creating and traversing CAD models\r\n"
            "Author: David Cowden\r\n"
            "License: Apache-2.0\r\n"
            "Website: https://github.com/dcowden/cadquery\r\n",
            None,
            QtGui.QApplication.UnicodeUTF8)
        FreeCAD.Console.PrintMessage(msg)

        #Getting the main window will allow us to start setting things up the way we want
        mw = FreeCADGui.getMainWindow()

        dockWidgets = mw.findChildren(QtGui.QDockWidget)

        for widget in dockWidgets:
            if widget.objectName() == "Report view":
                widget.setVisible(True)

        # Set up the paths to allow us to open the template
        template_path = os.path.join(module_base_path, 'Templates')
        template_path = os.path.join(template_path, 'script_template.py')

        ImportCQ.open(template_path)

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
