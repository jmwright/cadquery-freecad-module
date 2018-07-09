import cadquery

import cqparts
from cqparts.params import *

from cqparts.utils import property_buffered
from cqparts.display.material import render_props
from cqparts.constraint import Mate
from cqparts.utils import CoordSystem


class _Track(cqparts.Part):

    double_sided = Boolean(True, doc="if set, track is cut from both sides")

    # Profile Metrics
    width = PositiveFloat(30, doc="track width")
    depth = PositiveFloat(8, doc="track thickness")
    track_guage = PositiveFloat(None, doc="distance between wheel centers")
    track_width = PositiveFloat(None, doc="wheel's width")
    track_depth = PositiveFloat(2, doc="depth each track is cut")
    track_chamfer = PositiveFloat(None, doc="chamfer at wheel's edges")

    # Connector
    conn_diam = PositiveFloat(None, doc="diameter of connector circle")
    conn_neck_width = PositiveFloat(None, doc="connector neck width")
    conn_neck_length = PositiveFloat(None, doc="connector neck length")
    conn_clearance = PositiveFloat(0.5, doc="clearance ")

    _render = render_props(template='wood')

    def initialize_parameters(self):
        super(_Track, self).initialize_parameters()

        if self.track_guage is None:
            self.track_guage = self.width * (2. / 3)
        if self.track_width is None:
            self.track_width = self.track_guage / 4
        if self.track_depth is None:
            self.track_depth = self.track_width / 2
        if self.track_chamfer is None:
            self.track_chamfer = self.track_depth / 3

        if self.conn_diam is None:
            self.conn_diam = self.depth
        if self.conn_neck_width is None:
            self.conn_neck_width = self.conn_diam / 3
        if self.conn_neck_length is None:
            self.conn_neck_length = self.conn_diam * 0.6

    @property
    def _wheel_profile(self):

        if self.track_chamfer:

            left_side = (self.track_guage / 2) - (self.track_width / 2)
            points = [
                (left_side - (self.track_chamfer * 2), (self.depth / 2) + self.track_depth),
                (left_side - (self.track_chamfer * 2), (self.depth / 2) + self.track_chamfer),
                (left_side, (self.depth / 2) - self.track_chamfer), # remove if self.track_chamfer == 0
                (left_side, (self.depth / 2) - self.track_depth),
            ]
            # mirror over x = self.track_guage / 2 plane
            points += [(self.track_guage - x, y) for (x, y) in reversed(points)]

        else:
            # no chamfer, just plot the points for a rectangle
            points = [
                ((self.track_guage / 2) - (self.track_width / 2), (self.depth / 2) + self.track_depth),
                ((self.track_guage / 2) - (self.track_width / 2), (self.depth / 2) - self.track_depth),
                ((self.track_guage / 2) + (self.track_width / 2), (self.depth / 2) - self.track_depth),
                ((self.track_guage / 2) + (self.track_width / 2), (self.depth / 2) + self.track_depth),
            ]

        flip = lambda p, xf, yf: (p[0] * xf, p[1] * yf)

        profile = cadquery.Workplane('XZ') \
            .moveTo(*flip(points[0], 1, 1)).polyline([flip(p, 1, 1) for p in points[1:]]).close() \
            .moveTo(*flip(points[0], -1, 1)).polyline([flip(p, -1, 1) for p in points[1:]]).close()
        if self.double_sided:
            profile = profile \
                .moveTo(*flip(points[0], 1, -1)).polyline([flip(p, 1, -1) for p in points[1:]]).close() \
                .moveTo(*flip(points[0], -1, -1)).polyline([flip(p, -1, -1) for p in points[1:]]).close()

        return profile

    @property
    def _track_profile(self):
        return cadquery.Workplane('XZ').rect(self.width, self.depth)

    def _get_connector(self, clearance=False):
        clear_dist = self.conn_clearance if clearance else 0.
        return cadquery.Workplane('XY').box(
            self.conn_neck_width + (clear_dist * 2),
            self.conn_neck_length + self.conn_diam / 2,
            self.depth,
            centered=(True, False, True),
        ).union(cadquery.Workplane('XY', origin=(
            0, self.conn_neck_length + self.conn_diam / 2, -self.depth / 2
        )).circle((self.conn_diam / 2) + clear_dist).extrude(self.depth))

    @property
    def conn_length(self):
        return self.conn_neck_length + self.conn_diam


class StraightTrack(_Track):
    """
    .. image:: /_static/img/toys/track-straight.png
    """

    length = PositiveFloat(100, doc="track length")

    def make(self):
        track = self._track_profile.extrude(self.length) \
            .translate((0, self.length / 2, 0)) \
            .union(self._get_connector().translate((0, self.length / 2, 0))) \
            .cut(self._get_connector(True).translate((0, -self.length / 2, 0)))

        # cut tracks
        track = track.cut(
            self._wheel_profile \
                .extrude(self.length + self.conn_length) \
                .translate((0, self.length / 2 + self.conn_length, 0))
        )

        return track

    def make_simple(self):
        return self._track_profile.extrude(self.length) \
            .translate((0, self.length / 2, 0))

    @property
    def mate_start(self):
        return Mate(self, CoordSystem((0, -self.length / 2, 0)))

    @property
    def mate_end(self):
        return Mate(self, CoordSystem((0, self.length / 2, 0)))


class CurvedTrack(_Track):
    """
    .. image:: /_static/img/toys/track-curved.png
    """

    turn_radius = Float(100, doc="radius of turn")
    turn_angle = FloatRange(0, 360, 45, doc="arc angle covered by track (unit: degrees)")

    def make(self):
        revolve_params = {
            'angleDegrees': self.turn_angle,
            'axisStart': (self.turn_radius, 0),
            'axisEnd': (self.turn_radius, 1 if (self.turn_radius > 0) else -1),
        }

        track = self._track_profile.revolve(**revolve_params) \
            .translate((-self.turn_radius, 0, 0)) \
            .cut(self.mate_start.local_coords + self._get_connector(True)) \
            .union(self.mate_end.local_coords + self._get_connector(False))

        # cut tracks
        track = track.cut(
            self._wheel_profile.revolve(**revolve_params) \
                .translate((-self.turn_radius, 0, 0))
        )
        track = track.cut(
            self.mate_end.local_coords + self._wheel_profile.extrude(-self.conn_length)
        )

        return track
        #return self._wheel_profile.extrude(self.conn_length)

    def make_simple(self):
        return self._track_profile.revolve(
                angleDegrees=self.turn_angle,
                axisStart=(self.turn_radius, 0),
                axisEnd=(self.turn_radius, 1),
        ).translate((-self.turn_radius, 0, 0)) \

    @property
    def mate_start(self):
        return Mate(self, CoordSystem((-self.turn_radius, 0, 0)))

    @property
    def mate_end(self):
        angle = self.turn_angle if (self.turn_radius < 0) else -self.turn_angle
        return Mate(self, CoordSystem().rotated((0, 0, angle)) + self.mate_start.local_coords)
