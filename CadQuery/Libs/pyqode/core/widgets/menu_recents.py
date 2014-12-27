"""
Provides a menu that display the list of recent files and a RecentFilesManager
which use your application's QSettings to store the list of recent files.

"""
import os
from pyqode.qt import QtCore, QtGui, QtWidgets


class RecentFilesManager(QtCore.QObject):
    """
    Manages a list of recent files. The list of files is stored in your
    application QSettings.

    """
    #: Maximum number of files kept in the list.
    max_recent_files = 15
    updated = QtCore.Signal()

    def __init__(self, organisation, application):
        super(RecentFilesManager, self).__init__()
        self._settings = QtCore.QSettings(organisation, application)

    def clear(self):
        """ Clears recent files in QSettings """
        self.set_value('list', [])
        self.updated.emit()

    def remove(self, filename):
        """
        Remove a file path from the list of recent files.
        :param filename: Path of the file to remove
        """
        files = self.get_value('list', [])
        files.remove(filename)
        self.set_value('list', files)
        self.updated.emit()

    def get_value(self, key, default=None):
        """
        Reads value from QSettings
        :param key: value key
        :param default: default value.
        :return: value
        """
        return [os.path.normpath(pth) for pth in
                self._settings.value('recent_files/%s' % key, default)]

    def set_value(self, key, value):
        """
        Set the recent files value in QSettings.
        :param key: value key
        :param value: new value
        """
        value = [os.path.normpath(pth) for pth in value]
        self._settings.setValue('recent_files/%s' % key, value)

    def get_recent_files(self):
        """
        Gets the list of recent files. (files that do not exists anymore
        are automatically filtered)
        """
        ret_val = []
        files = self.get_value('list', [])
        # empty list
        if files is None:
            files = []
        # single file
        if isinstance(files, str):
            files = [files]
        # filter files, remove files that do not exist anymore
        for file in files:
            if file is not None and os.path.exists(file):
                ret_val.append(file)
        return ret_val

    def open_file(self, file):
        """
        Adds a file to the list (and move it to the top of the list if the
        file already exists)

        :param file: file path to add the list of recent files.

        """
        files = self.get_recent_files()
        try:
            files.remove(file)
        except ValueError:
            pass
        files.insert(0, file)
        # discard old files
        del files[self.max_recent_files:]
        self.set_value('list', files)
        self.updated.emit()

    def last_file(self):
        """
        Returns the path to the last opened file.
        """
        files = self.get_recent_files()
        return files[0]


class MenuRecentFiles(QtWidgets.QMenu):
    """
    Menu that manage the list of recent files.

    To use the menu, simply pass connect to the open_requested signal.

    """
    #: Signal emitted when the user clicked on a recent file action.
    #: The parameter is the path of the file to open.
    open_requested = QtCore.Signal(str)
    clear_requested = QtCore.Signal()

    def __init__(self, parent, recent_files_manager=None,
                 title='Recent files',
                 icon_provider=None,
                 clear_icon=('edit-clear', '')):
        """
        :param organisation: name of your organisation as used for your own
                             QSettings
        :param application: name of your application as used for your own
                            QSettings
        :param parent: parent object

        :param icon_provider: Object that provides icon based on the file path.
        :type icon_provider: QtWidgets.QFileIconProvider

        :param clear_icon: Clear action icon. This parameter is a tuple made up
            of the icon theme name and the fallback icon path (from your
            resources). Default is None, clear action has no icons.
        """
        super(MenuRecentFiles, self).__init__(title, parent)
        if icon_provider is None:
            self.icon_provider = QtWidgets.QFileIconProvider()
        else:
            self.icon_provider = icon_provider
        self.clear_icon = clear_icon
        #: Recent files manager
        self.manager = recent_files_manager
        #: List of recent files actions
        self.recent_files_actions = []
        self.update_actions()

    def update_actions(self):
        """
        Updates the list of actions.
        """
        self.clear()
        self.recent_files_actions[:] = []
        for file in self.manager.get_recent_files():
            action = QtWidgets.QAction(self)
            action.setText(os.path.split(file)[1])
            action.setToolTip(file)
            action.setStatusTip(file)
            action.setData(file)
            action.setIcon(self.icon_provider.icon(QtCore.QFileInfo(file)))
            action.triggered.connect(self._on_action_triggered)
            self.addAction(action)
            self.recent_files_actions.append(action)
        self.addSeparator()
        action_clear = QtWidgets.QAction('Clear list', self)
        action_clear.triggered.connect(self.clear_recent_files)
        if self.clear_icon and len(self.clear_icon) == 2:
            action_clear.setIcon(QtGui.QIcon.fromTheme(
                self.clear_icon[0], QtGui.QIcon(self.clear_icon[1])))
        self.addAction(action_clear)

    def clear_recent_files(self):
        """ Clear recent files and menu. """
        self.manager.clear()
        self.update_actions()
        self.clear_requested.emit()

    def _on_action_triggered(self):
        """
        Emits open_requested when a recent file action has been triggered.
        """
        action = self.sender()
        assert isinstance(action, QtWidgets.QAction)
        path = action.data()
        self.open_requested.emit(path)
        self.update_actions()
