import cadquery

import cqparts
from cqparts.params import *
from cqparts.constraint import Fixed, Mate
from cqparts.search import register, common_criteria
from cqparts.utils.wrappers import as_part
from cqparts.display.material import TEMPLATE


# basic.primatives registration utility
module_criteria = {
    'lib': 'basic',
    'type': 'indicator',
    'module': __name__,
}
_register = common_criteria(**module_criteria)(register)


# --------------- Indicators ---------------

@_register(indicator='coord_sys')
class CoordSysIndicator(cqparts.Assembly):
    """
    Assembly of 3 rectangles indicating xyz axes.

    * X = red
    * Y = green
    * Z = blue
    """
    length = PositiveFloat(10, doc="length of axis indicators")
    width = PositiveFloat(1, doc="width of axis indicators")

    class Rect(cqparts.Part):
        w = Float(1)
        (x, y, z) = (Float(), Float(), Float())
        def initialize_parameters(self):
            self.x = self.x or self.w
            self.y = self.y or self.w
            self.z = self.z or self.w
        def make(self):
            return cadquery.Workplane('XY').box(
                self.x, self.y, self.z,
                centered=(self.x <= self.w, self.y <= self.w, self.z <= self.w),
            )

    def make_components(self):
        return {
            'x': self.Rect(w=self.width, x=self.length, _render=TEMPLATE['red']),
            'y': self.Rect(w=self.width, y=self.length, _render=TEMPLATE['green']),
            'z': self.Rect(w=self.width, z=self.length, _render=TEMPLATE['blue']),
        }

    def make_constraints(self):
        return [
            Fixed(self.components[k].mate_origin)
            for k in 'xyz'
        ]


@_register(indicator='plane')
class PlaneIndicator(cqparts.Part):
    """
    A thin plate spread over the given plane
    """
    size = PositiveFloat(20, doc="size of square plate; length of one side")
    thickness = PositiveFloat(0.01, doc="thickness of indicator plate")
    name = String('XY', doc="name of plane, according to :meth:`cadquery.Plane.named`")
    def make(self):
        return cadquery.Workplane(self.name).box(self.size, self.size, self.thickness)
