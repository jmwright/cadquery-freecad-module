import cadquery
from cadquery import BoxSelector
from math import pi, cos, sqrt

from cqparts.params import *

from .base import ScrewDrive, register


class AcentricWedgesScrewDrive(ScrewDrive):
    count = IntRange(1, None, 4)
    width = PositiveFloat(0.5)
    acentric_radius = PositiveFloat(None)  # defaults to width / 2

    def initialize_parameters(self):
        super(AcentricWedgesScrewDrive, self).initialize_parameters()
        if self.acentric_radius is None:
            self.acentric_radius = self.width / 2

    def make(self):
        # Start with a cylindrical pin down the center
        tool = cadquery.Workplane("XY") \
            .circle(self.width / 2).extrude(-self.depth)

        # Create a single blade
        points = [
            (0, 0),
            (0, -self.depth),
            (-self.width / 2, -self.depth),
            (-self.diameter / 2, 0),
        ]
        blade = cadquery.Workplane("XZ").workplane(offset=self.acentric_radius - (self.width / 2)) \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(self.width)

        for i in range(self.count):
            angle = i * (360. / self.count)
            tool = tool.union(
                blade.translate((0, 0, 0)) \
                    .rotate((0, 0, 0), (0, 0, 1), angle)
            )

        return tool


@register(name='tri_point')
class TripointScrewDrive(AcentricWedgesScrewDrive):
    """
    .. image:: /_static/img/screwdrives/tri_point.png
    """
    count = IntRange(1, None, 3)
    acentric_radius = PositiveFloat(0.0)  # yeah, not my best class design, but it works


@register(name='torq_set')
class TorqsetScrewDrive(AcentricWedgesScrewDrive):
    """
    .. image:: /_static/img/screwdrives/torq_set.png
    """
    count = IntRange(1, None, 4)
