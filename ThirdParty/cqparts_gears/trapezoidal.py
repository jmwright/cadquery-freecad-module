
from math import pi, radians, sin, cos, acos

import cadquery
from cqparts.params import *
from cqparts.utils import CoordSystem

from cqparts.constraint import Mate

from .base import Gear


class TrapezoidalGear(Gear):
    """
    Basic gear with trapezoidal tooth shape.

    .. image:: /_static/img/gears/trapezoidal.png
    """
    tooth_height = PositiveFloat(None, doc="radial height of teeth")

    face_angle = PositiveFloat(30, doc="angle of tooth edge radial edge (unit: degrees)")
    spacing_ratio = FloatRange(0, 1, 0.5, doc="tooth thickness as a ratio of the distance between them")

    flat_top = Boolean(False, doc="if ``True`` the tops of teeth are flat")

    def initialize_parameters(self):
        super(TrapezoidalGear, self).initialize_parameters()
        if self.tooth_height is None:
            self.tooth_height = 0.2 * self.effective_radius  # default: 20% effective radius

    def _make_tooth_template(self):
        """
        Builds a single tooth including the cylinder with tooth faces
        tangential to its circumference.
        """
        # parameters
        period_arc = (2 * pi) / self.tooth_count
        tooth_arc = period_arc * self.spacing_ratio  # the arc between faces at effective_radius
        outer_radius = self.effective_radius + (self.tooth_height / 2)
        face_angle_rad = radians(self.face_angle)

        # cartesian isosceles trapezoid dimensions
        side_angle = face_angle_rad - (tooth_arc / 2)
        side_tangent_radius = sin(face_angle_rad) * self.effective_radius
        extra_side_angle = side_angle + acos(side_tangent_radius / outer_radius)

        tooth = cadquery.Workplane('XY', origin=(0, 0, -self.width / 2)) \
            .moveTo(
                side_tangent_radius * cos(side_angle),
                side_tangent_radius * sin(side_angle)
            )
        opposite_point = (
            -side_tangent_radius * cos(side_angle),
            side_tangent_radius * sin(side_angle)
        )
        if self.face_angle:
            tooth = tooth.lineTo(*opposite_point)
            #tooth = tooth.threePointArc(
            #    (0, -side_tangent_radius),
            #    opposite_point
            #)
        tooth = tooth.lineTo(
                -cos(extra_side_angle) * outer_radius,
                sin(extra_side_angle) * outer_radius
            )
        opposite_point = (
            cos(extra_side_angle) * outer_radius,
            sin(extra_side_angle) * outer_radius
        )
        if self.flat_top:
            tooth = tooth.lineTo(*opposite_point)
        else:
            tooth = tooth.threePointArc((0, outer_radius), opposite_point)
        tooth = tooth.close().extrude(self.width)

        return tooth

    def make(self):
        # create inside cylinder
        inner_radius = self.effective_radius - (self.tooth_height / 2)
        gear = cadquery.Workplane('XY', origin=(0, 0, -self.width / 2)) \
            .circle(inner_radius).extrude(self.width)

        # copy & rotate once per tooth
        tooth_template = self._make_tooth_template()

        period_arc = 360. / self.tooth_count
        for i in range(self.tooth_count):
            gear = gear.union(
                CoordSystem().rotated((0, 0, i * period_arc)) + tooth_template
            )

        return gear

    @property
    def mate_top(self):
        return Mate(self, CoordSystem((0, 0, self.width / 2)))

    @property
    def mate_bottom(self):
        return Mate(self, CoordSystem((0, 0, -self.width / 2)))
