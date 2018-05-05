import cadquery
from math import pi, cos, sin, sqrt

from cqparts.params import *

from .base import FastenerHead, register


class DrivenFastenerHead(FastenerHead):
    chamfer = PositiveFloat(None, doc="chamfer value (default: :math:`d/15`)")  # default to diameter / 10
    chamfer_top = Boolean(True, doc="if chamfer is set, top edges are chamfered (conical)")
    chamfer_base = Boolean(False, doc="if chamfer is set, base edges are chamfered (conical)")
    edges = PositiveInt(4, doc="number of edges on fastener head")
    width = PositiveFloat(None, doc="distance between flats")  # defaults based on number of edges, and diameter

    # Washer (optional)
    washer = Boolean(False)
    washer_height = PositiveFloat(None)  # default to height / 6
    washer_diameter = PositiveFloat(None)  # default to diameter * 1.2

    def initialize_parameters(self):
        if self.width is not None:
            # Set diameter based on witdh (ignore given diameter)
            # (width is the size of the wrench used to drive it)
            self.diameter = self.width / cos(pi / self.edges)
        if self.chamfer is None:
            self.chamfer = self.diameter / 15
        if self.washer_height is None:
            self.washer_height = self.height / 6
        if self.washer_diameter is None:
            self.washer_diameter = self.diameter * 1.2
        super(DrivenFastenerHead, self).initialize_parameters()

    def _default_access_diameter(self):
        # driven heads need more clearance
        if self.washer:
            return max((  # the greater of...
                self.diameter * 1.5,  # 150% head's diameter
                self.washer_diameter * 1.1  # 110% washer diameter
            ))
        return self.diameter * 1.2

    def get_cross_section_points(self):
        points = []
        d_angle = pi / self.edges
        radius = self.diameter / 2.
        for i in range(self.edges):
            angle = d_angle + ((2 * d_angle) * i)
            points.append((
                sin(angle) * radius,
                cos(angle) * radius
            ))
        return points

    def make(self):
        points = self.get_cross_section_points()
        head = cadquery.Workplane("XY") \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(self.height)

        if self.chamfer:
            cone_height = ((self.diameter / 2.) - self.chamfer) + self.height
            cone_radius = (self.diameter / 2.) + (self.height - self.chamfer)
            if self.chamfer_top:
                cone = cadquery.Workplane('XY').union(cadquery.CQ(cadquery.Solid.makeCone(
                    cone_radius, 0, cone_height,
                    pnt=cadquery.Vector(0, 0, 0),
                    dir=cadquery.Vector(0, 0, 1),
                )))
                head = head.intersect(cone)

            if self.chamfer_base:
                cone = cadquery.Workplane('XY').union(cadquery.CQ(cadquery.Solid.makeCone(
                    cone_radius, 0, cone_height,
                    pnt=cadquery.Vector(0, 0, self.height),
                    dir=cadquery.Vector(0, 0, -1),
                )))
                head = head.intersect(cone)

        # Washer
        if self.washer:
            washer = cadquery.Workplane("XY") \
                .circle(self.washer_diameter / 2) \
                .extrude(self.washer_height)
            head = head.union(washer)

        return head


@register(name='square')
class SquareFastenerHead(DrivenFastenerHead):
    """
    .. image:: /_static/img/fastenerheads/square.png
    """
    edges = PositiveInt(4)


@register(name='hex')
class HexFastenerHead(DrivenFastenerHead):
    """
    .. image:: /_static/img/fastenerheads/hex.png
    """
    edges = PositiveInt(6)


@register(name='hex_flange')
class HexFlangeFastenerHead(DrivenFastenerHead):
    """
    .. image:: /_static/img/fastenerheads/hex_flange.png
    """
    edges = PositiveInt(6)
    washer = Boolean(True)
