import cadquery
from math import sqrt, pi, sin, cos
from copy import copy
from cqparts.params import *

from .base import ScrewDrive, register


@register(name='square')
@register(name='robertson')
class SquareScrewDrive(ScrewDrive):
    """
    .. image:: /_static/img/screwdrives/square.png
    """
    width = PositiveFloat(None)
    count = IntRange(1, None, 1)

    def initialize_parameters(self):
        super(SquareScrewDrive, self).initialize_parameters()
        if self.width is None:
            self.width = self.diameter / sqrt(2)
        else:
            # Set diameter from square's width (ignore given diameter)
            self.diameter = self.width / cos(pi / 6)

    def get_square(self, angle=0):
        return cadquery.Workplane('XY') \
            .rect(self.width, self.width).extrude(-self.depth) \
            .rotate((0,0,0), (0,0,1), angle)

    def make(self):
        # Single square as template
        tool_template = cadquery.Workplane("XY") \
            .rect(self.width, self.width).extrude(-self.depth)

        # Create tool (rotate & duplicate template)
        tool = cadquery.Workplane('XY')
        for i in range(self.count):
            tool = tool.union(
                self.get_square(angle=i * (90.0 / self.count))
            )

        return tool


@register(name='double_square')
@register(name='2square')
class DoubleSquareScrewDrive(SquareScrewDrive):
    """
    .. image:: /_static/img/screwdrives/double_square.png
    """
    count = IntRange(1, None, 2)


@register(name='triple_square')
@register(name='3square')
class TrippleSquareScrewDrive(SquareScrewDrive):
    """
    .. image:: /_static/img/screwdrives/triple_square.png
    """
    count = IntRange(1, None, 3)
