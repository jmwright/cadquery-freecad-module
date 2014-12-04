# -*- coding: utf-8 -*-
""" Contains the AutoCompleteMode """
import logging
from pyqode.core.api import TextHelper
from pyqode.core.api.mode import Mode


class AutoCompleteMode(Mode):
    """ Automatically complete quotes and parentheses

    Generic auto complete mode that automatically completes the following
    symbols:

        - " -> "
        - ' -> '
        - ( -> )
        - [ -> ]
        - { -> }
    """
    #: Auto complete mapping, maps input key with completion text.
    MAPPING = {'"': '"', "'": "'", "(": ")", "{": "}", "[": "]"}
    #: The format to use for each symbol in mapping when there is a selection
    SELECTED_QUOTES_FORMATS = {key: '%s%s%s' for key in MAPPING.keys()}
    #: The format to use for each symbol in mapping when there is no selection
    QUOTES_FORMATS = {key: '%s' for key in MAPPING.keys()}

    def __init__(self):
        super(AutoCompleteMode, self).__init__()
        self.logger = logging.getLogger(__name__)
        self._ignore_post = False

    def on_state_changed(self, state):
        if state:
            self.editor.post_key_pressed.connect(self._on_post_key_pressed)
            self.editor.key_pressed.connect(self._on_key_pressed)
        else:
            self.editor.post_key_pressed.disconnect(self._on_post_key_pressed)
            self.editor.key_pressed.disconnect(self._on_key_pressed)

    def _on_post_key_pressed(self, event):
        if not event.isAccepted() and not self._ignore_post:
            txt = event.text()
            next_char = TextHelper(self.editor).get_right_character()
            if txt in self.MAPPING:
                to_insert = self.MAPPING[txt]
                if (not next_char or next_char in self.MAPPING.keys() or
                        next_char in self.MAPPING.values() or
                        next_char.isspace()):
                    TextHelper(self.editor).insert_text(
                        self.QUOTES_FORMATS[txt] % to_insert)
        self._ignore_post = False

    def _on_key_pressed(self, event):
        txt = event.text()
        cursor = self.editor.textCursor()
        from pyqode.qt import QtGui
        assert isinstance(cursor, QtGui.QTextCursor)
        if cursor.hasSelection():
            # quoting of selected text
            if event.text() in self.MAPPING.keys():
                first = event.text()
                last = self.MAPPING[event.text()]
                cursor.insertText(
                    self.SELECTED_QUOTES_FORMATS[event.text()] % (
                        first, cursor.selectedText(), last))
                self.editor.setTextCursor(cursor)
                event.accept()
            else:
                self._ignore_post = True
            return
        next_char = TextHelper(self.editor).get_right_character()
        self.logger.debug('next char: %s', next_char)
        ignore = False
        if txt and next_char == txt and next_char in self.MAPPING:
            ignore = True
        elif event.text() == ')' or event.text() == ']' or event.text() == '}':
            if next_char == ')' or next_char == ']' or next_char == '}':
                ignore = True
        if ignore:
            event.accept()
            TextHelper(self.editor).clear_selection()
            TextHelper(self.editor).move_right()
