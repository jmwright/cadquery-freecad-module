import FreeCAD
import FreeCADGui
from PySide import QtGui


def clearActiveDocument():
    """Clears the currently active 3D view so that we can re-render"""

    # Grab our code editor so we can interact with it
    mw = FreeCADGui.getMainWindow()
    mdi = mw.findChild(QtGui.QMdiArea)
    currentWin = mdi.currentSubWindow()
    if currentWin == None:
        return
    winName = currentWin.windowTitle().split(" ")[0].split('.')[0]

    # Translate dashes so that they can be safetly used since theyare common
    if '-' in winName:
        winName= winName.replace('-', "__")

    try:
        doc = FreeCAD.getDocument(winName)

        # Make sure we have an active document to work with
        if doc is not None:
            for obj in doc.Objects:
                doc.removeObject(obj.Name)
    except:
        pass


def getActiveCodePane():
    """Gets the currently active code pane, even if its 3D view is selected."""

    # Grab our code editor so we can interact with it
    mw = FreeCADGui.getMainWindow()
    mdi = mw.findChild(QtGui.QMdiArea)

    # If our current subwindow doesn't contain a script, we need to find the one that does
    mdiWin = mdi.currentSubWindow()
    if mdiWin == None: return None # We need to warn the caller that there is no code pane

    windowTitle = mdiWin.windowTitle()

    if mdiWin == 0 or ".py" not in mdiWin.windowTitle():
        if '__' in mdiWin.windowTitle():
            windowTitle = mdiWin.windowTitle().replace("__", '-')

        subList = mdi.subWindowList()

        for sub in subList:
            if sub.windowTitle() == windowTitle.split(" ")[0] + ".py":
                mdiWin = sub

    winName = mdiWin.windowTitle().split('.')[0]
    cqCodePane = mw.findChild(QtGui.QPlainTextEdit, "cqCodePane_" + winName)

    return cqCodePane


def closeActiveCodeWindow():
    mw = FreeCADGui.getMainWindow()
    mdi = mw.findChild(QtGui.QMdiArea)

    # We cannot trust the current subwindow to be a script window, it may be the associated 3D view
    mdiWin = mdi.currentSubWindow()

    # We have a 3D view selected so we need to find the corresponding script window
    if mdiWin == 0 or ".py" not in mdiWin.windowTitle():
        subList = mdi.subWindowList()

        for sub in subList:
            if sub.windowTitle() == mdiWin.windowTitle().split(" ")[0] + ".py":
                sub.close()
                return

    mdiWin.close()

def setActiveWindowTitle(title):
    """Sets the title of the currently active MDI window, as long as it is a scripting window"""

    mw = FreeCADGui.getMainWindow()
    mdi = mw.findChild(QtGui.QMdiArea)

    # We cannot trust the current subwindow to be a script window, it may be the associated 3D view
    mdiWin = mdi.currentSubWindow()

    if mdiWin == 0 or ".py" not in mdiWin.windowTitle():
        subList = mdi.subWindowList()

        for sub in subList:
            if sub.windowTitle() == mdiWin.windowTitle() + ".py":
                mdiWin = sub

    # Change the window title if there is something there to change
    if (mdiWin != 0):
        mdiWin.setWindowTitle(title)

        cqCodePane = mdiWin.findChild(QtGui.QPlainTextEdit)
        cqCodePane.setObjectName("cqCodePane_" + title.split('.')[0])


def populateParameterEditor(parameters):
    """Puts the proper controls in the script variable editor pane based on the parameters found"""

    FreeCAD.Console.PrintMessage("Script Variables:\r\n")

    mw = FreeCADGui.getMainWindow()

    # If the widget is open, we need to close it
    dockWidgets = mw.findChildren(QtGui.QDockWidget)
    for widget in dockWidgets:
        if widget.objectName() == "cqVarsEditor":
            gridLayout = QtGui.QGridLayout()

            line = 1

            # Add controls for all the parameters so that they can be edited from the GUI
            for pKey, pVal in parameters.iteritems():
                label = QtGui.QLabel(pKey)

                # We want to keep track of this parameter value field so that we can pull its value later when executing
                value = QtGui.QLineEdit()
                value.setText(str(pVal.default_value))
                value.setObjectName("pcontrol_" + pKey)

                # Add the parameter control sets, one set per line
                gridLayout.addWidget(label, line, 0)
                gridLayout.addWidget(value, line, 1)

                line += 1

            # Create a widget we can put the layout in and add a scrollbar
            newWidget = QtGui.QWidget()
            newWidget.setLayout(gridLayout)

            # Add a scroll bar in case there are a lot of variables in the script
            scrollArea = QtGui.QScrollArea()
            scrollArea.setBackgroundRole(QtGui.QPalette.Light)
            scrollArea.setStyleSheet("QLabel { color : black; }");
            scrollArea.setWidget(newWidget)

            widget.setWidget(scrollArea)