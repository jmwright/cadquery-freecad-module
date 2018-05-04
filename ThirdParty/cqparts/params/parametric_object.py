
from importlib import import_module

from .parameter import Parameter

from .. import __version__
from ..errors import ParameterError

import logging
log = logging.getLogger(__name__)


class ParametricObject(object):
    """
    Parametric objects may be defined like so:

    .. doctest::

        >>> from cqparts.params import (
        ...     ParametricObject,
        ...     PositiveFloat, IntRange,
        ... )

        >>> class Foo(ParametricObject):
        ...     x = PositiveFloat(5)
        ...     i = IntRange(1, 10, 3)  # between 1 and 10, defaults to 3
        ...     blah = 100

        >>> a = Foo(i=8)
        >>> (a.x, a.i)
        (5.0, 8)

        >>> a = Foo(i=11) # raises exception # doctest: +SKIP
        ParameterError: value of 11 outside the range {1, 10}

        >>> a = Foo(z=1)  # raises exception # doctest: +SKIP
        ParameterError: <class 'Foo'> does not accept parameter(s): z

        >>> a = Foo(x='123', i='2')
        >>> (a.x, a.i)
        (123.0, 2)

        >>> a = Foo(blah=200)  # raises exception, parameters must be Parameter types # doctest: +SKIP
        ParameterError: <class 'Foo'> does not accept any of the parameters: blah

        >>> a = Foo(x=None)  # a.x is None, a.i=3
        >>> (a.x, a.i)
        (None, 3)

    Internally to the object, parameters may be accessed simply with self.x, self.i
    These will always return the type defined

    """
    def __init__(self, **kwargs):
        # get all available parameters (recurse through inherited classes)
        params = self.class_params(hidden=True)

        # parameters explicitly defined during intantiation
        defined_params = set(kwargs.keys())

        # only accept a subset of params
        invalid_params = defined_params - set(params.keys())
        if invalid_params:
            raise ParameterError("{cls} does not accept parameter(s): {keys}".format(
                cls=repr(type(self)),
                keys=', '.join(sorted(invalid_params)),
            ))

        # Cast parameters into this instance
        for (name, param) in params.items():
            value = param.default
            if name in kwargs:
                value = param.cast(kwargs[name])
            setattr(self, name, value)

        self.initialize_parameters()

    @classmethod
    def class_param_names(cls, hidden=True):
        """
        Return the names of all class parameters.

        :param hidden: if ``False``, excludes parameters with a ``_`` prefix.
        :type hidden: :class:`bool`
        :return: set of parameter names
        :rtype: :class:`set`
        """
        param_names = set(
            k for (k, v) in cls.__dict__.items()
            if isinstance(v, Parameter)
        )
        for parent in cls.__bases__:
            if hasattr(parent, 'class_param_names'):
                param_names |= parent.class_param_names(hidden=hidden)

        if not hidden:
            param_names = set(n for n in param_names if not n.startswith('_'))
        return param_names

    @classmethod
    def class_params(cls, hidden=True):
        """
        Gets all class parameters, and their :class:`Parameter` instances.

        :return: dict of the form: ``{<name>: <Parameter instance>, ... }``
        :rtype: :class:`dict`

        .. note::

            The :class:`Parameter` instances returned do not have a value, only
            a default value.

            To get a list of an **instance's** parameters and values, use
            :meth:`params` instead.

        """
        param_names = cls.class_param_names(hidden=hidden)
        return dict(
            (name, getattr(cls, name))
            for name in param_names
        )

    def params(self, hidden=True):
        """
        Gets all instance parameters, and their *cast* values.

        :return: dict of the form: ``{<name>: <value>, ... }``
        :rtype: :class:`dict`
        """
        param_names = self.class_param_names(hidden=hidden)
        return dict(
            (name, getattr(self, name))
            for name in param_names
        )

    def __repr__(self):
        # Returns string of the form:
        #   <ClassName: diameter=3.0, height=2.0, twist=0.0>
        params = self.params(hidden=False)
        return "<{cls}: {params}>".format(
            cls=type(self).__name__,
            params=", ".join(
                "%s=%r" % (k, v)
                for (k, v) in sorted(params.items(), key=lambda x: x[0])  # sort by name
            ),
        )

    def initialize_parameters(self):
        """
        A palce to set default parameters more intelegently than just a
        simple default value (does nothing by default)

        :return: ``None``

        Executed just prior to exiting the :meth:`__init__` function.

        When overriding, strongly consider calling :meth:`super`.

        """
        pass

    # Serialize / Deserialize
    def serialize(self):
        """
        Encode a :class:`ParametricObject` instance to an object that can be
        encoded by the :mod:`json` module.

        :return: a dict of the format:
        :rtype: :class:`dict`

        ::

            {
                'lib': {  # library information
                    'name': 'cqparts',
                    'version': '0.1.0',
                },
                'class': {  # importable class
                    'module': 'yourpartslib.submodule',  # module containing class
                    'name': 'AwesomeThing',  # class being serialized
                },
                'params': {  # serialized parameters of AwesomeThing
                    'x': 10,
                    'y': 20,
                }
            }

        value of ``params`` key comes from :meth:`serialize_parameters`

        .. important::

            Serialize pulls the class name from the classes ``__name__`` parameter.

            This must be the same name of the object holding the class data, or
            the instance cannot be re-instantiated by :meth:`deserialize`.

        **Examples (good / bad)**

        .. doctest::

            >>> from cqparts.params import ParametricObject, Int

            >>> # GOOD Example
            >>> class A(ParametricObject):
            ...     x = Int(10)
            >>> A().serialize()['class']['name']
            'A'

            >>> # BAD Example
            >>> B = type('Foo', (ParametricObject,), {'x': Int(10)})
            >>> B().serialize()['class']['name']  # doctest: +SKIP
            'Foo'

        In the second example, the classes import name is expected to be ``B``.
        But instead, the *name* ``Foo`` is recorded. This missmatch will be
        irreconcilable when attempting to :meth:`deserialize`.
        """
        return {
            # Encode library information (future-proofing)
            'lib': {
                'name': 'cqparts',
                'version': __version__,
            },
            # class & name record, for automated import when decoding
            'class': {
                'module': type(self).__module__,
                'name': type(self).__name__,
            },
            'params': self.serialize_parameters(),
        }

    def serialize_parameters(self):
        """
        Get the parameter data in its serialized form.

        Data is serialized by each parameter's :meth:`Parameter.serialize`
        implementation.

        :return: serialized parameter data in the form: ``{<name>: <serial data>, ...}``
        :rtype: :class:`dict`
        """

        # Get parameter data
        class_params = self.class_params()
        instance_params = self.params()

        # Serialize each parameter
        serialized = {}
        for name in class_params.keys():
            param = class_params[name]
            value = instance_params[name]
            serialized[name] = param.serialize(value)
        return serialized

    @staticmethod
    def deserialize(data):
        """
        Create instance from serial data
        """
        # Import module & get class
        try:
            module = import_module(data.get('class').get('module'))
            cls = getattr(module, data.get('class').get('name'))
        except ImportError:
            raise ImportError("No module named: %r" % data.get('class').get('module'))
        except AttributeError:
            raise ImportError("module %r does not contain class %r" % (
                data.get('class').get('module'),
                data.get('class').get('name')
            ))

        # Deserialize parameters
        class_params = cls.class_params(hidden=True)
        params = dict(
            (name, class_params[name].deserialize(value))
            for (name, value) in data.get('params').items()
        )

        # Instantiate new instance
        return cls(**params)
