"""CadQuery GUI init module for FreeCAD
   This adds a workbench with a scripting editor to FreeCAD's GUI."""
# (c) 2014 Jeremy Wright LGPL v3

import FreeCAD
import FreeCADGui
from Gui.Command import *

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
        #logging.basicConfig(filename='/home/jwright/Documents/log.txt', level=logging.DEBUG)
        
        #We have our own CQ menu that's added when the user chooses our workbench
        commands = ['CadQueryOpenScript', 'CadQuerySaveScript', 'CadQuerySaveAsScript', 'CadQueryExecuteScript',
                    'CadQueryCloseScript']
        self.appendMenu('CadQuery', commands)

    def Activated(self):
        import os, sys
        from PySide import QtGui, QtCore
        import module_locator

        #Set up so that we can import from our embedded packages
        module_base_path = module_locator.module_path()
        libs_path = os.path.join(module_base_path, 'Libs')
        libs_path = os.path.join(libs_path, 'libs.zip')
        sys.path.insert(0, libs_path)

        import cadquery
        from pyqode.python.widgets import PyCodeEdit

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
            FreeCAD.Console.PrintError("\r\n" + msg)

        #Getting the main window will allow us to start setting things up the way we want
        mw = Gui.getMainWindow()

        #Find all of the docks that are open so we can close them (except the Python console)
        dockWidgets = mw.findChildren(QtGui.QDockWidget)

        for widget in dockWidgets:
            if widget.objectName() != "Report view":
                #Only hide the widget if it isn't already hidden
                if not widget.isHidden():
                    widget.setVisible(False)
                    #FreeCAD.Console.PrintMessage(widget.objectName())
                    self.closedWidgets.append(widget)
            else:
                widget.setVisible(True)

        #Add a new widget here that's a simple text area to begin with. It will become the CQ coding area
        cqCodeWidget = QtGui.QDockWidget("CadQuery Code View")
        cqCodeWidget.setObjectName("cqCodeView")
        mw.addDockWidget(QtCore.Qt.LeftDockWidgetArea, cqCodeWidget)

        #Set up the text area for our CQ code
        server_path = os.path.join(module_base_path, 'cq_server.py')
        codePane = PyCodeEdit(server_script=server_path, interpreter=interpreter, args=['-s', libs_path])
        codePane.setObjectName("cqCodePane")

        #Add the text area to our dock widget
        cqCodeWidget.setWidget(codePane)

    def Deactivated(self):
        from Gui import ExportCQ

        #Put the UI back the way we found it
        FreeCAD.Console.PrintMessage("\r\nCadQuery Workbench Deactivated\r\n")

        #Rely on our export library to help us save the file
        ExportCQ.save()

        #TODO: This won't work for now because the views are destroyed when they are hidden
        # for widget in self.closedWidgets:
        #     FreeCAD.Console.PrintMessage(widget.objectName())
        #     widget.setVisible(True)

FreeCADGui.addCommand('CadQueryOpenScript', CadQueryOpenScript())
FreeCADGui.addCommand('CadQuerySaveScript', CadQuerySaveScript())
FreeCADGui.addCommand('CadQuerySaveAsScript', CadQuerySaveAsScript())
FreeCADGui.addCommand('CadQueryExecuteScript', CadQueryExecuteScript())
FreeCADGui.addCommand('CadQueryCloseScript', CadQueryCloseScript())

FreeCADGui.addWorkbench(CadQueryWorkbench())
