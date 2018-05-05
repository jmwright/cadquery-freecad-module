
from math import pi, radians
from math import sin, cos, tan, asin, atan2
from math import sqrt

import cadquery

import cqparts
from cqparts.params import *
from cqparts import constraint
from cqparts.utils import CoordSystem

from . import register


class _InnerRing(cqparts.Part):
    inner_diam = PositiveFloat(None, doc="inside diameter")
    height = PositiveFloat(None, doc="height of ring")
    base_height = Float(None, doc="base location on Z axis (usually negative)")

    # cone parameters
    roller_surface_radius = PositiveFloat(None, doc="radius of rolling surface at XY plane")
    roller_surface_gradient = Float(None, doc="rolling surface gradient along +Z axis")

    def make(self):

        cone_radius_at = lambda z: self.roller_surface_radius + (self.roller_surface_gradient * z)
        cone_radius_base = cone_radius_at(self.base_height)
        cone_radius_top = cone_radius_at(self.base_height + self.height)

        # ring base shape
        inner_ring = cadquery.Workplane('XY', origin=(0, 0, self.base_height)) \
            .circle(max(cone_radius_base, cone_radius_top)) \
            .circle(self.inner_diam / 2) \
            .extrude(self.height)

        # intersect cone with base shape (provides conical rolling surface)
        if abs(self.roller_surface_gradient) > 1e-6:
            cone = cadquery.CQ(cadquery.Solid.makeCone(
                radius1=cone_radius_base,
                radius2=cone_radius_top,
                height=self.height,
                dir=cadquery.Vector(0, 0, 1),
            )).translate((0, 0, self.base_height))
            inner_ring = inner_ring.intersect(cone)

        return inner_ring


class _OuterRing(cqparts.Part):
    outer_diam = PositiveFloat(None, doc="outside diameter")
    height = PositiveFloat(None, doc="height of ring")
    base_height = Float(None, doc="base location on Z axis (usually negative)")

    # cone parameters
    roller_surface_radius = PositiveFloat(None, doc="radius of rolling surface at XY plane")
    roller_surface_gradient = Float(None, doc="rolling surface gradient along +Z axis")

    def make(self):

        # cone radii
        cone_radius_at = lambda z: self.roller_surface_radius + (self.roller_surface_gradient * z)
        cone_radius_base = cone_radius_at(self.base_height)
        cone_radius_top = cone_radius_at(self.base_height + self.height)

        # ring base shape
        outer_ring = cadquery.Workplane('XY', origin=(0, 0, self.base_height)) \
            .circle(self.outer_diam / 2).extrude(self.height)

        # cut cone from base shape (provides conical rolling surface)
        if abs(self.roller_surface_gradient) > 1e-6:
            cone = cadquery.CQ(cadquery.Solid.makeCone(
                radius1=cone_radius_base,
                radius2=cone_radius_top,
                height=self.height,
                dir=cadquery.Vector(0, 0, 1),
            )).translate((0, 0, self.base_height))
            outer_ring = outer_ring.cut(cone)
        else:
            outer_ring = outer_ring.faces('>Z') \
                .circle(self.roller_surface_radius).cutThruAll()

        return outer_ring


class _Roller(cqparts.Part):
    height = PositiveFloat(None, doc="roller height")
    radius = PositiveFloat(None, doc="radius of roller at XY plane intersection")
    gradient = Float(None, doc="conical surface gradient (zero is cylindrical)")
    base_height = Float(None, doc="height along Z axis of roller base")

    def make(self):
        cone_radius_at = lambda z: self.radius + (self.gradient * z)
        cone_radius_base = cone_radius_at(self.base_height)
        cone_radius_top = cone_radius_at(self.base_height + self.height)

        # intersect cone with base shape (provides conical rolling surface)
        if abs(self.gradient) > 1e-6:
            roller = cadquery.CQ(cadquery.Solid.makeCone(
                radius1=cone_radius_base,
                radius2=cone_radius_top,
                height=self.height,
                dir=cadquery.Vector(0, 0, 1),
            )).translate((0, 0, self.base_height))
        else:
            roller = cadquery.Workplane('XY', origin=(0, 0, self.base_height)) \
                .circle(self.radius).extrude(self.height)

        return roller


class _RollerRing(cqparts.Assembly):
    rolling_radius = PositiveFloat(None, doc="distance from bearing center to rolling element rotation axis along XY plane")
    roller_diam = PositiveFloat(None, doc="diamter of roller at cross-section perpendicular to roller's rotation axis where bearing's axis meets XY plane")
    roller_height = PositiveFloat(None, doc="length of roller along its rotational axis")
    roller_angle = Float(None, doc="tilt of roller's rotation axis (unit: degrees)")
    roller_count = IntRange(3, None, None, doc="number of rollers")

    def _roller_params(self):
        # Conical rollers
        focal_length = tan(radians(90 - self.roller_angle)) * self.rolling_radius
        cone_angle = atan2(  # 1/2 angle made by cone's point (unit: radians)
            (self.roller_diam / 2),
            sqrt(focal_length ** 2 + self.rolling_radius ** 2)
        )

        gradient = -tan(cone_angle) * (1 if self.roller_angle > 0 else -1)

        return {
            'height': self.roller_height,
            'radius': self.roller_diam / 2,
            'gradient': gradient,
            'base_height': -self.roller_height / 2,
        }

    @classmethod
    def _roller_name(cls, index):
        return 'roller_%03i' % index

    def make_components(self):
        roller_params = self._roller_params()
        return {
            self._roller_name(i): _Roller(**roller_params)
            for i in range(self.roller_count)
        }

    def make_constraints(self):
        constraints = []
        for i in range(self.roller_count):
            obj = self.components[self._roller_name(i)]
            angle = i * (360. / self.roller_count)
            constraints.append(constraint.Fixed(
                obj.mate_origin,
                CoordSystem().rotated((0, 0, angle)) + CoordSystem(
                    origin=(self.rolling_radius, 0, 0),
                ).rotated((0, -self.roller_angle, 0))
            ))
        return constraints


@register(name='taperedrollerbearing')
class TaperedRollerBearing(cqparts.Assembly):
    """
    Taperd roller bearing, with conical rolling elements

    .. image:: /_static/img/bearings/tapered-roller-bearing.png

    """

    inner_diam = PositiveFloat(20, doc="inner diameter")
    outer_diam = PositiveFloat(50, doc="outer diameter")
    height = PositiveFloat(10, doc="bearing height")

    # roller parameters
    rolling_radius = PositiveFloat(None, doc="distance from bearing center to rolling element rotation axis along XY plane")
    roller_diam = PositiveFloat(None, doc="diamter of roller at cross-section perpendicular to roller's rotation axis where bearing's axis meets XY plane")
    roller_height = PositiveFloat(8, doc="length of roller along its rotational axis")
    roller_angle = FloatRange(-45, 45, 10, doc="tilt of roller's rotation axis (unit: degrees)")
    roller_min_gap = PositiveFloat(None, doc="minimum gap between rollers")
    roller_count = IntRange(3, None, None, doc="number of rollers")

    tolerance = PositiveFloat(0.001, doc="gap between rollers and their tracks")

    def initialize_parameters(self):
        if self.roller_diam is None:
            self.roller_diam = ((self.outer_diam - self.inner_diam) / 2) / 3

        if self.rolling_radius is None:
            radial_depth = (self.outer_diam - self.inner_diam) / 2
            self.rolling_radius = (self.inner_diam / 2) + (0.5 * radial_depth)

        if self.roller_min_gap is None:
            self.roller_min_gap = self.roller_diam * 0.1  # default 10% roller diameter

        if self.roller_count is None:
            self.roller_count = min(self.max_roller_count, 12)

    @property
    def max_roller_count(self):
        """
        The maximum number of balls given ``rolling_radius`` and ``roller_diam``

        :return: maximum roller count
        :rtype: :class:`int`

        .. note::

            Calculation is innacurate, it assumes the roller's cross-section on
            a horizontal plane is circular, however a rotated cone's cross-section will
            be closer to eliptical than circular.
        """

        min_arc = asin(((self.roller_diam + self.roller_min_gap) / 2) / self.rolling_radius) * 2
        return int((2 * pi) / min_arc)

    def _roller_surface_params(self, inner):
        """
        Inner & outer conical parameters derrived from higher-level parameters

        :param inner: if True inner conical surface parameters given, else outer
        :type inner: :class:`bool`
        :return: ``**kwargs`` style dict for use in ring parts
        :rtype: :class:`dict`

        return example::

            {
                'roller_surface_radius': 25,  # radius of cone at XY plane
                'roller_surface_gradient': 0.1,  # rate of change of radius along z axis.
            }
        """

        if self.roller_angle == 0:
            # Rollers are cylindrical, the maths gets a lot simpler
            radius_delta = (self.roller_diam / 2) + self.tolerance
            gradient = 0
            if inner:
                radius = self.rolling_radius - radius_delta
            else:
                radius = self.rolling_radius + radius_delta
        else:
            # Conical rollers
            focal_length = tan(radians(90 - self.roller_angle)) * self.rolling_radius
            cone_angle = atan2(  # 1/2 angle made by cone's point (unit: radians)
                (self.roller_diam / 2),
                sqrt(focal_length ** 2 + self.rolling_radius ** 2)
            )

            multiplier = 1
            multiplier *= -1 if inner else 1
            multiplier *= 1 if (self.roller_angle > 0) else -1
            gradient = -tan(radians(self.roller_angle) + (cone_angle * multiplier))

            radius = gradient * -focal_length
            radius = radius + (-self.tolerance if inner else self.tolerance)

        return {
            'roller_surface_radius': radius,  # radius of cone at XY plane
            'roller_surface_gradient': gradient,  # rate of change of radius along z axis.
        }

    def make_components(self):
        return {
            'inner_ring': _InnerRing(
                inner_diam=self.inner_diam,
                height=self.height,
                base_height=-self.height / 2,
                **self._roller_surface_params(inner=True)
            ),
            'outer_ring': _OuterRing(
                outer_diam=self.outer_diam,
                height=self.height,
                base_height=-self.height / 2,
                **self._roller_surface_params(inner=False)
            ),
            'rolling_elements': _RollerRing(
                rolling_radius=self.rolling_radius,
                roller_diam=self.roller_diam,
                roller_height=self.roller_height,
                roller_angle=self.roller_angle,
                roller_count=self.roller_count,
            ),
        }

    def make_constraints(self):
        inner = self.components['inner_ring']
        outer = self.components['outer_ring']
        return [
            constraint.Fixed(inner.mate_origin),
            constraint.Coincident(
                outer.mate_origin,
                inner.mate_origin
            ),
        ]
