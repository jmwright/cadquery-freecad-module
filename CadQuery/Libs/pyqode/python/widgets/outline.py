"""
This document contains the tree widget used to display the editor document
outline.

"""
from pyqode.core.panels import FoldingPanel
from pyqode.python.modes import DocumentAnalyserMode
from pyqode.qt import QtCore, QtGui, QtWidgets
from pyqode.core.api import TextBlockHelper, TextHelper, TextBlockUserData


class PyOutlineTreeWidget(QtWidgets.QTreeWidget):
    """
    Displays the outline of a PyCodeEdit. The treeview is fully synced with
    the fold panel.

    To use the widget, you just have to set the active editor using
    :func:`PyOutlineTreeWidget.set_editor`.

    """
    def __init__(self, parent=None):
        super(PyOutlineTreeWidget, self).__init__(parent)
        self._editor = None
        self._analyser = None
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

        :param editor: PyCodeEdit
        """
        if self._analyser:
            try:
                self._analyser.document_changed.disconnect(self._on_changed)
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
                analyser = editor.modes.get(DocumentAnalyserMode)
            except KeyError:
                self._analyser = None
            else:
                assert isinstance(analyser, DocumentAnalyserMode)
                self._analyser = analyser
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
        if self._editor and self._analyser and self._folding_panel:
            items, to_collapse = self._analyser.to_tree_widget_items(
                to_collapse=to_collapse)
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
