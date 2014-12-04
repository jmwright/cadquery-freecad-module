# -*- coding: utf-8 -*-
"""
Contains the JediCompletionProvider class implementation.
"""
import logging
import os
from pyqode.core.api import Mode, TextHelper
from pyqode.python.backend import workers
from pyqode.qt import QtCore, QtWidgets


def _logger():
    return logging.getLogger(__name__)


class CalltipsMode(Mode, QtCore.QObject):
    """ Shows function calltips.

    This mode shows function/method call tips in a QToolTip using
    :meth:`jedi.Script.call_signatures`.
    """
    tooltipDisplayRequested = QtCore.Signal(object, int)
    tooltipHideRequested = QtCore.Signal()

    def __init__(self):
        Mode.__init__(self)
        QtCore.QObject.__init__(self)
        self.tooltipDisplayRequested.connect(self._display_tooltip)
        self.tooltipHideRequested.connect(QtWidgets.QToolTip.hideText)
        self.__requestCnt = 0

    def on_state_changed(self, state):
        if state:
            self.editor.key_released.connect(self._on_key_released)

    def _on_key_released(self, event):
        if (event.key() == QtCore.Qt.Key_ParenLeft or
                event.key() == QtCore.Qt.Key_Comma):
            tc = self.editor.textCursor()
            line = tc.blockNumber()
            col = tc.columnNumber()
            fn = self.editor.file.path
            encoding = self.editor.file.encoding
            source = self.editor.toPlainText()
            # jedi has a bug if the statement has a closing parenthesis
            # remove it!
            lines = source.splitlines()
            l = lines[line].rstrip()
            if l.endswith(")"):
                lines[line] = l[:-1]
            source = "\n".join(lines)
            self._request_calltip(source, line, col, fn, encoding)
        elif (event.key() in [
                QtCore.Qt.Key_ParenRight,
                QtCore.Qt.Key_Return,
                QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete]):
            QtWidgets.QToolTip.hideText()

    def _request_calltip(self, source, line, col, fn, encoding):
        if self.__requestCnt == 0:
            self.__requestCnt += 1
            _logger().debug("Calltip requested")
            self.editor.backend.send_request(
                workers.calltips,
                {'code': source, 'line': line, 'column': col, 'path': None,
                 'encoding': encoding}, on_receive=self._on_results_available)

    def _on_results_available(self, results):
        _logger().debug("Calltip request finished")
        self.__requestCnt -= 1
        if results:
            call = {"call.module.name": results[0],
                    "call.call_name": results[1],
                    "call.params": results[2],
                    "call.index": results[3],
                    "call.bracket_start": results[4]}
            self.tooltipDisplayRequested.emit(call, results[5])

    def _is_last_chard_end_of_word(self):
        try:
            tc = TextHelper(self.editor).word_under_cursor()
            tc.setPosition(tc.position())
            tc.movePosition(tc.StartOfLine, tc.KeepAnchor)
            l = tc.selectedText()
            last_char = l[len(l) - 1]
            seps = self.editor.word_separators
            symbols = [",", " ", "("]
            return last_char in seps and last_char not in symbols
        except IndexError:
            return False

    def _display_tooltip(self, call, col):
        if not call or self._is_last_chard_end_of_word():
            return
        # create a formatted calltip (current index appear in bold)
        calltip = "<nobr>{0}.{1}(".format(call['call.module.name'],
                                          call['call.call_name'])
        for i, param in enumerate(call['call.params']):
            if i != 0:
                calltip += ", "
            if i == call['call.index']:
                calltip += "<b>"
            calltip += param
            if i == call['call.index']:
                calltip += "</b>"
        calltip += ')</nobr>'
        # set tool tip position at the start of the bracket
        char_width = self.editor.fontMetrics().width('A')
        w_offset = (col - call['call.bracket_start'][1]) * char_width
        position = QtCore.QPoint(
            self.editor.cursorRect().x() - w_offset,
            self.editor.cursorRect().y() + char_width +
            self.editor.panels.margin_size(0))
        position = self.editor.mapToGlobal(position)
        # show tooltip
        QtWidgets.QToolTip.showText(position, calltip, self.editor)
