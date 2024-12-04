"""CadQuery GUI init module for FreeCAD
   This adds a workbench with a scripting editor to FreeCAD's GUI."""
# (c) 2014-2024 CadQuery Developers Apache 2.0 License
import FreeCAD, FreeCADGui
try:
    from CadQuery.CQGui.Command import *
except:
    from CQGui.Command import *


class CadQueryWorkbench (Workbench):
    """CadQuery workbench for FreeCAD"""
    """CadQuery workbench for FreeCAD"""
      
    MenuText = "CadQuery"
    ToolTip = "CadQuery workbench"

    def Initialize(self):
        self.appendMenu('CadQuery', ['Separator', 'CadQueryHelp'])

    def Activated(self):
        # Define the show_object function which CadQuery execution environments need to provide
        def show_object(cq_object):
            FreeCAD.Console.PrintMessage("show_object() called\r\n")

        # Register the show_object function as a global function
        globals()['show_object'] = show_object


    def Deactivated(self):
        pass


FreeCADGui.addCommand('CadQueryHelp', CadQueryHelp())

FreeCADGui.addWorkbench(CadQueryWorkbench())
