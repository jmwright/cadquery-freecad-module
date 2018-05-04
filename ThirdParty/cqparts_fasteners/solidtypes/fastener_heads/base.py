import six
import cadquery

# relative imports
import cqparts
from cqparts.params import *

import logging
log = logging.getLogger(__name__)


class FastenerHead(cqparts.Part):
    diameter = PositiveFloat(5.2, doc="fastener head diameter")
    height = PositiveFloat(2.0, doc="fastener head height")
    # tool access
    access_diameter = PositiveFloat(None, doc="diameter of circle alowing tool access above fastener (defaults to diameter)")
    access_height = PositiveFloat(1000, doc="depth of hole providing access (default 1m)")

    def initialize_parameters(self):
        if self.access_diameter is None:
            self.access_diameter = self._default_access_diameter()

    def _default_access_diameter(self):
        return self.diameter

    def make_cutter(self):
        """
        Create solid to subtract from material to make way for the fastener's
        head (just the head)
        """
        return cadquery.Workplane('XY') \
            .circle(self.access_diameter / 2) \
            .extrude(self.access_height)

    def get_face_offset(self):
        """
        Returns the screw drive origin offset relative to bolt's origin
        """
        return (0, 0, self.height)


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
