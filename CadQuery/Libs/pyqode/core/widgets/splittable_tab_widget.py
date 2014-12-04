"""
This module contains the splittable tab widget API
"""
import logging
import mimetypes
import os
import uuid
from pyqode.qt import QtCore, QtWidgets, QtGui
from pyqode.core.api import utils, CodeEdit, ColorScheme
from pyqode.core.dialogs import DlgUnsavedFiles
from .tab_bar import TabBar
from .code_edits import GenericCodeEdit, TextCodeEdit


def _logger():
    return logging.getLogger(__name__)


class DraggableTabBar(TabBar):
    """
    A draggable tab bar that allow to drag & drop tabs.

    Implementation is based on this qt article:
    http://www.qtcentre.org/wiki/index.php?title=Movable_Tabs
    """
    #: Signal emitted when a tab must be moved to the specified
    #: index (the tab might come from another tab bar (split)).
    tab_move_request = QtCore.Signal(QtWidgets.QWidget, int)

    def __init__(self, parent):
        super(DraggableTabBar, self).__init__(parent)
        self._pos = QtCore.QPoint()
        self.setAcceptDrops(True)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._pos = event.pos()  # _pos is a QPoint defined in the header
        super(DraggableTabBar, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # update tooltip with the tooltip of the tab under mouse cursor.
        index = self.tabAt(event.pos())
        tab = self.parent().widget(index)
        if tab is not None:
            tooltip = tab.toolTip()
            if not tooltip:
                try:
                    tooltip = tab.file.path
                except AttributeError:
                    pass
            self.setToolTip(tooltip)

        # If the distance is too small then return
        if (event.pos() - self._pos).manhattanLength() < \
                QtWidgets.QApplication.startDragDistance():
            return

        # If the left button isn't pressed anymore then return
        if not event.buttons() & QtCore.Qt.LeftButton:
            return

        drag = QtGui.QDrag(self)
        data = QtCore.QMimeData()
        data.tab = self.parent().currentWidget()
        data.widget = self
        # a crude way to distinguish tab-reodering drags from other drags
        data.setData("action", "tab-reordering")
        drag.setMimeData(data)
        drag.setPixmap(self.tabIcon(self.tabAt(event.pos())).pixmap(32, 32))
        drag.exec_()

    def dragEnterEvent(self, event):
        # Only accept if it's an tab-reordering request
        m = event.mimeData()
        formats = m.formats()
        if "action" in formats and m.data("action") == "tab-reordering":
            event.acceptProposedAction()

    def dropEvent(self, event):
        # drop a tab in a split (may be the same split or another one).
        m = event.mimeData()
        index = self.tabAt(event.pos())
        # Tell interested objects that a tab should be moved.
        if m.tab != self.parent().widget(index):
            self.tab_move_request.emit(m.tab, index)
        event.acceptProposedAction()


class BaseTabWidget(QtWidgets.QTabWidget):
    """
    Base tab widget class used by SplittableTabWidget. This tab widget adds a
    context menu to the tab bar that allow the user to:
        - split the current tab (horizontally or vertically)
        - close the current tab
        - close all tabs
        - close all other tabs

    The easiest way to add custom actions to the tab context menu is to
    override the ``_create_context_menu`` method.
    """
    #: Signal emitted when the last tab has been closed
    last_tab_closed = QtCore.Signal()
    #: Signal emitted when a tab has been closed
    tab_closed = QtCore.Signal(QtWidgets.QWidget)
    #: Signal emitted when the user clicked on split vertical or split
    #: horizontal
    #: **Parameters**:
    #: - widget: the widget to split
    #: - orientation: split orientation (horizontal/vertical)
    split_requested = QtCore.Signal(QtWidgets.QWidget, int)

    def __init__(self, parent):
        super(BaseTabWidget, self).__init__(parent)
        self._current = None
        self.currentChanged.connect(self._on_current_changed)
        self.tabCloseRequested.connect(self._on_tab_close_requested)

        tab_bar = DraggableTabBar(self)
        tab_bar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        tab_bar.customContextMenuRequested.connect(self._show_tab_context_menu)
        tab_bar.tab_move_request.connect(self._on_tab_move_request)
        self.setTabBar(tab_bar)
        self._context_mnu = self._create_tab_bar_menu()
        self.setAcceptDrops(True)

    def tab_under_menu(self):
        """
        Returns the tab that sits under the context menu.
        :return: QWidget
        """
        return self.tabBar().tabAt(self._menu_pos)

    @QtCore.Slot()
    def close(self):
        """
        Closes the active editor
        """
        self.tabCloseRequested.emit(self.tab_under_menu())

    @QtCore.Slot()
    def close_others(self):
        """
        Closes every editors tabs except the current one.
        """
        current_widget = self.widget(self.tab_under_menu())
        self._try_close_dirty_tabs(exept=current_widget)
        i = 0
        while self.count() > 1:
            widget = self.widget(i)
            if widget != current_widget:
                self.remove_tab(i)
            else:
                i = 1

    @QtCore.Slot()
    def close_all(self):
        """
        Closes all editors
        """
        if self._try_close_dirty_tabs():
            while self.count():
                widget = self.widget(0)
                self.remove_tab(0)
                self.tab_closed.emit(widget)
            return True
        return False

    def save_widget(self, editor):
        """
        Saves the widget. The base implementation does nothing.

        The function must return a bool that tells whether the save succeeded
        or not.

        :param editor: editor widget to save.
        """
        return True

    def _create_tab_bar_menu(self):
        _context_mnu = QtWidgets.QMenu()
        menu = QtWidgets.QMenu('Split', _context_mnu)
        menu.addAction('Split horizontally').triggered.connect(
            self._on_split_requested)
        menu.addAction('Split vertically').triggered.connect(
            self._on_split_requested)
        _context_mnu.addMenu(menu)
        _context_mnu.addSeparator()
        for name, slot in [('Close', self.close),
                           ('Close others', self.close_others),
                           ('Close all', self.close_all)]:
            qaction = QtWidgets.QAction(name, self)
            qaction.triggered.connect(slot)
            _context_mnu.addAction(qaction)
            self.addAction(qaction)
        return _context_mnu

    def _show_tab_context_menu(self, position):
        if self.count():
            self._menu_pos = position
            # self._context_mnu.popup(self.mapToGlobal(position))
            self._context_mnu.popup(self.tabBar().mapToGlobal(position))

    def _collect_dirty_tabs(self, skip=None):
        """
        Collects the list of dirty tabs

        :param skip: Tab to skip (used for close_others).
        """
        widgets = []
        filenames = []
        for i in range(self.count()):
            widget = self.widget(i)
            try:
                if widget.dirty and widget != skip:
                    widgets.append(widget)
                    filenames.append(widget.file.path)
            except AttributeError:
                pass
        return widgets, filenames

    def _try_close_dirty_tabs(self, exept=None):
        """
        Tries to close dirty tabs. Uses DlgUnsavedFiles to ask the user
        what he wants to do.
        """
        widgets, filenames = self._collect_dirty_tabs(skip=exept)
        if not len(filenames):
            return True
        dlg = DlgUnsavedFiles(self, files=filenames)
        if dlg.exec_() == dlg.Accepted:
            if not dlg.discarded:
                for item in dlg.listWidget.selectedItems():
                    filename = item.text()
                    widget = None
                    for widget in widgets:
                        if widget.path == filename:
                            break
                    if widget != exept:
                        self.save_widget(widget)
                        self.remove_tab(self.indexOf(widget))
            return True
        return False

    def _get_widget_path(self, widget):
        try:
            return widget.path
        except AttributeError:
            return ''

    def _on_tab_close_requested(self, index):
        widget = self.widget(index)
        dirty = False
        try:
            if widget.original is None:
                dirty = widget.dirty
        except AttributeError:
            pass
        if not dirty:
            self.remove_tab(index)
        else:
            # unsaved widget
            path = self._get_widget_path(widget)
            if not path:
                path = self.tabText(self.indexOf(widget))
            dlg = DlgUnsavedFiles(
                self, files=[path])
            if dlg.exec_() == dlg.Accepted:
                rm = True
                if not dlg.discarded:
                    rm = self.save_widget(widget)
                if rm:
                    self.remove_tab(index)
                    widget.deleteLater()

    @staticmethod
    def _close_widget(widget):
        """
        Closes the given widgets and handles cases where the widget has been
        clone or is a clone of another widget
        """
        if widget is None:
            return
        # handled cloned widgets
        clones = []
        if hasattr(widget, 'original') and widget.original:
            # cloned widget needs to be removed from the original
            widget.original.clones.remove(widget)
            try:
                widget.setDocument(None)
            except AttributeError:
                # not a QTextEdit/QPlainTextEdit
                pass
        elif hasattr(widget, 'clones'):
            clones = widget.clones
        try:
            # only clear current editor if it does not have any other clones
            widget.close(clear=len(clones) == 0)
        except (AttributeError, TypeError):
            # not a CodeEdit
            widget.close()
        return clones

    def _restore_original(self, clones):
        try:
            first = clones[0]
        except (IndexError, TypeError):
            # empty or None
            pass
        else:
            first.clones = clones[1:]
            first.original = None
            for c in first.clones:
                c.original = first

    def remove_tab(self, index):
        """
        Overrides removeTab to emit tab_closed and last_tab_closed signals.

        :param index: index of the tab to remove.
        """
        widget = self.widget(index)
        clones = self._close_widget(widget)
        self.tab_closed.emit(widget)
        self.removeTab(index)
        self._restore_original(clones)
        widget._original_tab_widget._tabs.remove(widget)
        if self.count() == 0:
            self.last_tab_closed.emit()

    def _on_split_requested(self):
        """
        Emits the split requested signal with the desired orientation.
        """
        orientation = self.sender().text()
        widget = self.widget(self.tab_under_menu())
        if 'horizontally' in orientation:
            self.split_requested.emit(
                widget, QtCore.Qt.Horizontal)
        else:
            self.split_requested.emit(
                widget, QtCore.Qt.Vertical)

    def _on_current_changed(self, index):
        tab = self.widget(index)
        if tab:
            tab.setFocus()

    def _on_tab_move_request(self, widget, new_index):
        parent = widget.parent_tab_widget
        index = parent.indexOf(widget)
        text = parent.tabText(index)
        icon = parent.tabIcon(index)
        parent.removeTab(index)
        widget.parent_tab_widget = self
        self.insertTab(new_index, widget, icon, text)
        self.setCurrentIndex(new_index)
        widget.setFocus()
        if parent.count() == 0:
            parent.last_tab_closed.emit()

    def dragEnterEvent(self, event):
        # Only accept if it's an tab-reordering request
        m = event.mimeData()
        formats = m.formats()
        if "action" in formats and m.data("action") == "tab-reordering":
            event.acceptProposedAction()

    def dropEvent(self, event):
        m = event.mimeData()
        index = self.tabBar().tabAt(event.pos())
        # Tell interested objects that a tab should be moved.
        if m.tab != self.widget(index):
            self._on_tab_move_request(m.tab, index)
            event.acceptProposedAction()

    def addTab(self, tab, *args):
        """
        Adds a tab to the tab widget, this function set the parent_tab_widget
        attribute on the tab instance.
        """
        tab.parent_tab_widget = self
        super(BaseTabWidget, self).addTab(tab, *args)


class SplittableTabWidget(QtWidgets.QSplitter):
    """
    A splittable tab widget. The widget is implemented as a splitter which
    contains a main tab widget and a collection of child SplittableTabWidget.

    Widgets added to the the tab widget **must** have a ``split`` method which
    returns a clone of the widget instance.

    You can add new tabs to the main tab widget by using the ``add_tab``
    method. Tabs are always closable.

    To change the underlying tab widget class, just set the
    ``tab_widget_klass`` class attribute.

    The splittable tab widget works with any kind of widget. There is a
    specialisation made specifically for managing a collection code editor
    widgets: SplittableCodeEditTabWidget.

    The implementation uses duck typing and will automatically show a dialog
    when closing an editor which has a ``dirty`` property. To actually save the
    widget, you must reimplement :meth:`SplittableTabWidget.save_widget``.
    """
    #: Signal emitted when the last tab has been closed.
    last_tab_closed = QtCore.Signal(QtWidgets.QSplitter)
    #: Signal emitted when the active tab changed (takes child tab widgets
    #: into account). Parameter is the new tab widget.
    current_changed = QtCore.Signal(QtWidgets.QWidget)

    #: underlying tab widget class
    tab_widget_klass = BaseTabWidget

    def __init__(self, parent=None, root=True):
        super(SplittableTabWidget, self).__init__(parent)
        self.child_splitters = []
        self.main_tab_widget = self.tab_widget_klass(self)
        self.main_tab_widget.last_tab_closed.connect(
            self._on_last_tab_closed)
        self.main_tab_widget.split_requested.connect(self.split)
        self.addWidget(self.main_tab_widget)
        self._parent_splitter = None
        self._current = None
        self.root = root
        if root:
            QtWidgets.QApplication.instance().focusChanged.connect(
                self._on_focus_changed)
        self._uuid = uuid.uuid1()
        self._tabs = []

    def add_tab(self, tab, title='', icon=None):
        """
        Adds a tab to main tab widget.

        :param tab: Widget to add as a new tab of the main tab widget.
        :param title: Tab title
        :param icon: Tab icon
        """
        if icon:
            tab._icon = icon
        if not hasattr(tab, 'clones'):
            tab.clones = []
        if not hasattr(tab, 'original'):
            tab.original = None
        if icon:
            self.main_tab_widget.addTab(tab, icon, title)
        else:
            self.main_tab_widget.addTab(tab, title)
        self.main_tab_widget.setCurrentIndex(
            self.main_tab_widget.indexOf(tab))
        self.main_tab_widget.show()
        tab._uuid = self._uuid
        tab.horizontalScrollBar().setValue(0)
        tab.setFocus()
        tab._original_tab_widget = self
        self._tabs.append(tab)
        self._on_focus_changed(None, tab)

    def _make_splitter(self):
        splitter = None
        for widget in reversed(self.child_splitters):
            if widget.parent() is None:
                widget.setParent(self)
                splitter = widget
                break
        if splitter is None:
            splitter = self.__class__(self, root=False)
        return splitter

    def split(self, widget, orientation):
        """
        Split the the current widget in new SplittableTabWidget.

        :param widget: widget to split
        :param orientation: orientation of the splitter
        :return: the new splitter
        """
        if orientation == int(QtCore.Qt.Horizontal):
            orientation = QtCore.Qt.Horizontal
        else:
            orientation = QtCore.Qt.Vertical
        self.setOrientation(orientation)
        splitter = self._make_splitter()
        splitter.show()
        self.addWidget(splitter)
        self.child_splitters.append(splitter)
        if widget.original:
            base = widget.original
        else:
            base = widget
        clone = base.split()
        if clone not in base.clones:
            # code editors maintain the list of clones internally but some
            # other widgets (user widgets) might not.
            base.clones.append(clone)
        clone.original = base
        splitter._parent_splitter = self
        splitter.last_tab_closed.connect(self._on_last_child_tab_closed)
        if hasattr(base, '_icon'):
            icon = base._icon
        else:
            icon = None
        # same group of tab splitter (user might have a group for editors and
        # another group for consoles or whatever).
        splitter._uuid = self._uuid
        splitter.add_tab(clone, title=self.main_tab_widget.tabText(
            self.main_tab_widget.indexOf(widget)), icon=icon)
        self.setSizes([1 for i in range(self.count())])
        return splitter

    def has_children(self):
        """
        Checks if there are children tab widgets.
        :return: True if there is at least one tab in the children tab widget.
        """
        for splitter in self.child_splitters:
            if splitter.has_children():
                return splitter
        return self.main_tab_widget.count() != 0

    def current_widget(self):
        """
        Returns a reference to the current widget, i.e. the last widget that
        got the focus.
        :return: QWidget
        """
        return self._current

    def widgets(self, include_clones=False):
        """
        Recursively gets the list of widgets.

        :param include_clones: True to retrieve all tabs, including clones,
            otherwise only original widgets are returned.
        """
        widgets = []
        for i in range(self.main_tab_widget.count()):
            widget = self.main_tab_widget.widget(i)
            try:
                if widget.original is None or include_clones:
                    widgets.append(widget)
            except AttributeError:
                pass
        for child in self.child_splitters:
            widgets += child.widgets(include_clones=include_clones)
        return widgets

    def _on_last_tab_closed(self, *args):
        has_children = self.has_children()
        if has_children:
            # hide the tab widget if there is not tabs
            if not self.main_tab_widget.count():
                self.main_tab_widget.hide()
        else:
            if self.root:
                # ensure root is visible when there are no children
                self.show()
                self.main_tab_widget.show()
            else:
                # hide ourselves (we don't have any other tabs or children)
                self._remove_from_parent()
        if not self.has_children():
            self.last_tab_closed.emit(self)

    def _on_focus_changed(self, old, new):
        try:
            result = new._uuid == self._uuid
        except (AttributeError, TypeError):
            pass
        else:
            if result:
                if new != self._current:
                    self._on_current_changed(new)

    def _on_current_changed(self, new):
        old = self._current
        self._current = new
        _logger().info(
            'current tab changed (old=%r, new=%r)', old, new)
        self.current_changed.emit(new)
        return old, new

    def _remove_from_parent(self):
        self.hide()
        self.setParent(None)
        self.main_tab_widget.hide()
        if not self.root:
            self._parent_splitter.child_splitters.remove(self)
            self._parent_splitter = None

    def _on_last_child_tab_closed(self):
        if not self.has_children():
            self.last_tab_closed.emit(self)
            if self.root:
                self.show()
                self.main_tab_widget.show()
            else:
                self._remove_from_parent()

    def count(self):
        """
        Returns the number of widgets currently displayed (takes child splits
        into account).
        """
        c = self.main_tab_widget.count()
        for child in self.child_splitters:
            c += child.count()
        return c


class CodeEditTabWidget(BaseTabWidget):
    """
    Tab widget specialised to hold pyqode's code editor widgets.

    It will manage the saving of editors
    """
    default_directory = os.path.expanduser('~')
    dirty_changed = QtCore.Signal(bool)

    @classmethod
    @utils.memoized
    def get_filter(cls, mimetype):
        """
        Returns a filter string for the file dialog. The filter is based
        on the mime type.

        :param mimetype: path from which the filter must be derived.
        :return: Filter string
        """
        return '%s (*%s)' % (mimetype, mimetypes.guess_extension(mimetype))

    def addTab(self, widget, *args):
        """
        Re-implements addTab to connect to the dirty changed signal and setup
        some helper attributes.

        :param widget: widget to add
        :param args: optional addtional arguments (name and/or icon).
        """
        widget.dirty_changed.connect(self._on_dirty_changed)
        super(CodeEditTabWidget, self).addTab(widget, *args)

    def _on_dirty_changed(self, dirty):
        """
        Adds a star in front of a dirtt tab and emits dirty_changed.
        """
        widget = self.sender()
        if isinstance(widget, CodeEdit):
            parent = widget.parent_tab_widget
            index = parent.indexOf(widget)
            title = parent.tabText(index)
            title = title.replace('* ', '')
            if dirty:
                parent.setTabText(index, "* " + title)
            else:
                parent.setTabText(index, title)
            parent.dirty_changed.emit(dirty)

    @classmethod
    def _ask_path(cls, editor):
        """
        Shows a QFileDialog and ask for a save filename.

        :return: save filename
        """
        try:
            filter = cls.get_filter(editor.mimetypes[0])
        except IndexError:
            filter = 'All files (*)'
        return QtWidgets.QFileDialog.getSaveFileName(
            editor, 'Save file as', cls.default_directory, filter)

    @classmethod
    def save_widget(cls, editor):
        """
        Implements SplittableTabWidget.save_widget to actually save the
        code editor widget.

        If the editor.file.path is None or empty or the file does not exist,
        a save as dialog is shown (save as).

        :param editor: editor widget to save.
        :return: False if there was a problem saving the editor (e.g. the save
        as dialog has been canceled by the user, or a permission error,...)
        """
        if editor.original:
            editor = editor.original
        if editor.file.path is None or not os.path.exists(editor.file.path):
            # save as
            path, filter = cls._ask_path(editor)
            if not path:
                return False
            if not os.path.splitext(path)[1]:
                if len(editor.mimetypes):
                    path += mimetypes.guess_extension(editor.mimetypes[0])
            editor.file._path = path
        text = os.path.split(editor.file.path)[1]
        editor.file.save()
        tw = editor.parent_tab_widget
        tw.setTabText(tw.indexOf(editor), text)
        for clone in [editor] + editor.clones:
            if clone != editor:
                tw = clone.parent_tab_widget
                tw.setTabText(tw.indexOf(clone), text)
        return True

    def _get_widget_path(self, editor):
        return editor.file.path

    def _restore_original(self, clones):
        super(CodeEditTabWidget, self)._restore_original(clones)
        try:
            first = clones[0]
        except (IndexError, TypeError):
            # empty or None
            pass
        else:
            try:
                # remove original highlighter (otherwise we get a runtime error
                # saying the original c++ object has been deleted)
                new_sh = first.syntax_highlighter.__class__(
                    first.document(), color_scheme=ColorScheme(
                        first.syntax_highlighter.color_scheme.name))
                first.modes.remove(first.syntax_highlighter.name)
                first.modes.append(new_sh)
            except (AttributeError, TypeError):
                pass


class SplittableCodeEditTabWidget(SplittableTabWidget):
    """
    SplittableTabWidget specialised for CodeEdit and subclasses.

    Offers some convenience function for opening/saving files.

    The widget supports multiple type of code editors. Each editor type must
    be explicitly registered using ``register_editor``. If there is no
    registered editor for the given mime-type, ``fallback_editor`` is used.
    """
    #: uses a CodeEditTabWidget which is able to save code editor widgets.
    tab_widget_klass = CodeEditTabWidget

    #: the icon provider class to use when creating new document. Must be
    #: a subclass of QtWidgets.QFileIconProvider. By default, QFileIconProvider
    #: is used.
    icon_provider_klass = QtWidgets.QFileIconProvider

    #: Maps a mime-type with an editor type.
    #: This map is used to instantiate the proper editor type when
    #: opening/creating a document.
    editors = {mimetype: TextCodeEdit for mimetype in TextCodeEdit.mimetypes}

    #: Fallback editor is used in case not editors matching the requested
    #: mime-type could not be found in the editors map.
    #: By default the fallback_editor is a
    #: :class:`pyqode.core.widgets.GenericCodeEdit`
    fallback_editor = GenericCodeEdit

    #: signal emitted when the dirty_changed signal of the current editor
    #: has been emitted.
    dirty_changed = QtCore.Signal(bool)

    #: Store the number of new documents created, for internal use.
    _new_count = 0

    @classmethod
    def register_code_edit(cls, code_edit_class):
        """
        Register an additional code edit **class**
        :param code_edit_class: code edit class to regiter.
        """
        for mimetype in code_edit_class.mimetypes:
            if mimetype in cls.editors:
                _logger().warn('editor for mimetype already registered, '
                               'skipping')
            cls.editors[mimetype] = code_edit_class
        _logger().info('registered editors: %r', cls.editors)

    def save_current_as(self):
        """
        Save current widget as.
        """
        mem = self._current.file.path
        self._current.file._path = None
        CodeEditTabWidget.default_directory = os.path.dirname(mem)
        if not self.main_tab_widget.save_widget(self._current):
            self._current.file._path = mem
        CodeEditTabWidget.default_directory = os.path.expanduser('~')
        return self._current.file.path

    def save_current(self):
        """
        Save current editor. If the editor.file.path is None, a save as dialog
        will be shown.
        """
        self.main_tab_widget.save_widget(self._current)

    def save_all(self):
        """
        Save all editors.
        """
        for w in self.widgets():
            self.main_tab_widget.save_widget(w)

    def _create_code_edit(self, mimetype, *args, **kwargs):
        """
        Create a code edit instance based on the mimetype of the file to
        open/create.

        :type mimetype: mime type
        :return: CodeEdit instance
        """
        if mimetype in self.editors.keys():
            return self.editors[mimetype](
                *args, parent=self.main_tab_widget, **kwargs)
        return self.fallback_editor(parent=self.main_tab_widget)

    def create_new_document(self, base_name='New Document', extension='.txt'):
        """
        Creates a new document.

        The document name will be ``base_name + count + extension``

        :type base_name: Base name of the document. An int will be appended.
        :type extension: Document extension (must include the DOT)

        :return: The created code editor
        """
        SplittableCodeEditTabWidget._new_count += 1
        name = '%s%d%s' % (base_name, self._new_count, extension)
        tab = self._create_code_edit(self.guess_mimetype(name))
        tab.setDocumentTitle(name)
        self.add_tab(tab, title=name, icon=self._icon(name))
        return tab

    def guess_mimetype(self, path):
        if 'CMakeLists.txt' in path:
            return 'text/x-cmake-project'
        else:
            return mimetypes.guess_type(path)[0]

    @utils.with_wait_cursor
    def open_document(self, path, *args, **kwargs):
        """
        Opens a document.

        :type path: Path of the document to open

        :param args: additional args to pass to the widget constructor.
        :param kwargs: addtional keyword args to pass to the widget
                       constructor.
        :return: The created code editor
        """
        path = os.path.normpath(path)
        paths = []
        widgets = []
        for w in self.widgets(include_clones=False):
            if os.path.exists(w.file.path):
                # skip new docs
                widgets.append(w)
                paths.append(w.file.path)
        if path in paths:
            i = paths.index(path)
            w = widgets[i]
            tw = w.parent_tab_widget
            tw.setCurrentIndex(tw.indexOf(w))
            return w
        else:
            assert os.path.exists(path)
            name = os.path.split(path)[1]
            tab = self._create_code_edit(self.guess_mimetype(path),
                                         *args, **kwargs)
            tab.file.open(path)
            tab.setDocumentTitle(name)
            icon = self._icon(path)
            self.add_tab(tab, title=name, icon=icon)
            return tab

    def close_document(self, path):
        """
        Closes a text document.
        :param path: Path of the document to close.
        """
        to_close = []
        for widget in self.widgets(include_clones=True):
            if widget.file.path == path:
                to_close.append(widget)
        for widget in to_close:
            tw = widget.parent_tab_widget
            tw.remove_tab(tw.indexOf(widget))

    def rename_document(self, old_path, new_path):
        """
        Renames an already opened document (this will not rename the file,
        just update the file path and tab title).

        Use that function to update a file that has been renamed externally.

        :param old_path: old path (path of the widget to rename with
            ``new_path``
        :param new_path: new path that will be used to rename the tab.
        """
        to_rename = []
        title = os.path.split(new_path)[1]
        for widget in self.widgets(include_clones=True):
            if widget.file.path == old_path:
                to_rename.append(widget)
        for widget in to_rename:
            tw = widget.parent_tab_widget
            widget.file._path = new_path
            tw.setTabText(tw.indexOf(widget), title)

    def closeEvent(self, event):
        """
        Saves dirty editors on close and cancel the event if the user choosed
        to continue to work.

        :param event: close event
        """
        dirty_widgets = []
        for w in self.widgets(include_clones=False):
            if w.dirty:
                dirty_widgets.append(w)
        filenames = []
        for w in dirty_widgets:
            if os.path.exists(w.file.path):
                filenames.append(w.file.path)
            else:
                filenames.append(w.documentTitle())
        if len(filenames) == 0:
            self.close_all()
            return
        dlg = DlgUnsavedFiles(self, files=filenames)
        if dlg.exec_() == dlg.Accepted:
            if not dlg.discarded:
                for item in dlg.listWidget.selectedItems():
                    filename = item.text()
                    widget = None
                    for widget in dirty_widgets:
                        if widget.file.path == filename or \
                                widget.documentTitle() == filename:
                            break
                    tw = widget.parent_tab_widget
                    tw.save_widget(widget)
                    tw.remove_tab(tw.indexOf(widget))
            self.close_all()
        else:
            event.ignore()

    def close_all(self):
        for w in self.widgets(include_clones=True):
            tw = w.parent_tab_widget
            tw.remove_tab(tw.indexOf(w))

    def _icon(self, path):
        provider = self.icon_provider_klass()
        if not os.path.exists(path):
            return provider.icon(provider.File)
        return provider.icon(QtCore.QFileInfo(path))

    def _on_current_changed(self, new):
        old, new = super(
            SplittableCodeEditTabWidget, self)._on_current_changed(new)
        if new:
            new.dirty_changed.connect(self.dirty_changed.emit)
        self.dirty_changed.emit(new.dirty)
        return old, new
