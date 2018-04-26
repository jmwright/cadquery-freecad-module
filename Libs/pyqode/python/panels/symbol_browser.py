# -*- coding: utf-8 -*-
"""
SymbolBrowserPanel
"""
import logging
from pyqode.core.api import Panel, TextHelper
from pyqode.qt import QtGui, QtCore, QtWidgets
from pyqode.core.share import Definition


def _logger():
    return logging.getLogger(__name__)


class SymbolBrowserPanel(Panel):
    """ Shows a combo box with the definitions found in the document.

    Allow quick navigation in the file and sync with the cursor
    position.
    """

    def __init__(self):
        super(SymbolBrowserPanel, self).__init__()
        self._prevLine = -1
        self._definitions = []
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.combo_box = QtWidgets.QComboBox()
        self.combo_box.setSizeAdjustPolicy(
            self.combo_box.AdjustToMinimumContentsLength)
        self.combo_box.activated.connect(self._on_definition_activated)
        layout.addWidget(self.combo_box)
        self.setLayout(layout)
        self.combo_box.addItem("Loading symbols...")

    def on_state_changed(self, state):
        super(SymbolBrowserPanel, self).on_state_changed(state)
        if state:
            self.editor.cursorPositionChanged.connect(
                self._on_cursor_pos_changed)
            try:
                self.editor.modes.get(
                    'OutlineMode').document_changed.connect(
                        self._on_document_changed)
            except KeyError:
                _logger().warning("No OutlineMode found, install it "
                                  "before SymbolBrowserPanel!")
        else:
            self.editor.cursorPositionChanged.disconnect(
                self._on_cursor_pos_changed)
            try:
                self.editor.modes.get(
                    'OutlineMode').document_changed.disconnect(
                        self._on_document_changed)
            except KeyError:
                pass

    def _on_document_changed(self):
        def flatten(results):
            """
            Flattens the document structure tree as a simple sequential list.
            """
            ret_val = []
            for de in results:
                ret_val.append(de)
                for sub_d in de.children:
                    nd = Definition(
                        sub_d.name, sub_d.line, sub_d.column, sub_d.icon)
                    nd.name = "    " + nd.name
                    ret_val.append(nd)
            return ret_val

        if not self or not self.editor:
            return
        mode = self.editor.modes.get('OutlineMode')
        definitions = flatten(mode.definitions)
        self.combo_box.clear()
        if definitions:
            self.combo_box.addItem(" < Select a symbol >")
        else:
            self.combo_box.addItem("No symbols")
        for d in definitions:
            try:
                self.combo_box.addItem(QtGui.QIcon(d.icon), d.name, d)
            except TypeError:
                self.combo_box.addItem(QtGui.QIcon.fromTheme(
                    d.icon[0], QtGui.QIcon(d.icon[1])), d.name, d)
        self._definitions = definitions
        self._sync_combo_box(TextHelper(self.editor).current_line_nbr())

    def _on_definition_activated(self, index):
        definition = self.combo_box.itemData(index)
        if definition:
            TextHelper(self.editor).goto_line(
                definition.line, column=definition.column)
            self.editor.setFocus()

    def _sync_combo_box(self, line):
        i = -1
        for i, d in enumerate(reversed(self._definitions)):
            if d.line <= line:
                break
        if i >= 0:
            index = len(self._definitions) - i
            self.combo_box.setCurrentIndex(index)

    def _on_cursor_pos_changed(self):
        line = TextHelper(self.editor).current_line_nbr()
        if self._prevLine != line:
            self._sync_combo_box(line)
        self._prevLine = line
