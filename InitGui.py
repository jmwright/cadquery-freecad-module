"""CadQuery GUI init module for FreeCAD
   This adds a workbench with a scripting editor to FreeCAD's GUI."""
# (c) 2014-2023 Jeremy Wright LGPL 3.0 License
import FreeCAD, FreeCADGui
# try:
#     from CadQuery.CQGui.Command import *
# except:
#     from CQGui.Command import *
# import CadQuery_rc

class CadQueryWorkbench (Workbench):
    """CadQuery workbench for FreeCAD"""
    """CadQuery workbench for FreeCAD"""
    import os

    # The the current version of CadQuery that the user wants to run
    cq_version = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/cadquery-freecad-module").GetInt("cqMajorVersion")
    
    MenuText = "CadQuery"
    ToolTip = "CadQuery workbench"
    Icon = FreeCAD.getUserAppDataDir() + "Mod/cadquery-freecad-module/CQGui/Resources/icons/CQ_Logo.svg"

    #Keeps track of which workbenches we have hidden so we can reshow them
    closedWidgets = []

    def Initialize(self):
        #Turn off logging for now
        #import logging
        #logging.basicConfig(filename='C:\\Users\\Jeremy\\Documents\\', level=logging.DEBUG)
        #logging.basicConfig(filename='/home/jwright/Documents/log.txt', level=logging.DEBUG)

        # See if CadQuery needs to be installed
        try:
            import cadquery
        except:
            from PySide import QtGui
            msg_box = QtGui.QMessageBox()
            msg_box.setText("The cadquery Python module is not installed. Without it this workbench will not work correctly.")
            msg_box.setInformativeText("Would you like to install it?")
            msg_box.addButton(QtGui.QMessageBox.Yes)
            msg_box.addButton(QtGui.QMessageBox.No)
            msg_box.addButton(QtGui.QMessageBox.Cancel)
            msg_box.setDefaultButton(QtGui.QMessageBox.Yes)
            ret = msg_box.exec_()

            # See how the user responded
            if ret == msg_box.Yes:
                FreeCAD.Console.PrintMessage("Installing cadquery module.\r\n")
                import subprocess as subp
                import shutil

                # Get the currently used Python binary
                python_bin = shutil.which('python')

                venv_dir = FreeCAD.getUserAppDataDir() + "Mod/cadquery-freecad-module/venv"
                proc = subp.Popen([python_bin, "-m", "venv", venv_dir], stdout=subp.PIPE, stderr=subp.PIPE)
                proc = subp.Popen(["sh", venv_dir + "/bin/activate"], stdout=subp.PIPE, stderr=subp.PIPE)
                # proc = subp.Popen([python_bin, "-m", "pip", "uninstall", "-y", "cadquery"], stdout=subp.PIPE, stderr=subp.PIPE)
                # proc = subp.Popen([python_bin, "-m", "pip", "install", "--upgrade", "pip"], stdout=subp.PIPE, stderr=subp.PIPE)
                # proc = subp.Popen([python_bin, "-m", "pip", "install", "--upgrade", "numpy"], stdout=subp.PIPE, stderr=subp.PIPE)
                proc = subp.Popen([python_bin, "-m", "pip", "install", "cadquery", "--user"], stdout=subp.PIPE, stderr=subp.PIPE)
                out, err = proc.communicate()
                FreeCAD.Console.PrintMessage(out.decode("utf8"))
                # if err != None:
                FreeCAD.Console.PrintMessage("CadQuery install error: " + err.decode("utf8"))

            return

        submenu = []

        dirs = self.ListExamples()

        # Step through and add an Examples submenu item for each example
        for curFile in dirs:
            submenu.append(str(curFile))

        #We have our own CQ menu that's added when the user chooses our workbench
        self.appendMenu('CadQuery', ['CadQueryNewScript', 'CadQueryOpenScript', 'CadQuerySaveScript',
                                     'CadQuerySaveAsScript', 'CadQueryCloseScript'])
        self.appendMenu(['CadQuery', 'Examples'], submenu)
        self.appendMenu('CadQuery', ['Separator', 'CadQueryExecuteScript', 'CadQueryValidateScript', 'ToggleVariablesEditor', 'CadQueryClearOutput'])
        self.appendMenu('CadQuery', ['Separator', 'CadQuerySettings'])

    def Activated(self):
        import os
        # try:
        #     from . import module_locator
        # except:
        #     import module_locator
        # try:
        #     from CadQuery.CQGui import ImportCQ
        # except:
        #     from CQGui import ImportCQ

        # module_base_path = module_locator.module_path()

        # See if CadQuery needs to be installed
        try:
            import cadquery
        except:
            return

        import cadquery
        from CQGui import ImportCQ
        from PySide import QtGui, QtCore

        msg = QtGui.QApplication.translate(
            "cqCodeWidget",
            "CadQuery " + cadquery.__version__ + "\r\n"
            "CadQuery is a parametric scripting API "
            "for creating and traversing CAD models\r\n"
            "Author: David Cowden\r\n"
            "License: Apache-2.0\r\n"
            "Website: https://github.com/dcowden/cadquery\r\n",
            None)
        FreeCAD.Console.PrintMessage(msg)

        #Getting the main window will allow us to start setting things up the way we want
        mw = FreeCADGui.getMainWindow()

        dockWidgets = mw.findChildren(QtGui.QDockWidget)

        for widget in dockWidgets:
            if widget.objectName() == "Report view":
                widget.setVisible(True)

        # Set up the paths to allow us to open the template
        # template_path = os.path.join(module_base_path, 'Templates')
        # template_path = os.path.join(template_path, 'script_template.py')
        #
        # ImportCQ.open(template_path)

    def AutoExecute(self):
        """We should be able to pass the CQGui.Commands.CadQueryExecuteScript function directly to the file_reloaded
           connect function, but that causes a segfault in FreeCAD. This function is a work-around for that. This
           function is passed to file_reloaded signal and in turn calls the CadQueryExecuteScript.Activated function."""
        try:
            import CadQuery.CQGui.Command
            CadQuery.CQGui.Command.CadQueryExecuteScript().Activated()
        except:
            from CQGui import ImportCQ
            CQGui.Command.CadQueryExecuteScript().Activated()


    def Deactivated(self):
        pass

    @staticmethod
    def ListExamples():
        import os
        try:
            from . import module_locator
        except:
            import module_locator

        dirs = []

        # List all of the example files in an order that makes sense
        module_base_path = module_locator.module_path()
        exs_dir_path = os.path.join(module_base_path, 'Libs/cadquery/examples/FreeCAD')
        dirs = os.listdir(exs_dir_path)
        dirs.sort()

        return dirs

# FreeCADGui.addCommand('CadQueryNewScript', CadQueryNewScript())
# FreeCADGui.addCommand('CadQueryOpenScript', CadQueryOpenScript())
# FreeCADGui.addCommand('CadQuerySaveScript', CadQuerySaveScript())
# FreeCADGui.addCommand('CadQuerySaveAsScript', CadQuerySaveAsScript())
# FreeCADGui.addCommand('CadQueryExecuteScript', CadQueryExecuteScript())
# FreeCADGui.addCommand('CadQueryValidateScript', CadQueryValidateScript())
# FreeCADGui.addCommand('CadQueryCloseScript', CadQueryCloseScript())
# FreeCADGui.addCommand('ToggleVariablesEditor', ToggleParametersEditor())
# FreeCADGui.addCommand('CadQueryClearOutput', CadQueryClearOutput())
# FreeCADGui.addCommand('CadQuerySettings', CadQuerySettings())

# Step through and add an Examples submenu item for each example
# dirs = CadQueryWorkbench.ListExamples()
# for curFile in dirs:
#     FreeCADGui.addCommand(curFile, CadQueryOpenExample(curFile))

FreeCADGui.addWorkbench(CadQueryWorkbench())
