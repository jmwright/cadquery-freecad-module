"""
This document contains the tree widget used to display the editor document
outline.

"""
from pyqode.core.panels import FoldingPanel
from pyqode.core.modes.outline import OutlineMode
from pyqode.qt import QtCore, QtGui, QtWidgets
from pyqode.core.api import TextBlockHelper, TextBlockUserData, TextHelper


class OutlineTreeWidget(QtWidgets.QTreeWidget):
    """
    Displays the outline of a CodeEdit.

    To use this widget:

    1. add an OutlineMode to CodeEdit
    2. call set_editor with a CodeEdit instance to show it's outline.

    """
    def __init__(self, parent=None):
        super(OutlineTreeWidget, self).__init__(parent)
        self._editor = None
        self._outline_mode = None
        self._folding_panel = None
        self._expanded_items = []
        self.setHeaderHidden(True)
        self.itemClicked.connect(self._on_item_clicked)
        self.itemCollapsed.connect(self._on_item_state_changed)
        self.itemExpanded.connect(self._on_item_state_changed)
        self._updating = True

    def set_editor(self, editor):
        """
        Sets the current editor. The widget display the structure of that
        editor.

        :param editor: CodeEdit
        """
        if self._outline_mode:
            try:
                self._outline_mode.document_changed.disconnect(self._on_changed)
            except (TypeError, RuntimeError):
                pass
        if self._folding_panel:
            try:
                self._folding_panel.trigger_state_changed.disconnect(
                    self._on_block_state_changed)
            except (TypeError, RuntimeError):
                pass
        self._editor = editor
        if self._editor is not None:
            try:
                self._folding_panel = editor.panels.get(FoldingPanel)
            except KeyError:
                pass
            else:
                self._folding_panel.trigger_state_changed.connect(
                    self._on_block_state_changed)
            try:
                analyser = editor.modes.get(OutlineMode)
            except KeyError:
                self._outline_mode = None
            else:
                self._outline_mode = analyser
                analyser.document_changed.connect(self._on_changed)
        self._on_changed()

    def _on_item_state_changed(self, item):
        if self._updating:
            return
        block = item.data(0, QtCore.Qt.UserRole).block
        assert isinstance(item, QtWidgets.QTreeWidgetItem)
        item_state = not item.isExpanded()
        block_state = TextBlockHelper.get_fold_trigger_state(block)
        if item_state != block_state:
            self._updating = True
            self._folding_panel.toggle_fold_trigger(block)
            self._updating = False

    def _on_block_state_changed(self, block, state):
        if self._updating:
            return
        data = block.userData()
        if data is not None:
            try:
                item_state = not data.tree_item.isExpanded()
                if item_state != state:
                    if state:
                        self.collapseItem(data.tree_item)
                    else:
                        self.expandItem(data.tree_item)
            except AttributeError:
                # a block that is not represented in the tree view has
                # folded/unfolded, just ignore it
                pass

    def _on_changed(self):
        """
        Update the tree items
        """
        self._updating = True
        to_collapse = []
        self.clear()
        if self._editor and self._outline_mode and self._folding_panel:
            items, to_collapse = self.to_tree_widget_items(
                self._outline_mode.definitions, to_collapse=to_collapse)
            if len(items):
                self.addTopLevelItems(items)
                self.expandAll()
                for item in reversed(to_collapse):
                    self.collapseItem(item)
                self._updating = False
                return

        # no data
        root = QtWidgets.QTreeWidgetItem()
        root.setText(0, 'No data')
        root.setIcon(0, QtGui.QIcon.fromTheme(
            'dialog-information',
            QtGui.QIcon(':/pyqode-icons/rc/dialog-info.png')))
        self.addTopLevelItem(root)
        self._updating = False

    def _on_item_clicked(self, item):
        """
        Go to the item position in the editor.
        """
        if item:
            name = item.data(0, QtCore.Qt.UserRole)
            if name:
                go = name.block.blockNumber()
                helper = TextHelper(self._editor)
                if helper.current_line_nbr() != go:
                    helper.goto_line(go, column=name.column)
                self._editor.setFocus()

    def to_tree_widget_items(self, definitions, to_collapse=None):
        """
        Converts the list of top level definitions to a list of top level
        tree items.
        """
        def convert(name, editor, to_collapse):
            ti = QtWidgets.QTreeWidgetItem()
            ti.setText(0, name.name)
            ti.setIcon(0, QtGui.QIcon(name.icon))
            name.block = editor.document().findBlockByNumber(name.line)
            ti.setData(0, QtCore.Qt.UserRole, name)
            block_data = name.block.userData()
            if block_data is None:
                block_data = TextBlockUserData()
                name.block.setUserData(block_data)
            block_data.tree_item = ti

            if to_collapse is not None and \
                    TextBlockHelper.get_fold_trigger_state(name.block):
                to_collapse.append(ti)

            for ch in name.children:
                ti_ch, to_collapse = convert(ch, editor, to_collapse)
                if ti_ch:
                    ti.addChild(ti_ch)
            return ti, to_collapse

        items = []
        for d in definitions:
            value, to_collapse = convert(d, self._editor, to_collapse)
            items.append(value)
        if to_collapse is not None:
            return items, to_collapse
        return items
