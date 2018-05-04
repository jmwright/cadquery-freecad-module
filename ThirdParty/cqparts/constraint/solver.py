
from ..utils.geometry import CoordSystem
from .base import Constraint
from .constraints import Fixed, Coincident


def solver(constraints, coord_sys=None):
    """
    Solve constraints. Solutions pair :class:`Constraint <cqparts.constraint.Constraint>`
    instances with their suitable :class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`
    world coordinates.

    :param constraints: constraints to solve
    :type constraints: iterable of :class:`Constraint <cqparts.constraint.Constraint>`
    :param coord_sys: coordinate system to offset solutions (default: no offset)
    :type coord_sys: :class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`

    :return: generator of (:class:`Component <cqparts.Component>`,
             :class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`) tuples.
    """

    if coord_sys is None:
        coord_sys = CoordSystem()  # default

    # Verify list contains constraints
    for constraint in constraints:
        if not isinstance(constraint, Constraint):
            raise ValueError("{!r} is not a constraint".format(constraint))

    solved_count = 0

    indexed = list(constraints)

    # Continue running solver until no solution is found
    while indexed:
        indexes_solved = []
        for (i, constraint) in enumerate(indexed):

            # Fixed
            if isinstance(constraint, Fixed):
                indexes_solved.append(i)
                yield (
                    constraint.mate.component,
                    coord_sys + constraint.world_coords + (CoordSystem() - constraint.mate.local_coords)
                )

            # Coincident
            elif isinstance(constraint, Coincident):
                try:
                    relative_to = constraint.to_mate.world_coords
                except ValueError:
                    relative_to = None

                if relative_to is not None:
                    indexes_solved.append(i)
                    # note: relative_to are world coordinates; adding coord_sys is not necessary
                    yield (
                        constraint.mate.component,
                        relative_to + (CoordSystem() - constraint.mate.local_coords)
                    )

        if not indexes_solved:  # no solutions found
            # At least 1 solution must be found each iteration.
            # if not, we'll just be looping forever.
            break
        else:
            # remove constraints from indexed list (so they're not solved twice)
            for j in reversed(indexes_solved):
                del indexed[j]

    if indexed:
        raise ValueError("not all constraints could be solved")
