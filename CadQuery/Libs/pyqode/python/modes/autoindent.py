# -*- coding: utf-8 -*-
""" Contains smart indent modes """
import re
from pyqode.core.api import TextHelper, get_block_symbol_data
from pyqode.qt.QtGui import QTextCursor
from pyqode.core.modes import AutoIndentMode, SymbolMatcherMode
from pyqode.core.modes.matcher import CLOSE, PAREN, SQUARE, BRACE, OPEN


class PyAutoIndentMode(AutoIndentMode):
    """ Automatically indents text, respecting the PEP8 conventions.

    Customised :class:`pyqode.core.modes.AutoIndentMode` for python
    that tries its best to follow the pep8 indentation guidelines.

    """
    def __init__(self):
        super(PyAutoIndentMode, self).__init__()
        self._helper = None

    def on_install(self, editor):
        super(PyAutoIndentMode, self).on_install(editor)
        self._helper = TextHelper(editor)

    def _get_indent(self, cursor):
        ln, column = self._helper.cursor_position()
        fullline = self._get_full_line(cursor)
        line = fullline[:column]
        pre, post = AutoIndentMode._get_indent(self, cursor)
        if self._at_block_start(cursor, line):
            return pre, post
        # return pressed in comments
        c2 = QTextCursor(cursor)
        if c2.atBlockEnd():
            c2.movePosition(c2.Left)
        if (self._helper.is_comment_or_string(
                c2, formats=['comment', 'docstring']) or
                fullline.endswith('"""')):
            if line.strip().startswith("#") and column != len(fullline):
                post += '# '
            return pre, post
        # between parens
        elif self._between_paren(cursor, column):
            return self._handle_indent_between_paren(
                column, line, (pre, post), cursor)
        else:
            lastword = self._get_last_word(cursor)
            lastwordu = self._get_last_word_unstripped(cursor)
            in_string_def, char = self._is_in_string_def(fullline, column)
            if in_string_def:
                post, pre = self._handle_indent_inside_string(
                    char, cursor, fullline, post)
            elif (fullline.rstrip().endswith(":") and
                    lastword.rstrip().endswith(':') and
                    self._at_block_end(cursor, fullline)):
                post = self._handle_new_scope_indentation(
                    cursor, fullline)
            elif line.endswith("\\"):
                # if user typed \ and press enter -> indent is always
                # one level higher
                post += self.editor.tab_length * " "
            elif (fullline.endswith((')', '}', ']')) and
                    lastword.endswith((')', '}', ']'))):
                post = self._handle_indent_after_paren(cursor, post)
            elif ("\\" not in fullline and "#" not in fullline and
                  not self._at_block_end(cursor, fullline)):
                post, pre = self._handle_indent_in_statement(
                    fullline, lastwordu, post, pre)
            elif ((self._at_block_end(cursor, fullline) and
                    fullline.strip().startswith('return ')) or
                    lastword == "pass"):
                post = post[:-self.editor.tab_length]
        return pre, post

    @staticmethod
    def _is_in_string_def(full_line, column):
        count = 0
        char = "'"
        for i in range(len(full_line)):
            if full_line[i] == "'" or full_line[i] == '"':
                count += 1
            if full_line[i] == '"' and i < column:
                char = '"'
        count_after_col = 0
        for i in range(column, len(full_line)):
            if full_line[i] == "'" or full_line[i] == '"':
                count_after_col += 1
        return count % 2 == 0 and count_after_col % 2 == 1, char

    @staticmethod
    def _is_paren_open(paren):
        return (paren.character == "(" or paren.character == "["
                or paren.character == '{')

    @staticmethod
    def _is_paren_closed(paren):
        return (paren.character == ")" or paren.character == "]"
                or paren.character == '}')

    @staticmethod
    def _get_full_line(tc):
        tc2 = QTextCursor(tc)
        tc2.select(QTextCursor.LineUnderCursor)
        full_line = tc2.selectedText()
        return full_line

    def _parens_count_for_block(self, col, block):
        open_p = []
        closed_p = []
        lists = get_block_symbol_data(self.editor, block)
        for symbols in lists:
            for paren in symbols:
                if paren.position >= col:
                    continue
                if self._is_paren_open(paren):
                    if not col:
                        return -1, -1, [], []
                    open_p.append(paren)
                if self._is_paren_closed(paren):
                    closed_p.append(paren)
        return len(open_p), len(closed_p), open_p, closed_p

    def _between_paren(self, tc, col):
        try:
            self.editor.modes.get('SymbolMatcherMode')
        except KeyError:
            return False
        block = tc.block()
        nb_open = nb_closed = 0
        while block.isValid() and block.text().strip():
            o, c, _, _ = self._parens_count_for_block(col, block)
            nb_open += o
            nb_closed += c
            block = block.previous()
            col = len(block.text())
        return nb_open > nb_closed

    @staticmethod
    def _get_last_word(tc):
        tc2 = QTextCursor(tc)
        tc2.movePosition(QTextCursor.Left, tc.KeepAnchor, 1)
        tc2.movePosition(QTextCursor.WordLeft, tc.KeepAnchor)
        return tc2.selectedText().strip()

    @staticmethod
    def _get_last_word_unstripped(tc):
        tc2 = QTextCursor(tc)
        tc2.movePosition(QTextCursor.Left, tc.KeepAnchor, 1)
        tc2.movePosition(QTextCursor.WordLeft, tc.KeepAnchor)
        return tc2.selectedText()

    def _get_indent_of_opening_paren(self, tc):
        tc.movePosition(tc.Left, tc.KeepAnchor)
        char = tc.selectedText()
        tc.movePosition(tc.Right, tc.MoveAnchor)
        mapping = {
            ')': (OPEN, PAREN),
            ']': (OPEN, SQUARE),
            '}': (OPEN, BRACE)
        }
        try:
            character, char_type = mapping[char]
        except KeyError:
            return None
        else:
            ol, oc = self.editor.modes.get(SymbolMatcherMode).symbol_pos(
                tc, character, char_type)
            line = self._helper.line_text(ol)
            return len(line) - len(line.lstrip())

    def _get_first_open_paren(self, tc, column):
        pos = None
        char = None
        ln = tc.blockNumber()
        tc_trav = QTextCursor(tc)
        mapping = {
            '(': (CLOSE, PAREN),
            '[': (CLOSE, SQUARE),
            '{': (CLOSE, BRACE)
        }
        while ln >= 0 and tc.block().text().strip():
            tc_trav.movePosition(tc_trav.StartOfLine, tc_trav.MoveAnchor)
            lists = get_block_symbol_data(self.editor, tc_trav.block())
            all_symbols = []
            for symbols in lists:
                all_symbols += [s for s in symbols]
            symbols = sorted(all_symbols, key=lambda x: x.position)
            for paren in reversed(symbols):
                if paren.position < column:
                    if self._is_paren_open(paren):
                        if paren.position > column:
                            continue
                        else:
                            pos = tc_trav.position() + paren.position
                            char = paren.character
                            # ensure it does not have a closing paren on
                            # the same line
                            tc3 = QTextCursor(tc)
                            tc3.setPosition(pos)
                            try:
                                ch, ch_type = mapping[paren.character]
                                l, c = self.editor.modes.get(
                                    SymbolMatcherMode).symbol_pos(
                                    tc3, ch, ch_type)
                            except KeyError:
                                continue
                            if l == ln and c < column:
                                continue
                            return pos, char
            # check previous line
            tc_trav.movePosition(tc_trav.Up, tc_trav.MoveAnchor)
            ln = tc_trav.blockNumber()
            column = len(self._helper.line_text(ln))
        return pos, char

    def _get_paren_pos(self, tc, column):
        pos, char = self._get_first_open_paren(tc, column)
        mapping = {'(': PAREN, '[': SQUARE, '{': BRACE}
        tc2 = QTextCursor(tc)
        tc2.setPosition(pos)
        import sys
        ol, oc = self.editor.modes.get(SymbolMatcherMode).symbol_pos(
            tc2, OPEN, mapping[char])
        cl, cc = self.editor.modes.get(SymbolMatcherMode).symbol_pos(
            tc2, CLOSE, mapping[char])
        return (ol, oc), (cl, cc)

    @staticmethod
    def _get_next_char(tc):
        tc2 = QTextCursor(tc)
        tc2.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
        char = tc2.selectedText()
        return char

    @staticmethod
    def _get_prev_char(tc):
        tc2 = QTextCursor(tc)
        tc2.movePosition(QTextCursor.PreviousCharacter, QTextCursor.KeepAnchor)
        char = tc2.selectedText()
        while char == ' ':
            tc2.movePosition(QTextCursor.PreviousCharacter, QTextCursor.KeepAnchor)
            char = tc2.selectedText()
        return char.strip()

    def _handle_indent_between_paren(self, column, line, parent_impl, tc):
        """
        Handle indent between symbols such as parenthesis, braces,...
        """
        pre, post = parent_impl
        next_char = self._get_next_char(tc)
        prev_char = self._get_prev_char(tc)
        prev_open = prev_char in ['[', '(', '{']
        next_close = next_char in [']', ')', '}']
        (open_line, open_symbol_col), (close_line, close_col) = \
            self._get_paren_pos(tc, column)
        open_line_txt = self._helper.line_text(open_line)
        open_line_indent = len(open_line_txt) - len(open_line_txt.lstrip())
        if prev_open:
            post = (open_line_indent + self.editor.tab_length) * ' '
        elif next_close and prev_char != ',':
            post = open_line_indent * ' '
        elif tc.block().blockNumber() == open_line:
            post = open_symbol_col * ' '

        # adapt indent if cursor on closing line and next line have same
        # indent -> PEP8 compliance
        if close_line and close_col:
            txt = self._helper.line_text(close_line)
            bn = tc.block().blockNumber()
            flg = bn == close_line
            next_indent = self._helper.line_indent(bn + 1) * ' '
            if flg and txt.strip().endswith(':') and next_indent == post:
                # | look at how the previous line ( ``':'):`` ) was
                # over-indented, this is actually what we are trying to
                # achieve here
                post += self.editor.tab_length * ' '

        # breaking string
        if next_char in ['"', "'"]:
            tc.movePosition(tc.Left)
        is_string = self._helper.is_comment_or_string(tc, formats=['string'])
        if next_char in ['"', "'"]:
            tc.movePosition(tc.Right)
        if is_string:
            trav = QTextCursor(tc)
            while self._helper.is_comment_or_string(
                    trav, formats=['string']):
                trav.movePosition(trav.Left)
            trav.movePosition(trav.Right)
            symbol = '%s' % self._get_next_char(trav)
            pre += symbol
            post += symbol

        return pre, post

    @staticmethod
    def _at_block_start(tc, line):
        """
        Improve QTextCursor.atBlockStart to ignore spaces
        """
        if tc.atBlockStart():
            return True
        column = tc.columnNumber()
        indentation = len(line) - len(line.lstrip())
        return column <= indentation

    @staticmethod
    def _at_block_end(tc, fullline):
        if tc.atBlockEnd():
            return True
        column = tc.columnNumber()
        return column >= len(fullline.rstrip()) - 1

    def _handle_indent_inside_string(self, char, cursor, fullline, post):
        # break string with a '\' at the end of the original line, always
        # breaking strings enclosed by parens is done in the
        # _handle_between_paren method
        n = self.editor.tab_length
        pre = '%s \\' % char
        post += n * ' '
        if fullline.endswith(':'):
            post += n * " "
        post += char
        return post, pre

    def _handle_new_scope_indentation(self, cursor, fullline):
        try:
            indent = (self._get_indent_of_opening_paren(cursor) +
                      self.editor.tab_length)
            post = indent * " "
        except TypeError:
            # e.g indent is None (meaning the line does not ends with ):, ]:
            # or }:
            kw = ["if", "class", "def", "while", "for", "else", "elif",
                  "except", "finally", "try"]
            l = fullline
            ln = cursor.blockNumber()

            def check_kw_in_line(kwds, lparam):
                for kwd in kwds:
                    if kwd in lparam:
                        return True
                return False

            while not check_kw_in_line(kw, l) and ln:
                ln -= 1
                l = self._helper.line_text(ln)
            indent = (len(l) - len(l.lstrip())) * " "
            indent += self.editor.tab_length * " "
            post = indent
        return post

    def _handle_indent_after_paren(self, cursor, post):
        indent = self._get_indent_of_opening_paren(cursor)
        if indent is not None:
            post = indent * " "
        return post

    def _handle_indent_in_statement(self, fullline, lastword, post, pre):
        if lastword and lastword[-1] != " ":
            pre += " \\"
        else:
            pre += '\\'
        post += self.editor.tab_length * " "
        if fullline.endswith(':'):
            post += self.editor.tab_length * " "
        return post, pre
