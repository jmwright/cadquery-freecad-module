# -*- coding: utf-8 -*-
""" Contains the python autocomplete mode """
from pyqode.core.api import TextHelper
from pyqode.core.modes import AutoCompleteMode


class PyAutoCompleteMode(AutoCompleteMode):
    """ Auto complete parentheses and method definitions.

    Extends :class:`pyqode.core.modes.AutoCompleteMode` to add
    support for method/function call:

        - function completion adds "):" to the function definition.
        - method completion adds "self):" to the method definition.
    """
    def _in_method_call(self):
        helper = TextHelper(self.editor)
        line_nbr = helper.current_line_nbr() - 1
        expected_indent = helper.line_indent() - 4
        while line_nbr >= 0:
            text = helper.line_text(line_nbr)
            indent = len(text) - len(text.lstrip())
            if indent == expected_indent and 'class' in text:
                return True
            line_nbr -= 1
        return False

    def _handle_fct_def(self):
        if self._in_method_call():
            th = TextHelper(self.editor)
            if '@classmethod' in th.line_text(th.current_line_nbr() - 1):
                txt = "cls):"
            else:
                txt = "self):"
        else:
            txt = "):"
        cursor = self.editor.textCursor()
        cursor.insertText(txt)
        cursor.movePosition(cursor.Left, cursor.MoveAnchor, 2)
        self.editor.setTextCursor(cursor)

    def _on_post_key_pressed(self, event):
        # if we are in disabled cc, use the parent implementation
        helper = TextHelper(self.editor)
        if (event.text() == "(" and
                helper.current_line_text().lstrip().startswith("def ")):
            self._handle_fct_def()
        else:
            line = TextHelper(self.editor).current_line_text().strip()
            if not line.endswith(('"""', "'''")):
                super(PyAutoCompleteMode, self)._on_post_key_pressed(event)
