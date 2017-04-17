# -*- coding: utf-8 -*-
"""
This module contains the pyFlakes checker mode
"""
from pyqode.core.modes import CheckerMode
from pyqode.python.backend.workers import run_pep8


class PEP8CheckerMode(CheckerMode):
    """
    This checker mode runs pep8.py on the fly to check your python style.
    """
    def __init__(self):
        CheckerMode.__init__(self, run_pep8)
