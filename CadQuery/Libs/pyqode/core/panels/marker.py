# -*- coding: utf-8 -*-
"""
This module contains the marker panel
"""
import logging
from pyqode.core.api import TextBlockUserData
from pyqode.core.api.panel import Panel
from pyqode.qt import QtCore, QtWidgets, QtGui
from pyqode.core.api.utils import DelayJobRunner, memoized, TextHelper


def _logger():
    """ Gets module's logger """
    return logging.getLogger(__name__)


class Marker(QtCore.QObject):
    """
    A marker is an icon draw on a marker panel at a specific line position and
    with a possible tooltip.
    """

    @property
    def position(self):
        """
        Gets the marker position (line number)
        :type: int
        """
        return self._position

    @property
    def icon(self):
        """
        Gets the icon file name. Read-only.
        """
        return self._icon

    @property
    def description(self):
        """ Gets the marker description. """
        return self._description

    def __init__(self, position, icon="", description="", parent=None):
        """
        :param position: The marker position/line number.
        :type position: int

        :param icon: the icon filename.
        :type icon: str

        :param parent: The optional parent object.
        :type parent: QtCore.QObject or None
        """
        QtCore.QObject.__init__(self, parent)
        #: The position of the marker (line number)
        self._position = position
        self._icon = icon
        self._description = description


class MarkerPanel(Panel):
    """
    General purpose marker panel.
    This panels takes care of drawing icons at a specific line number.

    Use addMarker, removeMarker and clearMarkers to manage the collection of
    displayed makers.

    You can create a user editable panel (e.g. a breakpoints panel) by using
    the following signals:

      - :attr:`pyqode.core.panels.MarkerPanel.add_marker_requested`
      - :attr:`pyqode.core.panels.MarkerPanel.remove_marker_requested`

    """
    #: Signal emitted when the user clicked in a place where there is no
    #: marker.
    add_marker_requested = QtCore.Signal(int)
    #: Signal emitted when the user clicked on an existing marker.
    remove_marker_requested = QtCore.Signal(int)

    def __init__(self):
        Panel.__init__(self)
        self._markers = []
        self._icons = {}
        self._previous_line = -1
        self.scrollable = True
        self._job_runner = DelayJobRunner(delay=100)
        self.setMouseTracking(True)
        self._to_remove = []

    def add_marker(self, marker):
        """
        Adds the marker to the panel.

        :param marker: Marker to add
        :type marker: pyqode.core.modes.Marker
        """
        key, val = self.make_marker_icon(marker.icon)
        if key and val:
            self._icons[key] = val
        self._markers.append(marker)
        doc = self.editor.document()
        assert isinstance(doc, QtGui.QTextDocument)
        block = doc.findBlockByLineNumber(marker.position - 1)
        user_data = block.userData()
        if user_data is None:
            user_data = TextBlockUserData()
            block.setUserData(user_data)
        marker.panel_ref = self
        user_data.markers.append(marker)
        self.repaint()

    @staticmethod
    @memoized
    def make_marker_icon(icon):
        """
        Make (and memoize) an icon from an icon filename.

        :param icon: Icon filename or tuple (to use a theme).
        """
        if isinstance(icon, tuple):
            return icon[0], QtGui.QIcon.fromTheme(
                icon[0], QtGui.QIcon(icon[1]))
        elif isinstance(icon, str):
            return icon, QtGui.QIcon(icon)
        else:
            return None, None

    def remove_marker(self, marker):
        """
        Removes a marker from the panel

        :param marker: Marker to remove
        :type marker: pyqode.core.Marker
        """
        self._markers.remove(marker)
        self._to_remove.append(marker)
        self.repaint()

    def clear_markers(self):
        """ Clears the markers list """
        while len(self._markers):
            self.remove_marker(self._markers[0])

    def marker_for_line(self, line):
        """
        Returns the marker that is displayed at the specified line number if
        any.

        :param line: The marker line.

        :return: Marker of None
        :rtype: pyqode.core.Marker
        """
        markers = []
        for marker in self._markers:
            if line == marker.position:
                markers.append(marker)
        return markers

    def sizeHint(self):
        """
        Returns the panel size hint. (fixed with of 16px)
        """
        metrics = QtGui.QFontMetricsF(self.editor.font())
        size_hint = QtCore.QSize(metrics.height(), metrics.height())
        if size_hint.width() > 16:
            size_hint.setWidth(16)
        return size_hint

    def paintEvent(self, event):
        Panel.paintEvent(self, event)
        painter = QtGui.QPainter(self)
        for top, block_nbr, block in self.editor.visible_blocks:
            user_data = block.userData()
            if hasattr(user_data, "markers"):
                markers = user_data.markers
                for i, marker in enumerate(markers):
                    if (hasattr(marker, 'panel_ref') and
                            marker.panel_ref == self):
                        # only draw our markers
                        if marker in self._to_remove:
                            try:
                                user_data.markers.remove(None)
                                self._to_remove.remove(marker)
                            except ValueError:
                                pass
                            continue
                        if marker and marker.icon:
                            rect = QtCore.QRect()
                            rect.setX(0)
                            rect.setY(top)
                            rect.setWidth(self.sizeHint().width())
                            rect.setHeight(self.sizeHint().height())
                            if isinstance(marker.icon, tuple):
                                key = marker.icon[0]
                            else:
                                key = marker.icon
                            if key not in self._icons:
                                key, val = self.make_marker_icon(marker.icon)
                                if key and val:
                                    self._icons[key] = val
                                else:
                                    continue
                            self._icons[key].paint(painter, rect)

    def mousePressEvent(self, event):
        # Handle mouse press:
        # - emit add marker signal if there were no marker under the mouse
        #   cursor
        # - emit remove marker signal if there were one or more markers under
        #   the mouse cursor.
        line = TextHelper(self.editor).line_nbr_from_position(event.pos().y())
        if self.marker_for_line(line):
            _logger().debug("remove marker requested")
            self.remove_marker_requested.emit(line)
        else:
            _logger().debug("add marker requested")
            self.add_marker_requested.emit(line)

    def mouseMoveEvent(self, event):
        # Requests a tooltip if the cursor is currently over a marker.
        line = TextHelper(self.editor).line_nbr_from_position(event.pos().y())
        markers = self.marker_for_line(line)
        text = '\n'.join([marker.description for marker in markers if
                          marker.description])
        if len(markers):
            if self._previous_line != line:
                top = TextHelper(self.editor).line_pos_from_number(
                    markers[0].position)
                if top:
                    self._job_runner.request_job(self._display_tooltip,
                                                 text, top)
        else:
            self._job_runner.cancel_requests()
        self._previous_line = line

    def leaveEvent(self, *args, **kwargs):
        """
        Hide tooltip when leaving the panel region.
        """
        QtWidgets.QToolTip.hideText()
        self._previous_line = -1

    def _display_tooltip(self, tooltip, top):
        """
        Display tooltip at the specified top position.
        """
        QtWidgets.QToolTip.showText(self.mapToGlobal(QtCore.QPoint(
            self.sizeHint().width(), top)), tooltip, self)
