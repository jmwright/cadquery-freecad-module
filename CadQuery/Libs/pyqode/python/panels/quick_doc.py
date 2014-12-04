# -*- coding: utf-8 -*-
"""
Contains the quick documentation panel
"""
from docutils.core import publish_parts
from pyqode.qt import QtCore, QtGui, QtWidgets
from pyqode.core.api import Panel, TextHelper
from pyqode.python.backend.workers import quick_doc


class QuickDocPanel(Panel):
    """ Shows the python documentation for the word under the text cursor.

    This panel quickly shows the documentation of the symbol under
    cursor.
    """
    STYLESHEET = '''
    QTextEdit
    {
        background-color: %s;
        color: %s;
    }
    '''

    _KEYS = ['panelBackground', 'background', 'panelForeground',
             'panelHighlight']

    def __init__(self):
        super(QuickDocPanel, self).__init__()
        # layouts
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)
        child_layout = QtWidgets.QVBoxLayout()

        # A QTextEdit to show the doc
        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setAcceptRichText(True)
        layout.addWidget(self.text_edit)

        # A QPushButton (inside a child layout for a better alignment)
        # to close the panel
        self.bt_close = QtWidgets.QPushButton()
        self.bt_close.setIcon(QtGui.QIcon.fromTheme(
            'window-close', QtGui.QIcon(':/pyqode-icons/rc/close.png')))
        self.bt_close.setIconSize(QtCore.QSize(16, 16))
        self.bt_close.clicked.connect(self.hide)
        child_layout.addWidget(self.bt_close)
        child_layout.addStretch()
        layout.addLayout(child_layout)

        # Action
        self.action_quick_doc = QtWidgets.QAction('Show documentation', self)
        self.action_quick_doc.setShortcut('Alt+Q')

        self.action_quick_doc.triggered.connect(
            self._on_action_quick_doc_triggered)

    def _reset_stylesheet(self):
        p = self.text_edit.palette()
        p.setColor(p.Base, self.editor.palette().toolTipBase().color())
        p.setColor(p.Text, self.editor.palette().toolTipText().color())
        self.text_edit.setPalette(p)

    def on_install(self, editor):
        super(QuickDocPanel, self).on_install(editor)
        self._reset_stylesheet()
        self.setVisible(False)

    def on_state_changed(self, state):
        super(QuickDocPanel, self).on_state_changed(state)
        if state:
            self.editor.add_action(self.action_quick_doc)
        else:
            self.editor.remove_action(self.action_quick_doc)

    def refresh_style(self):
        self._reset_stylesheet()

    def _on_action_quick_doc_triggered(self):
        tc = TextHelper(self.editor).word_under_cursor(select_whole_word=True)
        request_data = {
            'code': self.editor.toPlainText(),
            'line': tc.blockNumber(),
            'column': tc.columnNumber(),
            'path': self.editor.file.path,
            'encoding': self.editor.file.encoding
        }
        self.editor.backend.send_request(
            quick_doc, request_data, on_receive=self._on_results_available)

    def _on_results_available(self, results):
        self._reset_stylesheet()
        self.setVisible(True)
        if len(results) and results[0] != '':
            string = '\n\n'.join(results)
            string = publish_parts(
                string, writer_name='html',
                settings_overrides={'output_encoding': 'unicode'})[
                    'html_body']
            string = string.replace('colspan="2"', 'colspan="0"')
            string = string.replace('<th ', '<th align="left" ')
            string = string.replace(
                '</tr>\n<tr class="field"><td>&nbsp;</td>', '')
            if string:
                skip_error_msg = False
                lines = []
                for l in string.splitlines():
                    if (l.startswith('<div class="system-message"') or
                            l.startswith(
                                '<div class="last system-message"')):
                        skip_error_msg = True
                        continue
                    if skip_error_msg:
                        if l.endswith('</div>'):
                            skip_error_msg = False
                    else:
                        lines.append(l)
                self.text_edit.setText('\n'.join(lines))
                return
        else:
            self.text_edit.setText('Documentation not found')
