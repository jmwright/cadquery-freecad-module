
import six

from types import GeneratorType

from .component import Component
from .constraint import Constraint
from .constraint.solver import solver
from .utils.misc import indicate_last

from .errors import AssemblyFindError

import logging
log = logging.getLogger(__name__)


class Assembly(Component):
    """
    An assembly is a group of parts, and other assemblies (called components)
    """

    def __init__(self, *largs, **kwargs):
        super(Assembly, self).__init__(*largs, **kwargs)
        self._components = None
        self._constraints = None

    def make_components(self):
        """
        Create and return :class:`dict` of :class:`Component` instances.

        .. tip::

            This **must** be overridden in inheriting class, read:

            * :ref:`parts_assembly-build-cycle` for details.
            * :ref:`tutorial_assembly` for an example.

        :return: {<name>: <Component>, ...}
        :rtype: :class:`dict` of :class:`Component` instances
        """
        raise NotImplementedError("make_components function not implemented")

    def make_constraints(self):
        """
        Create and return :class:`list` of
        :class:`Constraint <cqparts.constraint.base.Constraint>` instances

        .. tip::

            This **must** be overridden in inheriting class, read:

            * :ref:`parts_assembly-build-cycle` for details.
            * :ref:`tutorial_assembly` for an example.

        :return: constraints for assembly children's placement
        :rtype: :class:`list` of :class:`Constraint <cqparts.constraint.base.Constraint>` instances

        Default behaviour returns an empty list; assumes assembly is
        entirely unconstrained.
        """
        raise NotImplementedError("make_constraints function not implemented")

    def make_alterations(self):
        """
        Make necessary changes to components after the constraints solver has
        completed.

        .. tip::

            This *can* be overridden in inheriting class, read:

            * :ref:`parts_assembly-build-cycle` for details.
            * :ref:`tutorial_assembly` for an example.

        """
        pass

    @property
    def components(self):
        """
        Returns full :class:`dict` of :class:`Component` instances, after
        a successful :meth:`build`

        :return: dict of named :class:`Component` instances
        :rtype: :class:`dict`

        For more information read about the :ref:`parts_assembly-build-cycle` .
        """
        if self._components is None:
            self.build(recursive=False)
        return self._components

    @property
    def constraints(self):
        """
        Returns full :class:`list` of :class:`Constraint <cqparts.constraint.Constraint>` instances, after
        a successful :meth:`build`

        :return: list of named :class:`Constraint <cqparts.constraint.Constraint>` instances
        :rtype: :class:`list`

        For more information read about the :ref:`parts_assembly-build-cycle` .
        """
        if self._constraints is None:
            self.build(recursive=False)
        return self._constraints

    def _placement_changed(self):
        """
        Called when ``world_coords`` is changed.

        All components' ``world_coords`` must be updated based on the change;
        calls :meth:`solve`.
        """
        self.solve()

    def solve(self):
        """
        Run the solver and assign the solution's :class:`CoordSystem` instances
        as the corresponding part's world coordinates.
        """
        if self.world_coords is None:
            log.warning("solving for Assembly without word coordinates set: %r", self)

        for (component, world_coords) in solver(self.constraints, self.world_coords):
            component.world_coords = world_coords

    @staticmethod
    def verify_components(components):
        """
        Verify values returned from :meth:`make_components`.

        Used internally during the :meth:`build` process.

        :param components: value returned from :meth:`make_components`
        :type components: :class:`dict`
        :raises ValueError: if verification fails
        """
        # verify returned type from user-defined function
        if not isinstance(components, dict):
            raise ValueError(
                "invalid type returned by make_components(): %r (must be a dict)" % components
            )

        # check types for (name, component) pairs in dict
        for (name, component) in components.items():
            # name is a string
            if not isinstance(name, str):
                raise ValueError((
                    "invalid name from make_components(): (%r, %r) "
                    "(must be a (str, Component))"
                ) % (name, component))

            # component is a Component instance
            if not isinstance(component, Component):
                raise ValueError((
                    "invalid component type from make_components(): (%r, %r) "
                    "(must be a (str, Component))"
                ) % (name, component))

            # name cannot contain a '.'
            if '.' in name:
                raise ValueError("component names cannot contain a '.' (%s, %r)" % (name, component))

    @staticmethod
    def verify_constraints(constraints):
        """
        Verify values returned from :meth:`make_constraints`.

        Used internally during the :meth:`build` process.

        :param constraints: value returned from :meth:`make_constraints`
        :type constraints: :class:`list`
        :raises ValueError: if verification fails
        """
        # verify return is a list
        if not isinstance(constraints, list):
            raise ValueError(
                "invalid type returned by make_constraints: %r (must be a list)" % constraints
            )

        # verify each list element is a Constraint instance
        for constraint in constraints:
            if not isinstance(constraint, Constraint):
                raise ValueError(
                    "invalid constraint type: %r (must be a Constriant)" % constraint
                )

    def build(self, recursive=True):
        """
        Building an assembly buffers the :meth:`components` and :meth:`constraints`.


        Running ``build()`` is optional, it's automatically run when requesting
        :meth:`components` or :meth:`constraints`.

        Mostly it's used to test that there aren't any critical runtime
        issues with its construction, but doing anything like *displaying* or
        *exporting* will ultimately run a build anyway.

        :param recursive: if set, iterates through child components and builds
                          those as well.
        :type recursive: :class:`bool`
        """

        # initialize values
        self._components = {}
        self._constraints = []

        def genwrap(obj, name, iter_type=None):
            # Force obj to act like a generator.
            # this wrapper will always yield at least once.
            if isinstance(obj, GeneratorType):
                for i in obj:
                    if (iter_type is not None) and (not isinstance(i, iter_type)):
                        raise TypeError("%s must yield a %r" % (name, iter_type))
                    yield i
            else:
                if (iter_type is not None) and (not isinstance(obj, iter_type)):
                    raise TypeError("%s must return a %r" % (name, iter_type))
                yield obj

        # Make Components
        components_iter = genwrap(self.make_components(), "make_components", dict)
        new_components = next(components_iter)
        self.verify_components(new_components)
        self._components.update(new_components)

        # Make Constraints
        constraints_iter = genwrap(self.make_constraints(), "make_components", list)
        new_constraints = next(constraints_iter)
        self.verify_constraints(new_constraints)
        self._constraints += new_constraints

        # Run solver : sets components' world coordinates
        self.solve()

        # Make Alterations
        alterations_iter = genwrap(self.make_alterations(), "make_alterations")
        next(alterations_iter)  # return value is ignored

        while True:
            (s1, s2, s3) = (True, True, True)  # stages
            # Make Components
            new_components = None
            try:
                new_components = next(components_iter)
                self.verify_components(new_components)
                self._components.update(new_components)
            except StopIteration:
                s1 = False

            # Make Constraints
            new_constraints = None
            try:
                new_constraints = next(constraints_iter)
                self.verify_constraints(new_constraints)
                self._constraints += new_constraints
            except StopIteration:
                s2 = False

            # Run solver : sets components' world coordinates
            if new_components or new_constraints:
                self.solve()

            # Make Alterations
            try:
                next(alterations_iter)  # return value is ignored
            except StopIteration:
                s3 = False

            # end loop when all iters are finished
            if not any((s1, s2, s3)):
                break

        if recursive:
            for (name, component) in self._components.items():
                component.build(recursive=recursive)

    def find(self, keys, _index=0):
        """
        :param keys: key path. ``'a.b'`` is equivalent to ``['a', 'b']``
        :type keys: :class:`str` or :class:`list`

        Find a nested :class:`Component` by a "`.`" separated list of names.
        for example::

            >>> motor.find('bearing.outer_ring')

        would return the Part instance of the motor bearing's outer ring.

        ::

            >>> bearing = motor.find('bearing')
            >>> ring = bearing.find('inner_ring')  # equivalent of 'bearing.inner_ring'

        the above code does much the same thing, ``bearing`` is an :class:`Assembly`,
        and ``ring`` is a :class:`Part`.

        .. note::

            For a key path of ``a.b.c`` the ``c`` key can referernce any
            :class:`Component` type.

            Everything prior (in this case ``a`` and ``b``) must reference an
            :class:`Assembly`.
        """

        if isinstance(keys, six.string_types):
            keys = [k for k in keys.split('.') if k]
        if _index >= len(keys):
            return self

        key = keys[_index]
        if key in self.components:
            component = self.components[key]
            if isinstance(component, Assembly):
                return component.find(keys, _index=(_index + 1))
            elif _index == len(keys) - 1:
                # this is the last search key; component is a leaf, return it
                return component
            else:
                raise AssemblyFindError(
                    "could not find '%s' (invalid type at [%i]: %r)" % (
                        '.'.join(keys), _index, component
                    )
                )
        else:
            raise AssemblyFindError(
                "could not find '%s', '%s' is not a component of %r" % (
                    '.'.join(keys), key, self
                )
            )

    # Component Tree
    def tree_str(self, name=None, prefix='', add_repr=False, _depth=0):
        u"""
        Return string listing recursively the assembly hierarchy

        :param name: if set, names the tree's trunk, otherwise the object's :meth:`repr` names the tree
        :type name: :class:`str`
        :param prefix: string prefixed to each line, can be used to indent
        :type prefix: :class:`str`
        :param add_repr: if set, *component* :meth:`repr` is put after their names
        :type add_repr: :class:`bool`
        :return: Printable string of an assembly's component hierarchy.
        :rtype: :class:`str`

        Example output from `block_tree.py <https://github.com/fragmuffin/cqparts/blob/master/tests/manual/block_tree.py>`_

        ::

            >>> log = logging.getLogger(__name__)
            >>> isinstance(block_tree, Assembly)
            True
            >>> log.info(block_tree.tree_str(name="block_tree"))
            block_tree
             \u251c\u25cb branch_lb
             \u251c\u25cb branch_ls
             \u251c\u2500 branch_r
             \u2502   \u251c\u25cb L
             \u2502   \u251c\u25cb R
             \u2502   \u251c\u25cb branch
             \u2502   \u251c\u2500 house
             \u2502   \u2502   \u251c\u25cb bar
             \u2502   \u2502   \u2514\u25cb foo
             \u2502   \u2514\u25cb split
             \u251c\u25cb trunk
             \u2514\u25cb trunk_split

        Where:

        * ``\u2500`` denotes an :class:`Assembly`, and
        * ``\u25cb`` denotes a :class:`Part`
        """

        # unicode characters
        c_t = u'\u251c'
        c_l = u'\u2514'
        c_dash = u'\u2500'
        c_o = u'\u25cb'
        c_span = u'\u2502'

        output = u''
        if not _depth:  # first line
            output = prefix
            if name:
                output += (name + u': ') if add_repr else name
            if add_repr or not name:
                output += repr(self)
            output += '\n'

        # build tree
        for (is_last, (name, component)) in indicate_last(sorted(self.components.items(), key=lambda x: x[0])):
            branch_chr = c_l if is_last else c_t
            if isinstance(component, Assembly):
                # Assembly: also list nested components
                output += prefix + ' ' + branch_chr + c_dash + u' ' + name
                if add_repr:
                    output += ': ' + repr(component)
                output += '\n'
                output += component.tree_str(
                    prefix=(prefix + (u'    ' if is_last else (u' ' + c_span + '  '))),
                    add_repr=add_repr,
                    _depth=_depth + 1,
                )
            else:
                # Part (assumed): leaf node
                output += prefix + ' ' + branch_chr + c_o + u' ' + name
                if add_repr:
                    output += ': ' + repr(component)
                output += '\n'
        return output
