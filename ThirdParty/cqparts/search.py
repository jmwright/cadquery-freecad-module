from collections import defaultdict
from copy import copy

from .errors import SearchMultipleFoundError, SearchNoneFoundError

# Search Index
#   of the format:
#       index = {
#           <category>: {
#               <value>: set([<set of classes>]),
#               ... more values
#           },
#           ... more categories
#       }
index = defaultdict(lambda: defaultdict(set))
class_list = set()

# class_criteria, of the format:
#       class_criteria = {
#           <Component class>: {
#               <category>: set([<set of values>]),
#               ... more categories
#           },
#           ... more classes
#       }
class_criteria = {}


def register(**criteria):
    """
    class decorator to add :class:`Part <cqparts.Part>` or
    :class:`Assembly <cqparts.Assembly>` to the ``cqparts`` search index:

    .. testcode::

        import cqparts
        from cqparts.params import *

        # Created Part or Assembly
        @cqparts.search.register(
            type='motor',
            current_class='dc',
            part_number='ABC123X',
        )
        class SomeMotor(cqparts.Assembly):
            shaft_diam = PositiveFloat(5)
            def make_components(self):
                return {}  # build assembly content

        motor_class = cqparts.search.find(part_number='ABC123X')
        motor = motor_class(shaft_diam=6.0)

    Then use :meth:`find` &/or :meth:`search` to instantiate it.

    .. warning::

        Multiple classes *can* be registered with identical criteria, but
        should be avoided.

        If multiple classes share the same criteria, :meth:`find` will never
        yield the part you want.

        Try adding unique criteria, such as *make*, *model*, *part number*,
        *library name*, &/or *author*.

        To avoid this, learn more in :ref:`tutorial_component-index`.
    """

    def inner(cls):
        # Add class references to search index
        class_list.add(cls)
        for (category, value) in criteria.items():
            index[category][value].add(cls)

        # Retain search criteria
        _entry = dict((k, set([v])) for (k, v) in criteria.items())
        if cls not in class_criteria:
            class_criteria[cls] = _entry
        else:
            for key in _entry.keys():
                class_criteria[cls][key] = class_criteria[cls].get(key, set()) | _entry[key]

        # Return class
        return cls

    return inner


def search(**criteria):
    """
    Search registered *component* classes matching the given criteria.

    :param criteria: search criteria of the form: ``a='1', b='x'``
    :return: parts registered with the given criteria
    :rtype: :class:`set`

    Will return an empty :class:`set` if nothing is found.

    ::

        from cqparts.search import search
        import cqparts_motors  # example of a 3rd party lib

        # Get all DC motor classes
        dc_motors = search(type='motor', current_class='dc')

        # For more complex queries:
        air_cooled = search(cooling='air')
        non_aircooled_dcmotors = dc_motors - air_cooled
        # will be all DC motors that aren't air-cooled
    """
    # Find all parts that match the given criteria
    results = copy(class_list)  # start with full list
    for (category, value) in criteria.items():
        results &= index[category][value]

    return results


def find(**criteria):
    """
    Find a single *component* class with the given criteria.

    Finds classes indexed with :meth:`register`

    :raises SearchMultipleFoundError: if more than one result found
    :raises SearchNoneFoundError: if nothing found

    ::

        from cqparts.search import find
        import cqparts_motors  # example of a 3rd party lib

        # get a specific motor class
        motor_class = find(type='motor', part_number='ABC123X')
        motor = motor_class(shaft_diameter=6.0)
    """
    # Find all parts that match the given criteria
    results = search(**criteria)

    # error cases
    if len(results) > 1:
        raise SearchMultipleFoundError("%i results found" % len(results))
    elif not results:
        raise SearchNoneFoundError("%i results found" % len(results))

    # return found Part|Assembly class
    return results.pop()


def common_criteria(**common):
    """
    Wrap a function to always call with the given ``common`` named parameters.

    :property common: criteria common to your function call
    :return: decorator function
    :rtype: :class:`function`

    .. doctest::

        >>> import cqparts
        >>> from cqparts.search import register, search, find
        >>> from cqparts.search import common_criteria

        >>> # Somebody elses (boring) library may register with...
        >>> @register(a='one', b='two')
        ... class BoringThing(cqparts.Part):
        ...     pass

        >>> # But your library is awesome; only registering with unique criteria...
        >>> lib_criteria = {
        ...     'author': 'your_name',
        ...     'libname': 'awesome_things',
        ... }

        >>> awesome_register = common_criteria(**lib_criteria)(register)

        >>> @awesome_register(a='one', b='two')  # identical to BoringThing
        ... class AwesomeThing(cqparts.Part):
        ...     pass

        >>> # So lets try a search
        >>> len(search(a='one', b='two')) # doctest: +SKIP
        2
        >>> # oops, that returned both classes

        >>> # To narrow it down, we add something unique:
        >>> len(search(a='one', b='two', libname='awesome_things'))  # finds only yours # doctest: +SKIP
        1

        >>> # or, we could use common_criteria again...
        >>> awesome_search = common_criteria(**lib_criteria)(search)
        >>> awesome_find = common_criteria(**lib_criteria)(find)
        >>> len(awesome_search(a='one', b='two')) # doctest: +SKIP
        1
        >>> awesome_find(a='one', b='two').__name__
        'AwesomeThing'

    A good universal way to apply unique criteria is with

    .. testcode::

        import cadquery, cqparts
        from cqparts.search import register, common_criteria
        _register = common_criteria(module=__name__)(register)

        @_register(shape='cube', scale='unit')
        class Cube(cqparts.Part):
            # just an example...
            def make(self):
                return cadquery.Workplane('XY').box(1, 1, 1)

    """
    def decorator(func):
        def inner(*args, **kwargs):
            merged_kwargs = copy(common)
            merged_kwargs.update(kwargs)
            return func(*args, **merged_kwargs)
        return inner
    return decorator
