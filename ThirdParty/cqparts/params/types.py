
from .parameter import Parameter

from ..errors import ParameterError


# ------------ float types ------------
class Float(Parameter):
    """
    Floating point
    """

    _doc_type = ':class:`float`'

    def type(self, value):
        try:
            cast_value = float(value)
        except ValueError:
            raise ParameterError("value cannot be cast to a float: %r" % value)
        return cast_value


class PositiveFloat(Float):
    """
    Floating point >= 0
    """
    def type(self, value):
        cast_value = super(PositiveFloat, self).type(value)
        if cast_value < 0:
            raise ParameterError("value is not positive: %g" % cast_value)
        return cast_value


class FloatRange(Float):
    """
    Floating point in the given range (inclusive)
    """
    def __init__(self, min, max, default, doc="[no description]"):
        """
        {``min`` <= value <= ``max``}

        :param min: minimum value
        :type min: float
        :param max: maximum value
        :type max: float
        """
        self.min = min
        self.max = max
        super(FloatRange, self).__init__(default, doc=doc)

    def type(self, value):
        cast_value = super(FloatRange, self).type(value)

        # Check range (min/max value of None is equivelant to -inf/inf)
        inside_range = True
        if (self.min is not None) and (cast_value < self.min):
            inside_range = False
        if (self.max is not None) and (cast_value > self.max):
            inside_range = False

        if not inside_range:
            raise ParameterError("value of %g outside the range {%s, %s}" % (
                cast_value, self.min, self.max
            ))

        return cast_value

# ------------ int types ---------------
class Int(Parameter):
    """
    Integer value
    """
    _doc_type = ":class:`int`"

    def type(self, value):
        try:
            cast_value = int(value)
        except ValueError:
            raise ParameterError("value cannot be cast to an integer: %r" % value)
        return cast_value


class PositiveInt(Int):
    """
    Integer >= 0
    """
    def type(self, value):
        cast_value = super(PositiveInt, self).type(value)
        if cast_value < 0:
            raise ParameterError("value is not positive: %g" % cast_value)
        return cast_value


class IntRange(Int):
    """
    Integer in the given range (inclusive)
    """
    def __init__(self, min, max, default, doc="[no description]"):
        """
        {``min`` <= value <= ``max``}

        :param min: minimum value
        :type min: int
        :param max: maximum value
        :type max: int
        """
        self.min = min
        self.max = max
        super(IntRange, self).__init__(default, doc=doc)

    def type(self, value):
        cast_value = super(IntRange, self).type(value)

        # Check range (min/max value of None is equivelant to -inf/inf)
        inside_range = True
        if (self.min is not None) and (cast_value < self.min):
            inside_range = False
        if (self.max is not None) and (cast_value > self.max):
            inside_range = False

        if not inside_range:
            raise ParameterError("value of %g outside the range {%s, %s}" % (
                cast_value, self.min, self.max
            ))

        return cast_value


# ------------ boolean types ------------
class Boolean(Parameter):
    """
    Boolean value
    """

    _doc_type = ':class:`bool`'

    def type(self, value):
        try:
            cast_value = bool(value)
        except ValueError:
            raise ParameterError("value cannot be cast to bool: %r" % value)
        return cast_value


# ------------ string types ------------
class String(Parameter):
    """
    String value
    """

    _doc_type = ":class:`str`"

    def type(self, value):
        try:
            cast_value = str(value)
        except ValueError:
            raise ParameterError("value cannot be cast to string: %r" % value)
        return cast_value


class LowerCaseString(String):
    """
    Lower case string
    """
    def type(self, value):
        cast_value = super(LowerCaseString, self).type(value)
        return cast_value.lower()


class UpperCaseString(String):
    """
    Upper case string
    """
    def type(self, value):
        cast_value = super(UpperCaseString, self).type(value)
        return cast_value.upper()


# ------------ others ---------------
class NonNullParameter(Parameter):
    """
    Non-nullable parameter
    """
    def cast(self, value):
        if value is None:
            raise ParameterError("value cannot be None")
        return self.type(value)


class PartsList(Parameter):

    _doc_type = ":class:`list` of :class:`Part <cqparts.Part>` instances"

    def type(self, value):
        # Verify, raise exception for any problems
        if isinstance(value, (list, tuple)):
            from .. import Part  # avoid circular dependency
            for part in value:
                if not isinstance(part, Part):
                    raise ParameterError("value must be a list of Part instances")
        else:
            raise ParameterError("value must be a list")

        return value
