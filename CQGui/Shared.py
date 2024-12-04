# (c) 2014-2024 CadQuery Developers Apache 2.0 License
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
