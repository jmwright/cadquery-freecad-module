import FreeCAD
from PySide import QtGui, QtCore

class SettingsDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.resize(200, 150)
        self.setWindowTitle('Settings')
        self.initUI()

    def initUI(self):
        fontSize = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/cadquery-freecad-module").GetInt("fontSize")
        keybinding = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/cadquery-freecad-module").GetString("executeKeybinding")
        executeOnSave = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/cadquery-freecad-module").GetBool("executeOnSave")
        showLineNumbers = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/cadquery-freecad-module").GetBool("showLineNumbers")
        allowReload = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/cadquery-freecad-module").GetBool("allowReload")

        font_size = QtGui.QLabel('Font Size')
        self.ui_font_size = QtGui.QSpinBox()
        self.ui_font_size.setValue(fontSize)

        key_binding = QtGui.QLabel('Execute Key-binding')
        self.ui_key_binding = QtGui.QLineEdit()
        self.ui_key_binding.setText(keybinding)

        execute_on_save = QtGui.QLabel('Execute on Save')
        self.execute_on_save = QtGui.QCheckBox()
        self.execute_on_save.setChecked(executeOnSave)

        show_line_numbers = QtGui.QLabel('Show Line Numbers')
        self.show_line_numbers = QtGui.QCheckBox()
        self.show_line_numbers.setChecked(showLineNumbers)

        allow_reload = QtGui.QLabel('Allow Reload')
        self.allow_reload = QtGui.QCheckBox()
        self.allow_reload.setChecked(allowReload)

        self.buttons = QtGui.QDialogButtonBox()
        self.buttons.setOrientation(QtCore.Qt.Horizontal)
        self.buttons.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)
        self.buttons.layout().setDirection(QtGui.QBoxLayout.LeftToRight)
        self.buttons.accepted.connect(self.acceptSettings)
        self.buttons.rejected.connect(self.reject)

        grid = QtGui.QGridLayout()
        grid.setContentsMargins(10, 10, 10, 10)
        grid.addWidget(font_size, 0, 0)
        grid.addWidget(self.ui_font_size, 0, 1)
        grid.addWidget(key_binding, 1, 0)
        grid.addWidget(self.ui_key_binding, 1, 1)
        grid.addWidget(execute_on_save, 2, 0)
        grid.addWidget(self.execute_on_save, 2, 1)
        grid.addWidget(show_line_numbers, 3, 0)
        grid.addWidget(self.show_line_numbers, 3, 1)
        grid.addWidget(allow_reload, 4, 0)
        grid.addWidget(self.allow_reload, 4, 1)
        grid.addWidget(self.buttons, 5, 1)

        self.setLayout(grid)

    @QtCore.Slot(int)
    def acceptSettings(self):
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/cadquery-freecad-module").SetInt("fontSize", self.ui_font_size.value())
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/cadquery-freecad-module").SetString("executeKeybinding", self.ui_key_binding.text())
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/cadquery-freecad-module").SetBool("executeOnSave", self.execute_on_save.checkState())
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/cadquery-freecad-module").SetBool("showLineNumbers", self.show_line_numbers.checkState())
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/cadquery-freecad-module").SetBool("allowReload", self.allow_reload.checkState())

        self.accept()

    # def getValues(self):
    #     return {
    #         'max': self.ui_max.value(),
    #         'min': self.ui_min.value(),
    #         'count': self.ui_count.value(),
    #         }

    # def setValues(self, settings):
    #     self.ui_max.setValue(settings['max'])
    #     self.ui_min.setValue(settings['min'])
    #     self.ui_count.setValue(settings['count'])
