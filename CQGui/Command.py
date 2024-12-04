# -*- coding: utf-8 -*-
"""Adds all of the commands that are used for the menus of the CadQuery module"""
# (c) 2014-2024 CadQuery Developers Apache 2.0 License
import imp, os, sys, tempfile
import FreeCAD, FreeCADGui
from PySide import QtGui
import CQGui.Shared as Shared
from random import random
from contextlib import contextmanager
from CQGui.HelpDialog import HelpDialog
# from cadquery import cqgi
from CQGui.Helpers import show

# Distinguish python built-in open function from the one declared here
if open.__module__ == '__builtin__':
    pythonopen = open


@contextmanager
def revert_sys_modules():
    """
    Remove any new modules after context has exited
    >>> with revert_sys_modules():
    ...     import some_module
    ...     some_module.do_something()
    >>> some_module.do_something()  # raises NameError: name 'some_module' is not defined
    """
    modules_before = set(sys.modules.keys())
    try:
        yield
    finally:
        # irrespective of the success of the context's execution, new modules
        # will be deleted upon exit
        for mod_name in list(sys.modules.keys()):
            if mod_name not in modules_before:
                del sys.modules[mod_name]


class CadQueryClearOutput:
    """Allows the user to clear the reports view when it gets overwhelmed with output"""

    def GetResources(self):
        return {"MenuText": "Clear Output",
                "Accel": "Shift+Alt+C",
                "ToolTip": "Clears the script output from the Reports view",
                "Pixmap": ":/icons/button_invalid.svg"}

    def IsActive(self):
        return True

    def Activated(self):
        # Grab our main window so we can interact with it
        mw = FreeCADGui.getMainWindow()

        reportView = mw.findChild(QtGui.QDockWidget, "Report view")

        # Clear the view because it gets overwhelmed sometimes and won't scroll to the bottom
        reportView.widget().clear()


class CadQueryExecuteScript:
    """CadQuery's command to execute a script file"""

    def GetResources(self):
        return {"MenuText": "Execute Script",
                "Accel": FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/cadquery-freecad-module").GetString("executeKeybinding"),
                "ToolTip": "Executes the CadQuery script",
                "Pixmap": ":/icons/media-playback-start.svg"}

    def IsActive(self):
        return True

    def Activated(self):
        # Grab our code editor so we can interact with it
        cqCodePane = Shared.getActiveCodePane()

        # Clear the old render before re-rendering
        Shared.clearActiveDocument()

        scriptText = cqCodePane.toPlainText().encode('utf-8')

        # Check to see if we are executig a CQGI compliant script
        if b"show_object(" in scriptText or b"debug(" in scriptText:
            FreeCAD.Console.PrintMessage("Executing CQGI-compliant script.\r\n")

            # Set some environment variables that may help the user
            os.environ["MYSCRIPT_FULL_PATH"] = cqCodePane.get_path()
            os.environ["MYSCRIPT_DIR"] = os.path.dirname(os.path.abspath(cqCodePane.get_path()))

            # A repreentation of the CQ script with all the metadata attached
            # cqModel = cqgi.parse(scriptText)

            # Allows us to present parameters to users later that they can alter
            parameters = cqModel.metadata.parameters
            build_parameters = {}

            # Collect the build parameters from the Parameters Editor view, if they exist
            mw = FreeCADGui.getMainWindow()

            # Tracks whether or not we have already added the variables editor
            isPresent = False

            # If the widget is open, we need to close it
            dockWidgets = mw.findChildren(QtGui.QDockWidget)
            for widget in dockWidgets:
                if widget.objectName() == "cqVarsEditor":
                    # Toggle the visibility of the widget
                    if not widget.visibleRegion().isEmpty():
                        # Find all of the controls that will have parameter values in them
                        valueControls = mw.findChildren(QtGui.QLineEdit)
                        for valueControl in valueControls:
                            objectName = valueControl.objectName()

                            # We only want text fields that will have parameter values in them
                            if objectName != None and objectName != '' and objectName.find('pcontrol_') >= 0:
                                # Associate the value in the text field with the variable name in the script
                                build_parameters[objectName.replace('pcontrol_', '')] = valueControl.text()

            build_result = cqModel.build(build_parameters=build_parameters)

            # if Settings.report_execute_time:
            #     FreeCAD.Console.PrintMessage("Script executed in " + str(build_result.buildTime) + " seconds\r\n")

            # Make sure that the build was successful
            if build_result.success:
                # Display all the results that the user requested
                for result in build_result.results:
                    # Apply options to the show function if any were provided
                    if result.options and result.options["rgba"]:
                        show(result.shape, result.options["rgba"])
                    else:
                        show(result.shape)

                for debugObj in build_result.debugObjects:
                    # Mark this as a debug object
                    debugObj.shape.val().label = "Debug" + str(random())

                    # Apply options to the show function if any were provided
                    if debugObj.options and debugObj.options["rgba"]:
                        show(debugObj.shape, debugObj.options["rgba"])
                    else:
                        show(debugObj.shape, (255, 0, 0, 0.80))
            else:
                FreeCAD.Console.PrintError("Error executing CQGI-compliant script. " + str(build_result.exception) + "\r\n")
        else:
            # Save our code to a tempfile and render it
            tempFile = tempfile.NamedTemporaryFile(delete=False)
            tempFile.write(scriptText)
            tempFile.close()

            # Set some environment variables that may help the user
            os.environ["MYSCRIPT_FULL_PATH"] = cqCodePane.get_path()
            os.environ["MYSCRIPT_DIR"] = os.path.dirname(os.path.abspath(cqCodePane.get_path()))

            # We import this way because using execfile() causes non-standard script execution in some situations
            with revert_sys_modules():
                imp.load_source('__cq_freecad_module__', tempFile.name)

        msg = QtGui.QApplication.translate(
            "cqCodeWidget",
            "Executed ",
            None)
        FreeCAD.Console.PrintMessage(msg + cqCodePane.get_path() + "\r\n")


class CadQueryHelp:
    """Opens a help dialog, allowing the user to access documentation and information about CadQuery"""

    def GetResources(self):
        return {"MenuText": "Help",
                "Accel": "",
                "ToolTip": "Opens the Help dialog",
                "Pixmap": ":/icons/preferences-general.svg"}

    def IsActive(self):
        return True

    def Activated(self):
        win = HelpDialog()

        win.exec_()
