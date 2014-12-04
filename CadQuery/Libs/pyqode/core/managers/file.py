"""
This module contains the file helper implementation

"""
try:
    from future.builtins import open
    from future.builtins import str
except:
    pass  # python 3.2 not supported
import locale
import logging
import mimetypes
# needed on windows
mimetypes.add_type('text/x-python', '.py')
mimetypes.add_type('text/xml', '.ui')
import os
from pyqode.core.api.decoration import TextDecoration
from pyqode.core.api.manager import Manager
from pyqode.core.api.utils import TextHelper
from pyqode.qt import QtCore, QtGui, QtWidgets
from pyqode.core.cache import Cache


def _logger():
    return logging.getLogger(__name__)


class FileManager(Manager):
    """
    Helps manage file operations:
        - opening and saving files
        - providing file icon
        - detecting mimetype

    Example of usage::

        editor = CodeEdit()
        assert editor.file.path == ''
        # open a file with default locale encoding or using the cached one.
        editor.open(__file__)
        assert editor.file.path == __file__
        print(editor.file.encoding)

        # reload with another encoding
        editor.open(__file__, encoding='cp1252', use_cached_encoding=False)
        assert editor.file.path == __file__
        editor.file.encoding == 'cp1252'

    """
    @property
    def path(self):
        """ Gets the file path """
        if self._path:
            return os.path.normpath(self._path)
        return ''

    @property
    def name(self):
        """ Gets the file base name """
        return os.path.split(self.path)[1]

    @property
    def extension(self):
        """ Gets the file path """
        return os.path.splitext(self.path)[1]

    @property
    def dirname(self):
        """ Gets the file directory name """
        return os.path.dirname(self._path)

    @property
    def encoding(self):
        """ Gets the file encoding """
        return self._encoding

    @property
    def icon(self):
        """ Gets the file icon, provided by _get_icon """
        return self._get_icon()

    def _get_icon(self):
        return QtWidgets.QFileIconProvider().icon(QtCore.QFileInfo(self.path))

    def __init__(self, editor, replace_tabs_by_spaces=True):
        """
        :param editor: Code edit instance to work on.
        :param replace_tabs_by_spaces: True to replace tabs by spaces on
            load/save.
        """
        super(FileManager, self).__init__(editor)
        self._path = ''
        #: File mimetype
        self.mimetype = ''
        #: store the last file encoding used to open or save the file.
        self._encoding = locale.getpreferredencoding()
        #: True to replace tabs by spaces
        self.replace_tabs_by_spaces = replace_tabs_by_spaces
        #: Opening flag. Set to true during the opening of a file.
        self.opening = False
        #: Saving flag. Set to while saving the editor content to a file.
        self.saving = True
        #: If True, the file is saved to a temporary file first. If the save
        #: went fine, the temporary file is renamed to the final filename.
        self.safe_save = True
        #: True to clean trailing whitespaces of changed lines. Default is
        #: True
        self.clean_trailing_whitespaces = True
        #: True to restore cursor position (if the document has already been
        # opened once).
        self.restore_cursor = True

    @staticmethod
    def get_mimetype(path):
        """
        Guesses the mime type of a file. If mime type cannot be detected, plain
        text is assumed.

        :param path: path of the file
        :return: the corresponding mime type.
        """
        filename = os.path.split(path)[1]
        _logger().debug('detecting mimetype for %s', filename)
        mimetype = mimetypes.guess_type(filename)[0]
        if mimetype is None:
            mimetype = 'text/x-plain'
        _logger().debug('mimetype detected: %s', mimetype)
        return mimetype

    def open(self, path, encoding=None, use_cached_encoding=True):
        """
        Open a file and set its content on the editor widget.

        pyqode does not try to guess encoding. It's up to the client code to
        handle encodings. You can either use a charset detector to detect
        encoding or rely on a settings in your application. It is also up to
        you to handle UnicodeDecodeError, unless you've added
        class:`pyqode.core.panels.EncodingPanel` on the editor.

        pyqode automatically caches file encoding that you can later reuse it
        automatically.

        :param path: Path of the file to open.
        :param encoding: Default file encoding. Default is to use the locale
                         encoding.
        :param use_cached_encoding: True to use the cached encoding instead
            of ``encoding``. Set it to True if you want to force reload with a
            new encoding.

        :raises: UnicodeDecodeError in case of error if no EncodingPanel
            were set on the editor.
        """
        ret_val = False
        if encoding is None:
            encoding = locale.getpreferredencoding()
        self.opening = True
        settings = Cache()
        self._path = path
        # get encoding from cache
        if use_cached_encoding:
            try:
                cached_encoding = settings.get_file_encoding(path)
            except KeyError:
                pass
            else:
                encoding = cached_encoding
        # open file and get its content
        try:
            with open(path, 'r', encoding=encoding) as file:
                content = file.read()
        except (UnicodeDecodeError, UnicodeError) as e:
            try:
                from pyqode.core.panels import EncodingPanel
                panel = self.editor.panels.get(EncodingPanel)
            except KeyError:
                raise e  # panel not found, not automatic error management
            else:
                panel.on_open_failed(path, encoding)
        else:
            # success! Cache the encoding
            settings.set_file_encoding(path, encoding)
            self._encoding = encoding
            # replace tabs by spaces
            if self.replace_tabs_by_spaces:
                content = content.replace("\t", " " * self.editor.tab_length)
            # set plain text
            self.editor.setPlainText(
                content, self.get_mimetype(path), self.encoding)
            self.editor.setDocumentTitle(self.editor.file.name)
            ret_val = True
        self.opening = False
        if self.restore_cursor:
            self._restore_cached_pos()
        return ret_val

    def _restore_cached_pos(self):
        pos = Cache().get_cursor_position(self.path)
        TextHelper(self.editor).goto_line(pos[0], pos[1])
        QtCore.QTimer.singleShot(1, self.editor.centerCursor)

    def reload(self, encoding):
        """
        Reload the file with another encoding.

        :param encoding: the new encoding to use to reload the file.
        """
        assert os.path.exists(self.path)
        self.open(self.path, encoding=encoding,
                  use_cached_encoding=False)

    @staticmethod
    def _rm(tmp_path):
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    def _reset_selection(self, sel_end, sel_start):
        text_cursor = self.editor.textCursor()
        text_cursor.setPosition(sel_start)
        text_cursor.setPosition(sel_end, text_cursor.KeepAnchor)
        self.editor.setTextCursor(text_cursor)

    def _get_selection(self):
        sel_start = self.editor.textCursor().selectionStart()
        sel_end = self.editor.textCursor().selectionEnd()
        return sel_end, sel_start

    def save(self, path=None, encoding=None, fallback_encoding=None):
        """
        Save the editor content to a file.

        :param path: optional file path. Set it to None to save using the
                     current path (save), set a new path to save as.
        :param encoding: optional encoding, will use the current
                         file encoding if None.
        :param fallback_encoding: Fallback encoding to use in case of encoding
            error. None to use the locale preferred encoding

        """
        if fallback_encoding is None:
            fallback_encoding = locale.getpreferredencoding()
        self.saving = True
        _logger().debug(
            "saving %r to %r with %r encoding", self.path, path, encoding)
        if path is None:
            if self.path:
                path = self.path
            else:
                _logger().debug(
                    'failed to save file, path argument cannot be None if '
                    'FileManager.path is also None')
                return False
        # use cached encoding if None were specified
        if encoding is None:
            encoding = self._encoding
        self.editor.text_saving.emit(str(path))
        # remember cursor position (clean_document might mess up the
        # cursor pos)
        if self.clean_trailing_whitespaces:
            sel_end, sel_start = self._get_selection()
            TextHelper(self.editor).clean_document()
        plain_text = self.editor.toPlainText()
        # perform a safe save: we first save to a temporary file, if the save
        # succeeded we just rename the temporary file to the final file name
        # and remove it.
        if self.safe_save:
            tmp_path = path + '~'
        else:
            tmp_path = path
        try:
            _logger().debug('saving editor content to temp file: %s', path)
            with open(tmp_path, 'w', encoding=encoding) as file:
                file.write(plain_text)
        except UnicodeEncodeError:
            # fallback to utf-8 in case of error.
            with open(tmp_path, 'w', encoding=fallback_encoding) as file:
                file.write(plain_text)
        except (IOError, OSError) as e:
            self._rm(tmp_path)
            self.saving = False
            self.editor.text_saved.emit(str(path))
            raise e
        else:
            _logger().debug('save to temp file succeeded')
            Cache().set_file_encoding(path, encoding)
            self._encoding = encoding
            if self.safe_save:
                # remove path and rename temp file, if safe save is on
                _logger().debug('rename %s to %s', tmp_path, path)
                self._rm(path)
                os.rename(tmp_path, path)
                self._rm(tmp_path)
            # reset dirty flags
            self.editor._original_text = plain_text
            self.editor.document().setModified(False)
            # remember path for next save
            self._path = os.path.normpath(path)
            # reset selection
            if self.clean_trailing_whitespaces:
                if sel_start != sel_end:
                    self._reset_selection(sel_end, sel_start)
        self.editor.text_saved.emit(str(path))
        self.saving = False

    def close(self, clear=True):
        """
        Close the file open in the editor:
            - clear editor content
            - reset file attributes to their default values

        :param clear: True to clear the editor content. Default is True.
        """
        Cache().set_cursor_position(
            self.path, TextHelper(self.editor).cursor_position())
        self.editor._original_text = ''
        if clear:
            self.editor.clear()
        self._path = ''
        self.mimetype = ''
        self._encoding = locale.getpreferredencoding()

    def clone_settings(self, original):
        self.replace_tabs_by_spaces = original.replace_tabs_by_spaces
        self.safe_save = original.replace_tabs_by_spaces
        self.clean_trailing_whitespaces = original.clean_trailing_whitespaces
        self.restore_cursor = original.restore_cursor
