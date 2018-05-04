
import os
from time import time
from contextlib import contextmanager
import jinja2


class property_buffered(object):
    """
    Buffer the result of a method on the class instance, similar to python builtin
    ``@property``, but the result is kept in memory until it's explicitly deleted.

    .. doctest::

        >>> from cqparts.utils.misc import property_buffered
        >>> class A(object):
        ...     @property_buffered
        ...     def x(self):
        ...         print("x called")
        ...         return 100
        >>> a = A()
        >>> a.x
        x called
        100
        >>> a.x
        100
        >>> del a.x
        >>> a.x
        x called
        100

    Basis of class was sourced from the `funkybob/antfarm <https://github.com/funkybob/antfarm/blob/40a7cc450eba09a280b7bc8f7c68a807b0177c62/antfarm/utils/functional.py>`_ project.
    thanks to `@funkybob <https://github.com/funkybob>`_.
    """
    def __init__(self, getter, name=None):
        self.name = name or getter.__name__
        self.getter = getter
        self.__doc__ = getter.__doc__  # preserve sphinx autodoc docstring

    def __get__(self, instance, owner):
        if instance is None:  # pragma: no cover
            return self
        value = self.getter(instance)
        instance.__dict__[self.name] = value
        return value


def indicate_last(items):
    """
    iterate through list and indicate which item is the last, intended to
    assist tree displays of hierarchical content.

    :return: yielding (<bool>, <item>) where bool is True only on last entry
    :rtype: generator
    """
    last_index = len(items) - 1
    for (i, item) in enumerate(items):
        yield (i == last_index, item)


@contextmanager
def working_dir(path):
    initial_path = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(initial_path)


@contextmanager
def measure_time(log, name):
    start_time = time()
    yield
    taken = time() - start_time
    log.debug("    %-25s (took: %gms)", name, round(taken * 1000, 3))
