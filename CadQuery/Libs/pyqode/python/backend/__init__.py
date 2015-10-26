# -*- coding: utf-8 -*-
"""
The backend package contains everything needed to implement the
server side of a python editor.

"""
from .workers import calltips
from .workers import defined_names
from .workers import goto_assignments
from .workers import icon_from_typename
from .workers import quick_doc
from .workers import run_pyflakes
# for backward compatibility, will be removed in a future release
from .workers import run_pyflakes as run_frosted
from .workers import run_pep8
from .workers import JediCompletionProvider


__all__ = [
    'calltips',
    'defined_names',
    'goto_assignments',
    'icon_from_typename',
    'quick_doc',
    'run_pyflakes',
    'run_frosted',
    'run_pep8',
    'JediCompletionProvider'
]
