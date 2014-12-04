# -*- coding: utf-8 -*-
"""
This module contains the pyFlakes checker mode
"""
from pyqode.core.modes import CheckerMode
from pyqode.python.backend.workers import run_frosted


class FrostedCheckerMode(CheckerMode):
    """ Runs pyflakes on you code while you're typing

    This checker mode runs pyflakes on the fly to check your python syntax.
    """
    def __init__(self):
        super(FrostedCheckerMode, self).__init__(run_frosted, delay=1200)
