# -*- coding: utf-8 -*-
import logging
from pyqode.core import api
from pyqode.core.api import Mode, TextBlockUserData, TextBlockHelper
from pyqode.core.api import DelayJobRunner
from pyqode.core.backend import NotRunning
from pyqode.python.backend.workers import Definition, defined_names
from pyqode.qt import QtCore, QtGui, QtWidgets


def _logger():
    return logging.getLogger(__name__)


class DocumentAnalyserMode(Mode, QtCore.QObject):
    """ Analyses the document outline as a tree of statements.

    This mode analyses the structure of a document (a tree of
    :class:`pyqode.python.backend.workers.Definition`.

    :attr:`pyqode.python.modes.DocumentAnalyserMode.document_changed`
    is emitted whenever the document structure changed.

    To keep good performances, the analysis task is run when the application is
    idle for more than 1 second (by default).
    """
    #: Signal emitted when the document structure changed.
    document_changed = QtCore.Signal()

    def __init__(self, delay=1000):
        Mode.__init__(self)
        QtCore.QObject.__init__(self)
        self._jobRunner = DelayJobRunner(delay=delay)
        #: The list of results (elements might have children; this is actually
        #: a tree).
        self.results = []

    def on_state_changed(self, state):
        if state:
            self.editor.new_text_set.connect(self._run_analysis)
            self.editor.textChanged.connect(self._request_analysis)
        else:
            self.editor.textChanged.disconnect(self._request_analysis)
            self.editor.new_text_set.disconnect(self._run_analysis)
            self._jobRunner.cancel_requests()

    def _request_analysis(self):
        self._jobRunner.request_job(self._run_analysis)

    def _run_analysis(self):
        if self.enabled and self.editor and self.editor.toPlainText() and \
                self.editor.file:
            request_data = {
                'code': self.editor.toPlainText(),
                'path': self.editor.file.path,
                'encoding': self.editor.file.encoding
            }
            try:
                self.editor.backend.send_request(
                    defined_names, request_data,
                    on_receive=self._on_results_available)
            except NotRunning:
                QtCore.QTimer.singleShot(100, self._run_analysis)
        else:
            self.results = []
            self.document_changed.emit()

    def _on_results_available(self, results):
        if results:
            results = [Definition().from_dict(ddict) for ddict in results]
        self.results = results
        if self.results is not None:
            _logger().debug("Document structure changed")
            self.document_changed.emit()

    @property
    def flattened_results(self):
        """
        Flattens the document structure tree as a simple sequential list.
        """
        ret_val = []
        for d in self.results:
            ret_val.append(d)
            for sub_d in d.children:
                nd = Definition(sub_d.name, sub_d.icon, sub_d.line,
                                sub_d.column, sub_d.full_name)
                nd.name = "  " + nd.name
                nd.full_name = "  " + nd.full_name
                ret_val.append(nd)
        return ret_val

    def to_tree_widget_items(self, to_collapse=None):
        """
        Returns the results as a list of top level QTreeWidgetItem.

        This is a convenience function that you can use to update a document
        tree widget wheneve the document changed.
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
        for d in self.results:
            value, to_collapse = convert(d, self.editor, to_collapse)
            items.append(value)
        if to_collapse is not None:
            return items, to_collapse
        return items
