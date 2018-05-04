
# Casting utilities are only intended to be used locally
# (ie: within the cqparts_fasteners.utils sub-modules).
# Each cast is designed to take a variety of inputs, and output
# the same class instance each time, or raise a fault

import cadquery


class CastingError(Exception):
    """
    Raised if there's any problem casting one object type to another.
    """
    pass


def solid(solid_in):
    """
    :return: cadquery.Solid instance
    """
    if isinstance(solid_in, cadquery.Solid):
        return solid_in
    elif isinstance(solid_in, cadquery.CQ):
        return solid_in.val()

    raise CastingError(
        "Cannot cast object type of {!r} to a solid".format(solid_in)
    )


def vector(vect_in):
    """
    :return: cadquery.Vector instance
    """
    if isinstance(vect_in, cadquery.Vector):
        return vect_in
    elif isinstance(vect_in, (tuple, list)):
        return cadquery.Vector(vect_in)

    raise CastingError(
        "Cannot cast object type of {!r} to a vector".format(vect_in)
    )
