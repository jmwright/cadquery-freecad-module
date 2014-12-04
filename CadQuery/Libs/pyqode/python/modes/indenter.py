# -*- coding: utf-8 -*-
"""
Contains the python indenter.
"""
from pyqode.qt import QtGui
from pyqode.core.modes import IndenterMode


class PyIndenterMode(IndenterMode):
    """
    Extends the core indenter to add the ability to always indent the whole
    line instead of inserting a tab at the cursor position. This behaviour can
    be turned off at runtime by setting :attr:`tab_always_indent` to False.
    """
    @property
    def tab_always_indent(self):
        """
        When this flag is set to True, any call to indent will indent the whole
        line instead of inserting a tab at the cursor position.
        """
        return self._tab_always_indent

    @tab_always_indent.setter
    def tab_always_indent(self, value):
        self._tab_always_indent = value
        if self.editor:
            for c in self.editor.clones:
                try:
                    c.modes.get(self.__class__).tab_always_indent = value
                except KeyError:
                    pass

    def __init__(self):
        super(PyIndenterMode, self).__init__()
        self._tab_always_indent = None
        self.tab_always_indent = True

    def indent(self):
        """
        Performs an indentation
        """
        if not self.tab_always_indent:
            super(PyIndenterMode, self).indent()
        else:
            cursor = self.editor.textCursor()
            assert isinstance(cursor, QtGui.QTextCursor)
            if cursor.hasSelection():
                self.indent_selection(cursor)
            else:
                # simply insert indentation at the cursor position
                tab_len = self.editor.tab_length
                cursor.beginEditBlock()
                if self.editor.use_spaces_instead_of_tabs:
                    cursor.insertText(tab_len * " ")
                else:
                    cursor.insertText('\t')
                cursor.endEditBlock()
                self.editor.setTextCursor(cursor)

    def unindent(self):
        """
        Performs an un-indentation
        """
        if self.tab_always_indent:
            cursor = self.editor.textCursor()
            if not cursor.hasSelection():
                cursor.select(cursor.LineUnderCursor)
            self.unindent_selection(cursor)
        else:
            super(PyIndenterMode, self).unindent()

    def clone_settings(self, original):
        self.tab_always_indent = original.tab_always_indent
