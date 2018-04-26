"""
This module provides a python console widgets based on the pyqode.core's OutputWindow.
"""
import sys

from pyqode.qt import QtWidgets, QtGui
from pyqode.core import modes as modes
from pyqode.core.api import ColorScheme
from pyqode.core.widgets import output_window

from pyqode.python import modes as pymodes
from pyqode.python.backend import server


class SyntaxHighlighter(pymodes.PythonSH):
    """
    Extends the base syntax highlighter to only highlight code that is entered after a python prompt
    """
    def highlight_block(self, text, block):
        if text.startswith('>>>') or text.startswith('...'):
            super(SyntaxHighlighter, self).highlight_block(text, block)
        else:
            match = self.editor.link_regex.search(text)
            if match:
                start, end = match.span('url')
                fmt = QtGui.QTextCharFormat()
                fmt.setForeground(QtWidgets.qApp.palette().highlight().color())
                fmt.setUnderlineStyle(fmt.SingleUnderline)
                self.setFormat(start, end - start, fmt)


class CodeCompletionMode(modes.CodeCompletionMode):
    """
    Extend base code completion mode to insert the completion in the user buffer of the
    input handler
    """
    pass


class PyConsole(output_window.OutputWindow):
    """
    Extends the OutputWindow to run a python interpreter with all the bells and whistles of a python code
    editor (code completion!).
    """
    def __init__(self, parent=None, interpreter=sys.executable, backend=server.__file__,
                 color_scheme='qt'):
        self._pygment_color_scheme = color_scheme
        super(PyConsole, self).__init__(parent=parent, input_handler=output_window.BufferedInputHandler(),
                                        backend=backend)
        self.start_process(interpreter.replace('pythonw', 'python'),
                           arguments=['-i'], print_command=False, use_pseudo_terminal=True)

    def change_interpreter(self, interpreter=sys.executable):
        self.stop_process()
        self.start_process(interpreter.replace('pythonw', 'python'),
                           arguments=['-i'], print_command=False, use_pseudo_terminal=True)

    def _init_code_edit(self, backend):
        self.modes.append(modes.SymbolMatcherMode())
        self.modes.append(CodeCompletionMode())
        self.modes.append(pymodes.PyAutoCompleteMode())
        self.modes.append(modes.IndenterMode())
        super(PyConsole, self)._init_code_edit(backend)
        self.modes.append(SyntaxHighlighter(self.document(), color_scheme=ColorScheme(self._pygment_color_scheme)))
        try:
            self.panels.remove('ReadOnlyPanel')
        except KeyError:
            pass
        self.update_terminal_colors()

    def update_terminal_colors(self):
        """
        Update terminal color scheme based on the pygments color scheme colors
        """
        self.color_scheme = self.create_color_scheme(
            background=self.syntax_highlighter.color_scheme.background,
            foreground=self.syntax_highlighter.color_scheme.formats['normal'].foreground().color())

    def terminate_process(self):
        self._process.write(b'exit()')
        self._process.waitForBytesWritten()
