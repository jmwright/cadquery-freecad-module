# -*- coding: utf-8 -*-
"""
This packages contains the python specific panels:

    - QuickDocPanel: show docstring of functions/classes.
    - SymbolBrowserPanel: combo box that shows the symbols
      in the current document.

"""
from pyqode.python.panels.symbol_browser import SymbolBrowserPanel
from pyqode.python.panels.quick_doc import QuickDocPanel


try:
    # load pyqode.python resources (code completion icons)
    from pyqode.python._forms import pyqode_python_icons_rc  # DO NOT REMOVE!!!
except ImportError:
    # PyQt/PySide might not be available for the interpreter that run the
    # backend
    pass


__all__ = [
    'QuickDocPanel',
    'SymbolBrowserPanel',
]
