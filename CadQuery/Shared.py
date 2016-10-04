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
    # Grab our code editor so we can interact with it
    mw = FreeCADGui.getMainWindow()
    mdi = mw.findChild(QtGui.QMdiArea)
    winName = mdi.currentSubWindow().windowTitle().split('.')[0]
    cqCodePane = mw.findChild(QtGui.QPlainTextEdit, "cqCodePane_" + winName)

    return cqCodePane