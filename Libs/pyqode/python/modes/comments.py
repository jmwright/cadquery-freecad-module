# -*- coding: utf-8 -*-
import sys
import os
from pyqode.core import api, icons
from pyqode.qt import QtGui, QtCore, QtWidgets


class CommentsMode(api.Mode):
    """ Comments/uncomments a set of lines using Ctrl+/.
    """
    def __init__(self):
        super(CommentsMode, self).__init__()
        self.action = QtWidgets.QAction(_("Comment/Uncomment"), self.editor)
        self.action.setShortcut("Ctrl+/")
        icon = icons.icon(qta_name='fa.comment')
        if icon:
            self.action.setIcon(icon)

    def on_state_changed(self, state):
        """
        Called when the mode is activated/deactivated
        """
        if state:
            self.action.triggered.connect(self.comment)
            self.editor.add_action(self.action, sub_menu='Python')
            if 'pyqt5' in os.environ['QT_API'].lower():
                self.editor.key_pressed.connect(self.on_key_pressed)
        else:
            self.editor.remove_action(self.action, sub_menu='Python')
            self.action.triggered.disconnect(self.comment)
            if 'pyqt5' in os.environ['QT_API'].lower():
                self.editor.key_pressed.disconnect(self.on_key_pressed)

    def on_key_pressed(self, key_event):
        ctrl = (key_event.modifiers() & QtCore.Qt.ControlModifier ==
                QtCore.Qt.ControlModifier)
        if key_event.key() == QtCore.Qt.Key_Slash and ctrl:
            self.comment()
            key_event.accept()

    def check_selection(self, cursor):
        sel_start = cursor.selectionStart()
        sel_end = cursor.selectionEnd()
        reversed_selection = cursor.position() == sel_start
        # were there any selected lines? If not select the current line
        has_selection = True
        if not cursor.hasSelection():
            cursor.select(QtGui.QTextCursor.LineUnderCursor)
            has_selection = False

        return has_selection, reversed_selection, sel_end, sel_start

    def get_selected_lines(self):
        nb_lines = len(
            api.TextHelper(self.editor).selected_text().splitlines())
        cursor = self.editor.textCursor()
        self._move_cursor_to_selection_start(cursor)
        lines = []
        for i in range(nb_lines):
            lines.append(cursor.block().text())
            cursor.movePosition(cursor.NextBlock)
        return lines

    def get_operation(self):
        lines = self.get_selected_lines()
        if not lines:
            lines = [api.TextHelper(self.editor).current_line_text()]
        min_indent = sys.maxsize
        comment = False
        for l in lines:
            indent = len(l) - len(l.lstrip())
            if indent < min_indent and l:
                min_indent = indent
            if not l.lstrip().startswith('# ') and l:
                comment = True
        return min_indent, comment, len(lines)

    def comment(self):
        """
        Comments/Uncomments the selected lines or the current lines if there
        is no selection.
        """
        cursor = self.editor.textCursor()
        # get the indent at which comment should be inserted and whether to
        # comment or uncomment the selected text
        indent, comment, nb_lines = self.get_operation()
        has_selection = cursor.hasSelection()
        if nb_lines > 1:
            self._move_cursor_to_selection_start(cursor)
            cursor.beginEditBlock()
            for i in range(nb_lines):
                self.comment_line(indent, cursor, comment)
                cursor.movePosition(cursor.NextBlock)
            cursor.endEditBlock()
        else:
            # comment a single line
            cursor.beginEditBlock()
            self.comment_line(indent, cursor, comment)
            if not has_selection:
                # move to the first non-whitespace character of the next line
                cursor.movePosition(cursor.NextBlock)
                text = cursor.block().text()
                indent = len(text) - len(text.lstrip())
                cursor.movePosition(cursor.Right, cursor.MoveAnchor, indent)
                cursor.endEditBlock()
                self.editor.setTextCursor(cursor)
            else:
                cursor.endEditBlock()

    def _move_cursor_to_selection_start(self, cursor):
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        if start > end:
            start = end
        cursor.setPosition(start)

    def comment_line(self, indent, cursor, comment):
        if not cursor.block().text():
            return
        cursor.movePosition(cursor.StartOfLine)
        cursor.movePosition(cursor.Right, cursor.MoveAnchor, indent)
        if comment:
            cursor.insertText('# ')
            if cursor.atEnd():
                cursor.insertText('\n')
        else:
            cursor.deleteChar()
            cursor.deleteChar()
