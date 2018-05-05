import cadquery
from math import pi, cos, sin, sqrt

from cqparts.params import *

from .base import FastenerHead, register

class CylindricalFastenerHead(FastenerHead):
    fillet = PositiveFloat(None)  # defaults to diameter / 10

    # Dome on top ?
    domed = Boolean(False)
    dome_ratio = PositiveFloat(0.25)  # ratio of head's height

    def initialize_parameters(self):
        super(CylindricalFastenerHead, self).initialize_parameters()
        if self.fillet is None:
            self.fillet = self.diameter / 10

    def make(self):
        head = cadquery.Workplane("XY") \
            .circle(self.diameter / 2.).extrude(self.height)

        if self.domed:
            dome_height = self.height * self.dome_ratio
            sphere_radius = ((dome_height ** 2) + ((self.diameter / 2.) ** 2)) / (2 * dome_height)

            sphere = cadquery.Workplane("XY") \
                .workplane(offset=self.height - sphere_radius) \
                .sphere(sphere_radius)

            head = head.intersect(sphere)

        else:
            # Fillet top face
            if self.fillet:
                head = head.faces(">Z").edges().fillet(self.fillet)

        return head


@register(name='cheese')
class CheeseFastenerHead(CylindricalFastenerHead):
    """
    .. image:: /_static/img/fastenerheads/cheese.png
    """
    fillet = PositiveFloat(0.0)
    domed = Boolean(False)


@register(name='pan')
class PanFastenerHead(CylindricalFastenerHead):
    """
    .. image:: /_static/img/fastenerheads/pan.png
    """
    domed = Boolean(False)


@register(name='dome')
class DomeFastenerHead(CylindricalFastenerHead):
    """
    .. image:: /_static/img/fastenerheads/dome.png
    """
    domed = Boolean(True)


@register(name='round')
class RoundFastenerHead(CylindricalFastenerHead):
    """
    .. image:: /_static/img/fastenerheads/round.png
    """
    domed = Boolean(True)
    dome_ratio = PositiveFloat(1)

    # Coach Head
    coach_head = Boolean(False)
    coach_width = PositiveFloat(None)  # default = diameter / 2
    coach_height = PositiveFloat(None)  # default = height
    coach_chamfer = PositiveFloat(None)  # default = coach_width / 6

    def initialize_parameters(self):
        super(RoundFastenerHead, self).initialize_parameters()
        if self.coach_width is None:
            self.coach_width = self.diameter / 2
        if self.coach_height is None:
            self.coach_height = self.height
        if self.coach_chamfer is None:
            self.coach_chamfer = self.coach_width / 6

    def make(self):
        head = super(RoundFastenerHead, self).make()

        # Add chamfered square block beneath fastener head
        if self.coach_head:
            cone_radius = ((self.coach_width / 2.) + self.coach_height) - self.coach_chamfer
            cone_height = cone_radius

            box = cadquery.Workplane("XY").rect(self.coach_width, self.coach_width).extrude(-self.coach_height)
            cone = cadquery.Workplane("XY").union(
                cadquery.CQ(cadquery.Solid.makeCone(0, cone_radius, cone_height)) \
                    .translate((0, 0, -cone_height))
            )
            head = head.union(box.intersect(cone))

        return head


@register(name='round_coach')
class RoundCoachFastenerHead(RoundFastenerHead):
    """
    .. image:: /_static/img/fastenerheads/round_coach.png
    """
    coach_head = Boolean(True)


@register(name='trapezoidal')
class TrapezoidalFastenerHead(FastenerHead):
    """
    .. image:: /_static/img/fastenerheads/trapezoidal.png
    """
    diameter_top = PositiveFloat(None)  # default to diameter * 0.75

    def initialize_parameters(self):
        super(TrapezoidalFastenerHead, self).initialize_parameters()
        if self.diameter_top is None:
            self.diameter_top = self.diameter * 0.75

    def make(self, offset=(0, 0, 0)):
        r1 = self.diameter / 2.
        r2 = self.diameter_top / 2.
        head = cadquery.Workplane("XY").union(
            cadquery.CQ(cadquery.Solid.makeCone(r1, r2, self.height))
        )

        return head.translate(offset)
