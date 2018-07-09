import cadquery

import cqparts
from cqparts.params import *

class Gear(cqparts.Part):
    effective_radius = PositiveFloat(25, doc="designed equivalent wheel radius")
    tooth_count = PositiveInt(12, doc="number of teeth")
    width = PositiveFloat(10, doc="gear thickness")

    def make_simple(self):
        return cadquery.Workplane('XY', origin=(0, 0, -self.width)) \
            .circle(self.effective_radius).extrude(self.width)
