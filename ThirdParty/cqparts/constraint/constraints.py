
from .base import Constraint
from .mate import Mate
from ..utils.geometry import CoordSystem


class Fixed(Constraint):
    """
    Sets a component's world coordinates so the given ``mate`` is
    positioned and orientated to the given ``world_coords``.

    There is only 1 possible solution.
    """

    def __init__(self, mate, world_coords=None):
        """
        :param mate: mate to lock
        :type mate: :class:`Mate <cqparts.constraint.Mate>`
        :param world_coords: world coordinates to lock ``mate`` to
        :type world_coords: :class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`
        :raises TypeError: if an invalid parameter type is passed

        If the ``world_coords`` parameter is set as a
        :class:`Mate <cqparts.constraint.Mate>` instance, the mate's
        ``.world_coords`` is used.

        If ``world_coords`` is ``None``, the object is locked to the origin.
        """
        # mate
        if isinstance(mate, Mate):
            self.mate = mate
        else:
            raise TypeError("mate must be a %r, not a %r" % (Mate, type(mate)))

        # world_coords
        if isinstance(world_coords, CoordSystem):
            self.world_coords = world_coords
        elif isinstance(world_coords, Mate):
            self.world_coords = world_coords.world_coords
        elif world_coords is None:
            self.world_coords = CoordSystem()
        else:
            raise TypeError(
                "world_coords must be a %r or %r, not a %r" % (Mate, CoordSystem, type(world_coords))
            )


class Coincident(Constraint):
    """
    Set a component's world coordinates of ``mate.component`` so that
    ``mate.world_coords`` == ``to_mate.world_coords``.

    To successfully determine the component's location, the relative component
    must be solvable.

    .. note::
        An :class:`Assembly <cqparts.Assembly>` **cannot** solely rely
        on relative locks to place its components.
        This is because every component will be waiting for another component
        to be placed, a circular problem.

        At least one of them must use the :class:`Fixed`
    """
    def __init__(self, mate, to_mate):
        """
        :param mate: mate to lock
        :type mate: :class:`Mate <cqparts.constraint.Mate>`
        :param to_mate: mate to lock ``mate`` to
        :type to_mate: :class:`Mate <cqparts.constraint.Mate>`
        """
        # mate
        if isinstance(mate, Mate):
            self.mate = mate
        else:
            raise TypeError("mate must be a %r, not a %r" % (Mate, type(mate)))

        # to_mate
        if isinstance(to_mate, Mate):
            self.to_mate = to_mate
        else:
            raise TypeError("to_mate must be a %r, not a %r" % (Mate, type(to_mate)))
