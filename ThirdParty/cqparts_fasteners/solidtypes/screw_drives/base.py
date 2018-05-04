import six
import cadquery

import cqparts
from cqparts.params import *
from cqparts.utils import CoordSystem


class ScrewDrive(cqparts.Part):
    diameter = PositiveFloat(3.0, doc="screw drive's diameter")
    depth = PositiveFloat(None, doc="depth of recess into driven body")

    def initialize_parameters(self):
        super(ScrewDrive, self).initialize_parameters()
        if self.depth is None:
            self.depth = self.diameter  # default to be as deep as it is wide

    def make(self):
        """
        Make the solid to use as a cutter, to make the screw-drive impression
        in another solid.

        :return: cutter solid
        :rtype: :class:`cadquery.Workplane`
        """
        raise NotImplementedError("%r implements no solid to subtract" % type(self))

    def apply(self, workplane, world_coords=CoordSystem()):
        """
        Application of screwdrive indentation into a workplane
        (centred on the given world coordinates).

        :param workplane: workplane with solid to alter
        :type workplane: :class:`cadquery.Workplane`
        :param world_coords: coorindate system relative to ``workplane`` to move
                             cutter before it's cut from the ``workplane``
        :type world_coords: :class:`CoordSystem`
        """

        self.world_coords = world_coords
        return workplane.cut(self.world_obj)


# ------ Registration
from cqparts.search import (
    find as _find,
    search as _search,
    register as _register,
)
from cqparts.search import common_criteria

module_criteria = {
    'module': __name__,
}

register = common_criteria(**module_criteria)(_register)
search = common_criteria(**module_criteria)(_search)
find = common_criteria(**module_criteria)(_find)
