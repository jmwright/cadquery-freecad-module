"""
This module contains the modes controller.
"""
import logging
from pyqode.core.api.manager import Manager


def _logger():
    """ Returns module's logger """
    return logging.getLogger(__name__)


class ModesManager(Manager):
    """
    Manages the list of modes of the code edit widget.

    """
    def __init__(self, editor):
        super(ModesManager, self).__init__(editor)
        self._modes = {}

    def append(self, mode):
        """
        Adds a mode to the editor.

        :param mode: The mode instance to append.

        """
        _logger().debug('adding mode %r', mode.name)
        self._modes[mode.name] = mode
        mode.on_install(self.editor)
        return mode

    def remove(self, name_or_klass):
        """
        Removes a mode from the editor.

        :param name_or_klass: The name (or class) of the mode to remove.
        :returns: The removed mode.
        """
        _logger().debug('removing mode %r', name_or_klass)
        mode = self.get(name_or_klass)
        mode.on_uninstall()
        self._modes.pop(mode.name)
        return mode

    def clear(self):
        """
        Removes all modes from the editor. All modes are removed from list
        and deleted.

        """
        while len(self._modes):
            key = list(self._modes.keys())[0]
            mode = self.remove(key)
            del mode

    def get(self, name_or_klass):
        """
        Gets a mode by name (or class)

        :param name_or_klass: The name or the class of the mode to get
        :type name_or_klass: str or type
        :rtype: pyqode.core.api.Mode
        """
        if not isinstance(name_or_klass, str):
            name_or_klass = name_or_klass.__name__
        return self._modes[name_or_klass]

    def __len__(self):
        return len(list(self._modes.values()))

    def __iter__(self):
        """
        Returns the list of modes.

        :return:
        """
        return iter([v for k, v in sorted(self._modes.items())])
