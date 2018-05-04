import cadquery
from cqparts.params import *

from .base import ScrewDrive, register


@register(name='slot')
class SlotScrewDrive(ScrewDrive):
    """
    .. image:: /_static/img/screwdrives/slot.png
    """
    width = PositiveFloat(None, doc="slot width")

    def initialize_parameters(self):
        if self.width is None:
            self.width = self.diameter / 8
        if self.depth is None:
            self.depth = self.width * 1.5
        super(SlotScrewDrive, self).initialize_parameters()

    def make(self):
        tool = cadquery.Workplane("XY") \
            .rect(self.width, self.diameter).extrude(-self.depth)
        return tool


@register(name='cross')
class CrossScrewDrive(ScrewDrive):
    """
    .. image:: /_static/img/screwdrives/cross.png
    """
    width = PositiveFloat(None, doc="slot width")

    def initialize_parameters(self):
        if self.width is None:
            self.width = self.diameter / 8
        if self.depth is None:
            self.depth = self.width * 1.5
        super(CrossScrewDrive, self).initialize_parameters()

    def make(self):
        tool = cadquery.Workplane("XY") \
            .rect(self.width, self.diameter).extrude(-self.depth) \
            .faces(">Z") \
            .rect(self.diameter, self.width).extrude(-self.depth)
        return tool
