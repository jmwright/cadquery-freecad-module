
import six

class Parameter(object):
    """
    Used to set parameters of a :class:`ParametricObject <parametric_object.ParametricObject>`.

    All instances of this class defined in a class' ``__dict__`` will be
    valid input to the object's constructor.

    **Creating your own Parameter**

    To create your own parameter type, inherit from this class and override
    the :meth:`type` method.

    To demonstrate, let's create a parameter that takes an integer, and
    multiplies it by 10.

    .. doctest::

        >>> from cqparts.params import Parameter
        >>> class Tens(Parameter):
        ...     _doc_type = ":class:`int`"
        ...     def type(self, value):
        ...         return int(value) * 10

    Now to use it in a :class:`ParametricObject <cqparts.params.parametric_object.ParametricObject>`

    .. doctest::

        >>> from cqparts.params import ParametricObject
        >>> class Foo(ParametricObject):
        ...     a = Tens(5, doc="a in groups of ten")
        ...     def bar(self):
        ...         print("a = %i" % self.a)

        >>> f = Foo(a=8)
        >>> f.bar()
        a = 80

    """

    def __init__(self, default=None, doc=None):
        """
        :param default: default value, will cast before storing
        """
        self.default = self.cast(default)
        self.doc = doc

    @classmethod
    def new(cls, default=None):
        """
        Create new instance of the parameter with a new default
        ``doc``

        :param default: new parameter instance default value
        """
        return cls(default=default)

    def cast(self, value):
        """
        First layer of type casting, used for high-level verification.

        If ``value`` is ``None``, :meth:`type` is not called to cast the value
        further.

        :param value: the value given to the :class:`ParametricObject <cqparts.params.parametric_object.ParametricObject>`'s constructor
        :return: ``value`` or ``None``
        :raises ParameterError: if type is invalid
        """
        if value is None:
            return None
        return self.type(value)

    def type(self, value):
        """
        Second layer of type casting, usually overridden to change the given
        ``value`` into the parameter's type.

        Casts given value to the type dictated by this parameter type.

        Raise a :class:`ParameterError` on errors.

        :param value: the value given to the :class:`ParametricObject <cqparts.params.parametric_object.ParametricObject>`'s constructor
        :return: ``value`` cast to parameter's type
        :raises ParameterError: if type is invalid
        """
        return value

    # sphinx documentation helpers
    def _param(self):
        # for a sphinx line:
        #   :param my_param: <return is published here>
        if not isinstance(self.doc, six.string_types):
            return "[no description]"
        return self.doc

    _doc_type = '[unknown]'

    def _type(self):
        # for a sphinx line:
        #   :type my_param: <return is published here>
        return self._doc_type

    # Serializing / Deserializing
    @classmethod
    def serialize(cls, value):
        r"""
        Converts value to something serializable by :mod:`json`.

        :param value: value to convert
        :return: :mod:`json` serializable equivalent

        By default, returns ``value``, to pass straight to :mod:`json`

        .. warning::

            :meth:`serialize` and :meth:`deserialize` **are not** symetrical.


        **Example of serializing then deserializing a custom object**

        Let's create our own ``Color`` class we'd like to represent as a
        parameter.

        .. doctest::

            >>> class Color(object):
            ...     def __init__(self, r, g, b):
            ...         self.r = r
            ...         self.g = g
            ...         self.b = b
            ...
            ...     def __eq__(self, other):
            ...         return (
            ...             type(self) == type(other) and \
            ...             self.r == other.r and \
            ...             self.g == other.g and \
            ...             self.b == other.b
            ...         )
            ...
            ...     def __repr__(self):
            ...         return "<Color: %i, %i, %i>" % (self.r, self.g, self.b)

            >>> from cqparts.params import Parameter
            >>> class ColorParam(Parameter):
            ...     _doc_type = ":class:`list`"  # for sphinx documentation
            ...     def type(self, value):
            ...         (r, g, b) = value
            ...         return Color(r, g, b)
            ...
            ...     @classmethod
            ...     def serialize(cls, value):
            ...         # the default serialize will fail, we know this
            ...         # because json.dumps(Color(0,0,0)) raises an exception
            ...         if value is None:  # parameter is nullable
            ...             return None
            ...         return [value.r, value.g, value.b]
            ...
            ...     @classmethod
            ...     def deserialize(cls, value):
            ...         # the de-serialized rgb list is good to pass to type
            ...         return value

        Note that ``json_deserialize`` does not return a ``Color`` instance.
        Intead, it returns a *list* to be used as an input to :meth:`cast`
        (which is ultimately passed to :meth:`type`)

        This is because when the values are deserialized, they're used as the
        default values for a newly created :class:`ParametricObject <cqparts.params.parametric_object.ParametricObject>` class.

        So now when we use them in a :class:`ParametricObject <cqparts.params.parametric_object.ParametricObject>`:

        .. doctest::

            >>> from cqparts.params import ParametricObject, Float
            >>> class MyObject(ParametricObject):
            ...     color = ColorParam(default=[127, 127, 127])  # default 50% grey
            ...     height = Float(10)

            >>> my_object = MyObject(color=[100, 200, 255])
            >>> my_object.color  # is a Color instance (not a list)
            <Color: 100, 200, 255>

        Now to demonstrate how a parameter goes in and out of being serialized,
        we'll create a ``test`` method that, doesn't do anything, except that
        it should *not* throw any exceptions from its assertions, or the call
        to :meth:`json.dumps`

        .. doctest::

            >>> import json

            >>> def test(value, obj_class=Color, param_class=ColorParam):
            ...     orig_obj = param_class().cast(value)
            ...
            ...     # serialize
            ...     if value is None:
            ...         assert orig_obj == None
            ...     else:
            ...         assert isinstance(orig_obj, obj_class)
            ...     serialized = json.dumps(param_class.serialize(orig_obj))
            ...
            ...     # show serialized value
            ...     print(serialized)  # as a json string
            ...
            ...     # deserialize
            ...     ds_value = param_class.deserialize(json.loads(serialized))
            ...     new_obj = param_class().cast(ds_value)
            ...
            ...     # now orig_obj and new_obj should be identical
            ...     assert orig_obj == new_obj
            ...     print("all good")

            >>> test([1, 2, 3])
            [1, 2, 3]
            all good
            >>> test(None)
            null
            all good

        These are used to serialize and deserialize :class:`ParametricObject <cqparts.params.parametric_object.ParametricObject>`
        instances, so they may be added to a catalogue, then re-created.

        To learn more, go to :meth:`ParametricObject.serialize() <cqparts.params.parametric_object.ParametricObject.serialize>`

        """
        return value

    @classmethod
    def deserialize(cls, value):
        """
        Converts :mod:`json` deserialized value to its python equivalent.

        :param value: :mod:`json` deserialized value
        :return: python equivalent of ``value``

        .. important::

            ``value`` must be deserialized to be a valid input to :meth:`cast`

        More information on this in :meth:`serialize`

        """
        return value
