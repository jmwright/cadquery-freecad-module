# -*- coding: utf-8 -*-
"""
This package contains a series of python specific modes (calltips,
autoindent, code linting,...).

"""
from .autocomplete import PyAutoCompleteMode
from .autoindent import PyAutoIndentMode
from .calltips import CalltipsMode
from .comments import CommentsMode
from .document_analyser import DocumentAnalyserMode
from .frosted_checker import FrostedCheckerMode
from .goto_assignements import Assignment
from .goto_assignements import GoToAssignmentsMode
from .indenter import PyIndenterMode
from .sh import PythonSH
from .pep8_checker import PEP8CheckerMode


try:
    # load pyqode.python resources (code completion icons)
    from pyqode.python._forms import pyqode_python_icons_rc  # DO NOT REMOVE!!!
except ImportError:
    # PyQt/PySide might not be available for the interpreter that run the
    # backend
    pass


__all__ = [
    'Assignment',
    'CalltipsMode',
    'CommentsMode',
    'DocumentAnalyserMode',
    'FrostedCheckerMode',
    'GoToAssignmentsMode',
    'PEP8CheckerMode',
    'PyAutoCompleteMode',
    'PyAutoIndentMode',
    'PyIndenterMode',
    'PythonSH',
]
