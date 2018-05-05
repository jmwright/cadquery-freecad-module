

# Build Exceptions
class ParameterError(Exception):
    """Raised when an invalid parameter is specified"""

class MakeError(Exception):
    """Raised when there are issues during the make() process of a Part or Assembly"""


# Internal Search Exceptions
class AssemblyFindError(Exception):
    """Raised when an assembly element cannot be found"""


# Solids Validity
class SolidValidityError(Exception):
    """Raised when an unrecoverable issue occurs with a solid"""


# Search Exceptions
class SearchError(Exception):
    """
    Raised by search algithms, for example :meth:`cqparts.search.find`

    Parent of both :class:`SearchNoneFoundError` & :class:`SearchMultipleFoundError`

    .. doctest::

        >>> from cqparts.errors import SearchError
        >>> from cqparts.search import find

        >>> try:
        ...     part_a_class = find(a='common', b='criteria')  # multiple results
        ...     part_b_class = find(a="doesn't exist")  # no results
        ... except SearchError:
        ...     # error handling?
        ...     pass
    """

class SearchNoneFoundError(SearchError):
    """Raised when no results are found by :meth:`cqparts.search.find`"""

class SearchMultipleFoundError(SearchError):
    """Raised when multiple results are found by :meth:`cqparts.search.find`"""
