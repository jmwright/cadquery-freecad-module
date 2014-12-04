# -*- coding: utf-8 -*-
"""
This module contains interactive widgets:
    - interactive console: a text edit made to run subprocesses interactively
"""
import locale
import logging
import os
import sys

from pyqode.core.api.client import PROCESS_ERROR_STRING
from pyqode.qt.QtCore import Qt, Signal, QProcess, QProcessEnvironment
from pyqode.qt.QtWidgets import QTextEdit
from pyqode.qt.QtGui import QColor, QTextCursor, QFont


def _logger():
    return logging.getLogger(__name__)


class InteractiveConsole(QTextEdit):
    """
    An interactive console is a QTextEdit specialised to run a process
    interactively

    The user will see the process outputs and will be able to
    interact with the process by typing some text, this text will be forwarded
    to the process stdin.

    You can customize the colors using the following attributes:

        - stdout_color: color of the process stdout
        - stdin_color: color of the user inputs. Green by default
        - app_msg_color: color for custom application message (
          process started, process finished)
        - stderr_color: color of the process stderr

    """
    #: Signal emitted when the process has finished.
    process_finished = Signal(int)

    def __init__(self, parent=None):
        super(InteractiveConsole, self).__init__(parent)
        self._stdout_col = QColor("#404040")
        self._app_msg_col = QColor("#4040FF")
        self._stdin_col = QColor("#22AA22")
        self._stderr_col = QColor("#FF0000")
        self._process = None
        self._args = None
        self._usr_buffer = ""
        self._clear_on_start = True
        self.process = QProcess()
        self._merge_outputs = False
        self.process.finished.connect(self._on_process_finished)
        self.process.error.connect(self._write_error)
        self.process.readyReadStandardError.connect(self._on_stderr)
        self.process.readyReadStandardOutput.connect(self._on_stdout)
        self._running = False
        self._writer = self.write
        self._user_stop = False
        font = "monospace"
        if sys.platform == "win32":
            font = "Consolas"
        elif sys.platform == "darwin":
            font = 'Monaco'
        self._font_family = font
        self.setFont(QFont(font, 10))
        self.setReadOnly(True)

    def set_writer(self, writer):
        """
        Changes the writer function to handle writing to the text edit.

        A writer function must have the following prototype:

        .. code-block:: python

            def write(text_edit, text, color)

        :param writer: write function as described above.
        """
        if self._writer != writer and self._writer:
            self._writer = None
        if writer:
            self._writer = writer

    def _on_stdout(self):
        raw = self.process.readAllStandardOutput()
        txt = bytes(raw).decode(locale.getpreferredencoding())
        self._writer(self, txt, self.stdout_color)

    def _on_stderr(self):
        txt = bytes(self.process.readAllStandardError()).decode(
            locale.getpreferredencoding())
        _logger().debug('%s', txt)
        self._writer(self, txt, self.stderr_color)

    @property
    def background_color(self):
        """ The console background color. Default is white. """
        pal = self.palette()
        return pal.color(pal.Base)

    @background_color.setter
    def background_color(self, color):
        pal = self.palette()
        pal.setColor(pal.Base, color)
        pal.setColor(pal.Text, self.stdout_color)
        self.setPalette(pal)

    @property
    def stdout_color(self):
        """ STDOUT color. Default is black. """
        return self._stdout_col

    @stdout_color.setter
    def stdout_color(self, color):
        self._stdout_col = color
        pal = self.palette()
        pal.setColor(pal.Text, self._stdout_col)
        self.setPalette(pal)

    @property
    def stderr_color(self):
        """
        Color for stderr output if
        :attr:`pyqode.core.widgets.InteractiveConsole.merge_outputs` is False.

        Default is Red.
        """
        return self._stderr_col

    @stderr_color.setter
    def stderr_color(self, color):
        self._stderr_col = color

    @property
    def stdin_color(self):
        """
        STDIN color. Default is green.
        """
        return self._stdin_col

    @stdin_color.setter
    def stdin_color(self, color):
        self._stdin_col = color

    @property
    def app_msg_color(self):
        """
        Color of the application messages (e.g.: 'Process started',
        'Process finished with status %d')
        """
        return self._app_msg_col

    @app_msg_color.setter
    def app_msg_color(self, color):
        self._app_msg_col = color

    @property
    def clear_on_start(self):
        """
        True to clear window when starting a new process. False to accumulate
        outputs.
        """
        return self._clear_on_start

    @clear_on_start.setter
    def clear_on_start(self, value):
        self._clear_on_start = value

    @property
    def merge_outputs(self):
        """
        Merge stderr with stdout. Default is False.

        If set to true, stderr and stdin will use the same color: stdin_color.

        """
        return self._merge_outputs

    @merge_outputs.setter
    def merge_outputs(self, value):
        self._merge_outputs = value
        if value:
            self.process.setProcessChannelMode(QProcess.MergedChannels)
        else:
            self.process.setProcessChannelMode(QProcess.SeparateChannels)

    @property
    def is_running(self):
        """
        Checks if the process is running.
        :return:
        """
        return self._running

    def closeEvent(self, *args, **kwargs):
        if self.process.state() == QProcess.Running:
            self.process.terminate()

    def start_process(self, process, args=None, cwd=None, env=None):
        """
        Starts a process interactively.

        :param process: Process to run
        :type process: str

        :param args: List of arguments (list of str)
        :type args: list

        :param cwd: Working directory
        :type cwd: str

        :param env: environment variables (dict).
        """
        self.setReadOnly(False)
        if env is None:
            env = {}
        if args is None:
            args = []
        if not self._running:
            if cwd:
                self.process.setWorkingDirectory(cwd)
            e = self.process.systemEnvironment()
            ev = QProcessEnvironment()
            for v in e:
                values = v.split('=')
                ev.insert(values[0], '='.join(values[1:]))
            for k, v in env.items():
                ev.insert(k, v)
            self.process.setProcessEnvironment(ev)
            self._running = True
            self._process = process
            self._args = args
            if self._clear_on_start:
                self.clear()
            self._user_stop = False
            self.process.start(process, args)
            self._write_started()
        else:
            _logger().warning('a process is already running')

    def stop_process(self):
        """
        Stop the process (by killing it).
        """
        _logger().debug('killing process')
        self._user_stop = True
        self.process.kill()
        self.setReadOnly(True)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # send the user input to the child process
            if sys.platform == 'win32':
                self._usr_buffer += "\r"
            self._usr_buffer += "\n"
            self.process.write(bytes(
                self._usr_buffer, locale.getpreferredencoding()))
            self._usr_buffer = ""
        else:
            if event.key() != Qt.Key_Backspace:
                txt = event.text()
                self._usr_buffer += txt
                self.setTextColor(self._stdin_col)
            elif event.text().isalnum():
                self._usr_buffer = self._usr_buffer[
                    0:len(self._usr_buffer) - 1]
        # text is inserted here, the text color must be defined before this
        # line
        super(InteractiveConsole, self).keyPressEvent(event)
        self.setTextColor(self._stdout_col)

    def _on_process_finished(self, exit_code, exit_status):
        if not self._user_stop:
            self._writer(
                self, "\nProcess finished with exit code %d" %
                exit_code, self._app_msg_col)
        self._running = False
        _logger().debug('process finished (exit_code=%r, exit_status=%r)',
                        exit_code, exit_status)
        self.process_finished.emit(exit_code)
        self.setReadOnly(True)

    def _write_started(self):
        self._writer(self, "{0} {1}\n".format(
            self._process, " ".join(self._args)), self._app_msg_col)
        self._running = True
        _logger().debug('process started')

    def _write_error(self, error):
        if self._user_stop:
            self._writer(self, '\nProcess stopped by the user',
                         self.app_msg_color)
        else:
            self._writer(self, "Failed to start {0} {1}\n".format(
                self._process, " ".join(self._args)), self.app_msg_color)
            err = PROCESS_ERROR_STRING[error]
            self._writer(self, "Error: %s" % err, self.stderr_color)
            _logger().debug('process error: %s', err)
        self._running = False

    @staticmethod
    def write(text_edit, text, color):
        """
        Default write function. Move the cursor to the end and insert text with
        the specified color.

        :param text_edit: QInteractiveConsole instance
        :type text_edit: pyqode.widgets.QInteractiveConsole

        :param text: Text to write
        :type text: str

        :param color: Desired text color
        :type color: QColor
        """
        text_edit.moveCursor(QTextCursor.End)
        text_edit.setTextColor(color)
        text_edit.insertPlainText(text)
        text_edit.moveCursor(QTextCursor.End)

    def apply_color_scheme(self, color_scheme):
        """
        Apply a pygments color scheme to the console.

        As there is not a 1 to 1 mapping between color scheme formats and
        console formats, we decided to make the following mapping (it usually
        looks good for most of the available pygments styles):

            - stdout_color = normal color
            - stderr_color = red (lighter if background is dark)
            - stdin_color = numbers color
            - app_msg_color = string color
            - bacgorund_color = background


        :param color_scheme: pyqode.core.api.ColorScheme to apply
        """
        self.stdout_color = color_scheme.formats['normal'].foreground().color()
        self.stdin_color = color_scheme.formats['number'].foreground().color()
        self.app_msg_color = color_scheme.formats[
            'string'].foreground().color()
        self.background_color = color_scheme.background
        if self.background_color.lightness() < 128:
            self.stderr_color = QColor('#FF8080')
        else:
            self.stderr_color = QColor('red')
