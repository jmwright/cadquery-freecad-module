# -*- coding: utf-8 -*-
"""
This file contains all the pyQode QtDesigner plugins.

Installation:
==================

run designer.pyw (Qt Designer must be installed on your system and must be
in your path on Windows)
"""
# This only works with PyQt, PySide does not support the QtDesigner module
from pyqode.python.widgets.code_edit import PyCodeEdit
from pyqode.core._designer_plugins import WidgetPlugin


class PyCodeEditPlugin(WidgetPlugin):
    def klass(self):
        return PyCodeEdit

    def objectName(self):
        return 'pyCodeEdit'
