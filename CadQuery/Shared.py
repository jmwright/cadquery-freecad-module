import FreeCAD
import FreeCADGui
from PySide import QtGui


def clearActiveDocument():
    """Clears the currently active 3D view so that we can re-render"""

    # Grab our code editor so we can interact with it
    mw = FreeCADGui.getMainWindow()
    mdi = mw.findChild(QtGui.QMdiArea)
    winName = mdi.currentSubWindow().windowTitle().split('.')[0]

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

    # TODO: Make sure that the code pane is selected, even if the associated 3D view currently has focus

    # Grab our code editor so we can interact with it
    mw = FreeCADGui.getMainWindow()
    mdi = mw.findChild(QtGui.QMdiArea)

    # If our current subwindow doesn't contain a script, we need to find the one that does
    mdiWin = mdi.currentSubWindow()
    if mdiWin == 0 or ".py" not in mdiWin.windowTitle():
        subList = mdi.subWindowList()

        for sub in subList:
            print(sub.windowTitle())
            if sub.windowTitle() == mdiWin.windowTitle().split(" ")[0] + ".py":
                mdiWin = sub

    winName = mdiWin.windowTitle().split('.')[0]
    cqCodePane = mw.findChild(QtGui.QPlainTextEdit, "cqCodePane_" + winName)

    return cqCodePane


def getActiveCodeWindow():
    """Gets the currently active code window (that holds the pane), even if the associated 3D view window has focus"""

    mw = FreeCADGui.getMainWindow()
    mdi = mw.findChild(QtGui.QMdiArea)

    # We cannot trust the current subwindow to be a script window, it may be the associated 3D view
    mdiWin = mdi.currentSubWindow()

    # We have a 3D view selected so we need to find the corresponding script window
    if mdiWin == 0 or ".py" not in mdiWin.windowTitle():
        subList = mdi.subWindowList()

        for sub in subList:
            if sub.windowTitle() == mdiWin.windowTitle() + ".py":
                mdiWin = sub

    return mdiWin


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