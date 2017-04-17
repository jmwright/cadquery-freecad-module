"""
This module contains the python code fold detector.
"""
import re
from pyqode.core.api import IndentFoldDetector, TextBlockHelper, TextHelper


class PythonFoldDetector(IndentFoldDetector):
    """
    Python specific fold detector.

    Python is an indent based language so we use indentation for detecting
    the outline but we discard regions with higher indentation if they do not
    follow a trailing ':'. That way, only the real logical blocks are
    displayed.

    We also add some trickery to make import regions and docstring appear with
    an higher fold level than they should be (in order to make them foldable).
    """
    #: regex which identifies a single line docstring
    _single_line_docstring = re.compile(r'""".*"""')

    def _strip_comments(self, prev_block):
        txt = prev_block.text().strip() if prev_block else ''
        if txt.find('#') != -1:
            txt = txt[:txt.find('#')].strip()
        return txt

    def _handle_docstrings(self, block, lvl, prev_block):
        if block.docstring:
            is_start = block.text().strip().startswith('"""')
            if is_start:
                TextBlockHelper.get_fold_lvl(prev_block) + 1
            else:
                pblock = block.previous()
                while pblock.isValid() and pblock.text().strip() == '':
                    pblock = pblock.previous()
                is_start = pblock.text().strip().startswith('"""')
                if is_start:
                    return TextBlockHelper.get_fold_lvl(pblock) + 1
                else:
                    return TextBlockHelper.get_fold_lvl(pblock)
        # fix end of docstring
        elif prev_block and prev_block.text().strip().endswith('"""'):
            single_line = self._single_line_docstring.match(
                prev_block.text().strip())
            if single_line:
                TextBlockHelper.set_fold_lvl(prev_block, lvl)
            else:
                TextBlockHelper.set_fold_lvl(
                    prev_block, TextBlockHelper.get_fold_lvl(
                        prev_block.previous()))
        return lvl

    def _handle_imports(self, block, lvl, prev_block):
        txt = block.text()
        indent = len(txt) - len(txt.lstrip())
        if (hasattr(block, 'import_stmt') and prev_block and
                'import ' in prev_block.text() and indent == 0):
            return 1
        return lvl

    def detect_fold_level(self, prev_block, block):
        """
        Perfoms fold level detection for current block (take previous block
        into account).

        :param prev_block: previous block, None if `block` is the first block.
        :param block: block to analyse.
        :return: block fold level
        """
        # Python is an indent based language so use indentation for folding
        # makes sense but we restrict new regions to indentation after a ':',
        # that way only the real logical blocks are displayed.
        lvl = super(PythonFoldDetector, self).detect_fold_level(
            prev_block, block)
        # cancel false indentation, indentation can only happen if there is
        # ':' on the previous line
        prev_lvl = TextBlockHelper.get_fold_lvl(prev_block)
        if prev_block and lvl > prev_lvl and not (
                self._strip_comments(prev_block).endswith(':')):
            lvl = prev_lvl
        lvl = self._handle_docstrings(block, lvl, prev_block)
        lvl = self._handle_imports(block, lvl, prev_block)
        return lvl
