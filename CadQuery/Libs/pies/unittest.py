from __future__ import absolute_import

import sys
from unittest import *

from ._utils import unmodified_isinstance

NativeTestCase = TestCase

if sys.version_info < (2, 7):
    skip = lambda why: (lambda func: 'skip')
    skipIf = lambda cond, why: (skip(why) if cond else lambda func: func)

    class TestCase(unmodified_isinstance(TestCase)):
        def assertIs(self, expr1, expr2, msg=None):
            if expr1 is not expr2:
                self.fail(msg or '%r is not %r' % (expr1, expr2))
