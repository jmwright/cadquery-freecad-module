# -*- coding: utf-8 -*-
import os
from pyqode.core import api
from pyqode.qt import QtGui, QtCore, QtWidgets


class CommentsMode(api.Mode):
    """ Comments/uncomments a set of lines using Ctrl+/.
    """
    def __init__(self):
        super(CommentsMode, self).__init__()
        self.action = QtWidgets.QAction("Comment/Uncomment", self.editor)
        self.action.setShortcut("Ctrl+/")

    def on_state_changed(self, state):
        """
        Called when the mode is activated/deactivated
        """
        if state:
            self.action.triggered.connect(self.comment)
            self.editor.add_action(self.action)
            if 'pyqt5' in os.environ['QT_API'].lower():
                self.editor.key_pressed.connect(self.on_key_pressed)
        else:
            self.editor.remove_action(self.action)
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

    def comment(self):
        """
        Comments/Uncomments the selected lines or the current lines if there
        is no selection.
        """
        cursor = self.editor.textCursor()
        # make comment/uncomment a single operation for the undo stack
        cursor.beginEditBlock()

        # did the user do a reversed selection (from _bottom to _top)?
        has_sel, reversed_sel, sel_end, sel_start = self.check_selection(
            cursor)
        # get selected lines
        lines = cursor.selection().toPlainText().splitlines()
        nb_lines = len(lines)
        # move to first line
        cursor.setPosition(sel_start)
        # we uncomment if all lines were commented, otherwise we comment all
        # lines in selection
        comment = False
        for i in range(nb_lines):
            cursor.movePosition(QtGui.QTextCursor.StartOfLine)
            cursor.movePosition(QtGui.QTextCursor.EndOfLine, cursor.KeepAnchor)
            line = cursor.selectedText().lstrip()
            if not len(line.strip()):
                # skips empty lines
                continue
            indent = len(cursor.selectedText()) - len(line)
            if not line.startswith("# "):
                comment = True
                break
            # next line
            cursor.movePosition(QtGui.QTextCursor.EndOfLine)
            cursor.setPosition(cursor.position() + 1)
        cursor.setPosition(sel_start)
        l = 2  # len('# ') == 2
        performed = 0
        for i in range(nb_lines):
            cursor.movePosition(QtGui.QTextCursor.StartOfLine)
            cursor.movePosition(QtGui.QTextCursor.EndOfLine, cursor.KeepAnchor)
            line = cursor.selectedText().lstrip()
            if line != "":
                cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                # Uncomment
                if not comment:
                    cursor.setPosition(cursor.position() + indent)
                    cursor.movePosition(cursor.Right, cursor.KeepAnchor, 2)
                    cursor.insertText("")
                    if i == 0:
                        sel_start -= l
                    sel_end -= l
                # comment
                else:
                    cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                    cursor.setPosition(cursor.position() + indent)
                    cursor.insertText("# ")
                    if i == 0:
                        sel_start += l
                    sel_end += l
            performed += 1
            # next line
            cursor.movePosition(QtGui.QTextCursor.EndOfLine)
            if not cursor.atEnd():
                cursor.setPosition(cursor.position() + 1)
        cursor.endEditBlock()
        if has_sel:
            cursor.setPosition(sel_start)
            cursor.setPosition(sel_end, QtGui.QTextCursor.KeepAnchor)
        else:
            if not cursor.atEnd():
                if performed:
                    cursor.setPosition(sel_start + (l if not comment else -l))
                cursor.movePosition(cursor.Down, cursor.MoveAnchor, 1)
        self.editor.setTextCursor(cursor)
