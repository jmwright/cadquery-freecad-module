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
