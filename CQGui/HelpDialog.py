from PySide import QtGui, QtCore

class HelpDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(HelpDialog, self).__init__(parent)
        self.resize(300, 200)
        self.setWindowTitle('Help')
        self.initUI()

    def initUI(self):
        import cadquery

        # Introduction to CadQuery line
        intro_label = QtGui.QLabel('CadQuery is a parametric scripting API for creating CAD models and assemblies.')
        intro_label.setWordWrap(True)

        # CadQuery version
        cadquery_ver = cadquery.__version__
        version_label = QtGui.QLabel('CadQuery Version: ' + cadquery_ver)

        # CadQuery contributors
        cq_contribs = QtGui.QLabel('Authors: CadQuery Developers')

        # CadQuery documentation link
        cq_docs_link = QtGui.QLabel('- <a href="https://cadquery.readthedocs.io">CadQuery Documentation</a>')
        cq_docs_link.setOpenExternalLinks(True)

        # FreeCAD workbench documentation link
        wb_docs_link = QtGui.QLabel('- <a href="https://github.com/CadQuery/freecad-cadquery-module/docs">Workbench Documentation</a>')
        wb_docs_link.setOpenExternalLinks(True)

        self.buttons = QtGui.QDialogButtonBox()
        self.buttons.setOrientation(QtCore.Qt.Horizontal)
        self.buttons.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttons.layout().setDirection(QtGui.QBoxLayout.LeftToRight)
        self.buttons.accepted.connect(self.closeHelp)

        grid = QtGui.QGridLayout()
        grid.setContentsMargins(10, 10, 10, 10)
        grid.addWidget(intro_label, 0, 0)
        grid.addWidget(version_label, 1, 0)
        grid.addWidget(cq_contribs, 2, 0)
        grid.addWidget(cq_docs_link, 3, 0)
        grid.addWidget(wb_docs_link, 4, 0)
        grid.addWidget(self.buttons, 5, 0)

        self.setLayout(grid)

    @QtCore.Slot(int)
    def closeHelp(self):
        self.accept()
