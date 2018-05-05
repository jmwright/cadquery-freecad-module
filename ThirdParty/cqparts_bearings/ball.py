
from math import pi, radians, sin, cos, asin

import cadquery

import cqparts
from cqparts.params import *
from cqparts import constraint
from cqparts.constraint import Mate
from cqparts.utils import CoordSystem

from . import register


class _Ring(cqparts.Part):
    # Basic shape
    outer_radius = PositiveFloat(10, doc="outside radius")
    inner_radius = PositiveFloat(8, doc="inside radius")
    width = PositiveFloat(5, doc="ring's width")

    # Ball rails
    ball_radius = PositiveFloat(3, doc="ball bearing radius")
    rolling_radius = PositiveFloat(6, doc="distance of ball's center from bearing's axis")

    @classmethod
    def get_ball_torus(cls, rolling_radius, ball_radius):
        return cadquery.Workplane("XY").union(
            cadquery.CQ(cadquery.Solid.makeTorus(
                rolling_radius, ball_radius, # radii
                pnt=cadquery.Vector(0,0,0).wrapped,
                dir=cadquery.Vector(0,0,1).wrapped,
                angleDegrees1=0.,
                angleDegrees2=360.,
            ))
        )

    def get_ring(self):
        return cadquery.Workplane('XY', origin=(0, 0, -self.width / 2)) \
            .circle(self.outer_radius).circle(self.inner_radius) \
            .extrude(self.width)

    def make(self):
        ring = self.get_ring()
        torus = self.get_ball_torus(self.rolling_radius, self.ball_radius)
        return ring.cut(torus)

    def make_simple(self):
        return self.get_ring()

    def get_mate_center(self, angle=0):
        """
        Mate at ring's center rotated ``angle`` degrees.

        :param angle: rotation around z-axis (unit: deg)
        :type angle: :class:`float`

        :return: mate in ring's center rotated about z-axis
        :rtype: :class:`Mate <cqparts.constraint.Mate>`
        """
        return Mate(self, CoordSystem.from_plane(
            cadquery.Plane(
                origin=(0, 0, self.width / 2),
                xDir=(1, 0, 0),
                normal=(0, 0, 1),
            ).rotated((0, 0, angle))  # rotate about z-axis
        ))


class _Ball(cqparts.Part):
    radius = PositiveFloat(10, doc="radius of sphere")

    def make(self):
        return cadquery.Workplane('XY').sphere(self.radius)


class _BallRing(cqparts.Assembly):
    rolling_radius = PositiveFloat(8, doc="radius at which the balls roll (default: half way between outer & inner radii)")
    ball_diam = PositiveFloat(3, doc="diameter of ball bearings (default: distance between outer and inner radii / 2)")
    ball_count = IntRange(3, None, 8, doc="number of ball bearings in ring")
    angle = Float(0, doc="bearing's inner ring's rotation (unit: deg)")

    @classmethod
    def ball_name(cls, index):
        return 'ball_%03i' % index

    @classmethod
    def get_max_ballcount(cls, ball_diam, rolling_radius, min_gap=0.):
        """
        The maximum number of balls given ``rolling_radius`` and ``ball_diam``

        :param min_gap: minimum gap between balls (measured along vector between
                        spherical centers)
        :type min_gap: :class:`float`
        :return: maximum ball count
        :rtype: :class:`int`
        """

        min_arc = asin(((ball_diam + min_gap) / 2) / rolling_radius) * 2
        return int((2 * pi) / min_arc)

    def make_components(self):
        components = {}
        for i in range(self.ball_count):
            components[self.ball_name(i)] = _Ball(radius=self.ball_diam / 2)
        return components

    def make_constraints(self):
        constraints = []

        ball_angle = -radians(self.angle * 2)
        rail_angle_delta = radians(self.angle / 2)
        for i in range(self.ball_count):
            # crude, innacruate calculation. justification: ball position is just illustrative
            ball = self.components[self.ball_name(i)]
            arc_angle = i * ((pi * 2) / self.ball_count)
            rail_angle = arc_angle + rail_angle_delta
            constraints.append(constraint.Fixed(
                ball.mate_origin,
                CoordSystem(
                    origin=(
                        self.rolling_radius * cos(rail_angle),
                        self.rolling_radius * sin(rail_angle),
                        0,
                    ),
                    xDir=(cos(ball_angle), sin(ball_angle), 0),
                    normal=(0, 0, 1),
                )
            ))

        return constraints


@register(name='ballbearing')
class BallBearing(cqparts.Assembly):
    """
    Ball bearing

    .. image:: /_static/img/bearings/ball-bearing.png

    """


    # Inner & Outer Rings
    outer_diam = PositiveFloat(30, doc="outer diameter")
    outer_width = PositiveFloat(None, doc="outer ring's thickness (default maximum / 3)")
    inner_diam = PositiveFloat(10, doc="inner diameter")
    inner_width = PositiveFloat(None, doc="inner ring's thickness (default maximum / 3)")
    width = PositiveFloat(5, doc="bearing width")

    # Rolling Elements
    ball_diam = PositiveFloat(None, doc="diameter of ball bearings (default: distance between outer and inner radii / 2)")
    rolling_radius = PositiveFloat(None, doc="radius at which the balls roll (default: half way between outer & inner radii)")
    tolerance = PositiveFloat(0.001, doc="gap between rolling elements and their tracks")
    ball_count = IntRange(3, None, None, doc="number of ball bearings")
    ball_min_gap = PositiveFloat(None, doc="minimum gap between balls (measured along vector between spherical centers) (default: ``ball_diam`` / 10)")

    # Dynamic
    angle = Float(0, doc="bearing's inner ring's rotation (unit: deg)")

    def initialize_parameters(self):
        if self.inner_diam >= self.outer_diam:
            raise ValueError("inner diameter exceeds outer: %r >= %r" % (
                self.inner_diam, self.outer_diam
            ))

        # --- Inner & Outer Rings
        if self.outer_width is None:
            self.outer_width = ((self.outer_diam - self.inner_diam) / 2) / 3

        if self.inner_width is None:
            self.inner_width = ((self.outer_diam - self.inner_diam) / 2) / 3

        # --- Rolling elements
        if self.rolling_radius is None:
            self.rolling_radius = (((self.outer_diam - self.inner_diam) / 2) + self.inner_diam) / 2

        if self.ball_diam is None:
            self.ball_diam = (self.outer_diam - self.inner_diam) / 4

        if (self.rolling_radius + (self.ball_diam / 2)) > (self.outer_diam / 2):
            raise ValueError("rolling elements will protrude through outer ring")
        elif (self.rolling_radius - (self.ball_diam / 2)) < (self.inner_diam / 2):
            raise ValueError("rolling elements will protrude through inner ring")

        if self.ball_min_gap is None:
            self.ball_min_gap = self.ball_diam / 10

        if self.ball_count is None:
            self.ball_count = _BallRing.get_max_ballcount(
                ball_diam=self.ball_diam,
                rolling_radius=self.rolling_radius,
                min_gap=self.ball_min_gap,
            )
        else:
            max_ballcount = _BallRing.get_max_ballcount(
                ball_diam=self.ball_diam,
                rolling_radius=self.rolling_radius,
            )
            if self.ball_count > max_ballcount:
                raise ValueError("%r balls cannot fit in bearing" % self.ball_count)

        super(BallBearing, self).initialize_parameters()

    def make_components(self):
        return {
            'outer_ring': _Ring(
                outer_radius=self.outer_diam / 2,
                inner_radius=(self.outer_diam / 2) - self.outer_width,
                width=self.width,
                ball_radius=(self.ball_diam / 2) + self.tolerance,
                rolling_radius=self.rolling_radius,
            ),
            'inner_ring': _Ring(
                outer_radius=(self.inner_diam / 2) + self.inner_width,
                inner_radius=self.inner_diam / 2,
                width=self.width,
                ball_radius=(self.ball_diam / 2) + self.tolerance,
                rolling_radius=self.rolling_radius,
            ),
            'rolling_elements': _BallRing(
                rolling_radius=self.rolling_radius,
                ball_diam=self.ball_diam,
                ball_count=self.ball_count,
                angle=self.angle,
            ),
        }

    def make_constraints(self):
        outer = self.components['outer_ring']
        inner = self.components['inner_ring']
        ring = self.components['rolling_elements']
        constraints = [
            constraint.Fixed(outer.mate_origin),
            constraint.Coincident(
                inner.get_mate_center(angle=0),
                outer.get_mate_center(angle=self.angle)
            ),
            constraint.Coincident(ring.mate_origin, outer.mate_origin),
        ]
        # rolling elements
        # FIXME: use a more sensible constraint when available (see issue #30)

        return constraints

    def get_cutter(self):
        cutter = cadquery.Workplane('XY', origin=(0, 0, -self.width / 2)) \
            .circle(self.outer_diam / 2).extrude(self.width)
        if self.ball_diam > self.width:
            cutter = cutter.union(_Ring.get_ball_torus(self.rolling_radius, self.ball_diam / 2))
        return cutter

    @property
    def mate_axis_start(self):
        return Mate(self, CoordSystem(origin=(0, 0, -self.width / 2)))

    @property
    def mate_axis_center(self):
        return self.mate_origin

    @property
    def mate_axis_end(self):
        return Mate(self, CoordSystem(origin=(0, 0, self.width / 2)))
