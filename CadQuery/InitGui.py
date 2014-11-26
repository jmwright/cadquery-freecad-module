# CadQuery gui init module
# (c) 2001 Juergen Riegel LGPL
import FreeCAD
import FreeCADGui
from Gui.Command import *

class CadQueryWorkbench (Workbench):
    """CadQuery workbench object"""
    MenuText = "CadQuery"
    ToolTip = "CadQuery workbench"
    Icon = ":/icons/CQ_Logo.svg"

    #Keeps track of which workbenches we have hidden so we can reshow them
    closedWidgets = []

    def Initialize(self):
        import os

        os.environ['QT_API'] = 'pyside'

        #sys.path.append('./Libs/cadquery.zip')
        #sys.path.append('./Libs/pyqode.zip')

        #If we need a CQ menu, this would be the way to add it
        commands = ['CadQueryOpenScript', 'CadQuerySaveScript', 'CadQuerySaveAsScript', 'CadQueryExecuteScript',
                    'CadQueryCloseScript']
        self.appendMenu('CadQuery', commands)

    def Activated(self):
        import cadquery
        from PySide import QtGui
        import sys

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

        from PySide import QtGui
        from PySide import QtCore

        FreeCAD.addImportType("CadQuery Script (*.py)", "Gui.ImportCQ")
        FreeCAD.addExportType("CadQuery Script (*.py)", "Gui.ExportCQ")

        try:
            import cadquery
        except ImportError:
            msg = QtGui.QApplication.translate(
                "cqCodeWidget",
                "The cadquery library is not installed, please install it before using this workbench.\r\n"
                "Linux and MacOS Users: 'pip install --upgrade cadquery'\r\n"
                "Windows Users: 'Not sure yet.\r\n",
                None,
                QtGui.QApplication.UnicodeUTF8)
            FreeCAD.Console.PrintError(msg)

        #try:
        # import os, sys, inspect
        # cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0], "Libs/")))
        # if cmd_subfolder not in sys.path:
        #     sys.path.append(cmd_subfolder)
        import sys
        sys.path.insert(0, '/home/jwright/Documents/Projects/CadQuery/cadquery-freecad-module/CadQuery/Libs/pyqode.zip')
        sys.path.insert(0, '/home/jwright/Documents/Projects/CadQuery/cadquery-freecad-module/CadQuery/Libs/cadquery.zip')
        sys.path.append('/home/jwright/Documents/Projects/CadQuery/cadquery-freecad-module/CadQuery/Libs/pyqode.zip')
        sys.path.append('/home/jwright/Documents/Projects/CadQuery/cadquery-freecad-module/CadQuery/Libs/cadquery.zip')
        #sys.path.insert(0, '/home/jwright/Documents/Projects/CadQuery/cadquery-freecad-module/CadQuery/Libs')

        from pyqode.qt import QtWidgets
        from pyqode.python.backend import server
        from pyqode.python.widgets import PyCodeEdit
        from pyqode.python.widgets import code_edit

        # except ImportError:
        #     msg = QtGui.QApplication.translate(
        #         "cqCodeWidget",
        #         "The pyQode library is not installed, please install it before using this workbench.\r\n"
        #         "Linux and MacOS Users: 'pip install --upgrade pyqode.core pyqode.qt pyqode.python'\r\n",
        #         None,
        #         QtGui.QApplication.UnicodeUTF8)
        #     FreeCAD.Console.PrintError(msg)

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
                #FreeCAD.Console.PrintMessage(str(widget.objectName()) + " is being hidden.\n")

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
        codePane = PyCodeEdit(server_script=server.__file__, interpreter=interpreter, args=['-S', '/home/jwright/Documents/Projects/CadQuery/cadquery-freecad-module/CadQuery/Libs/pyqode.zip'])
        codePane.setObjectName("cqCodePane")

        #Add the text area to our dock widget
        cqCodeWidget.setWidget(codePane)

    def Deactivated(self):
        from PySide import QtGui
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
