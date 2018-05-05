
from .parameter import Parameter
from .types import NonNullParameter

# ------------ decorator(s) ---------------
def as_parameter(nullable=True, strict=True):
    """
    Decorate a container class as a functional :class:`Parameter` class
    for a :class:`ParametricObject`.

    :param nullable: if set, parameter's value may be Null
    :type nullable: :class:`bool`

    .. doctest::

        >>> from cqparts.params import as_parameter, ParametricObject

        >>> @as_parameter(nullable=True)
        ... class Stuff(object):
        ...     def __init__(self, a=1, b=2, c=3):
        ...         self.a = a
        ...         self.b = b
        ...         self.c = c
        ...     @property
        ...     def abc(self):
        ...         return (self.a, self.b, self.c)

        >>> class Thing(ParametricObject):
        ...     foo = Stuff({'a': 10, 'b': 100}, doc="controls stuff")

        >>> thing = Thing(foo={'a': 20})
        >>> thing.foo.a
        20
        >>> thing.foo.abc
        (20, 2, 3)
    """
    def decorator(cls):
        base_class = Parameter if nullable else NonNullParameter

        return type(cls.__name__, (base_class,), {
            # Preserve text for documentation
            '__name__': cls.__name__,
            '__doc__': cls.__doc__,
            '__module__': cls.__module__,
            # Sphinx doc type string
            '_doc_type': ":class:`{class_name} <{module}.{class_name}>`".format(
                class_name=cls.__name__, module=__name__
            ),
            #
            'type': lambda self, value: cls(**value)
        })


    return decorator
