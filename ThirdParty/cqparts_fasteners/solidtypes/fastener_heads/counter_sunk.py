import cadquery
from math import pi, cos, sin, sqrt

from cqparts.params import *

from .base import FastenerHead, register

# pull FreeCAD module from cadquery (workaround for torus)
FreeCAD = cadquery.freecad_impl.FreeCAD


@register(name='countersunk')
class CounterSunkFastenerHead(FastenerHead):
    """
    .. image:: /_static/img/fastenerheads/countersunk.png
    """
    chamfer = PositiveFloat(None)  # default to diameter / 20
    raised = PositiveFloat(0.0)  # if None, defaults to diameter / 10
    bugle = Boolean(False)
    bugle_ratio = FloatRange(0, 1, 0.5)

    def initialize_parameters(self):
        super(CounterSunkFastenerHead, self).initialize_parameters()
        if self.raised is None:
            self.raised = self.diameter / 10.
        if self.chamfer is None:
            self.chamfer = self.diameter / 20

    def make(self):
        cone_radius = self.diameter / 2
        cone_height = cone_radius  # to achieve a 45deg angle
        cylinder_radius = cone_radius - self.chamfer
        cylinder_height = self.height
        shaft_radius = (self.diameter / 2.) - self.height

        cone = cadquery.Workplane("XY").union(
            cadquery.CQ(cadquery.Solid.makeCone(0, cone_radius, cone_height)) \
                .translate((0, 0, -cone_height))
        )

        cylinder = cadquery.Workplane("XY") \
            .circle(cylinder_radius).extrude(-cylinder_height)

        head = cone.intersect(cylinder)

        # Raised bubble (if given)
        if self.raised:
            sphere_radius = ((self.raised ** 2) + (cylinder_radius ** 2)) / (2 * self.raised)

            sphere = cadquery.Workplane("XY").workplane(offset=-(sphere_radius - self.raised)) \
                .sphere(sphere_radius)
            raised_cylinder = cadquery.Workplane("XY").circle(cylinder_radius).extrude(self.raised)
            from Helpers import show

            raised_bubble = sphere.intersect(raised_cylinder)
            head = head.union(raised_bubble)

        # Bugle Head
        if self.bugle and (0 <= self.bugle_ratio < 1.0):
            # bugle_angle = angle head material makes with chamfer cylinder on top
            bugle_angle = (pi / 4) * self.bugle_ratio
            # face_span = longest straight distance along flat conical face (excluding chamfer)
            face_span = sqrt(2) * (((self.diameter / 2.) - self.chamfer) - shaft_radius)
            r2 = (face_span / 2.) / sin((pi / 4) - bugle_angle)
            d_height = r2 * sin(bugle_angle)
            r1 = (r2 * cos(bugle_angle)) + shaft_radius

            torus = cadquery.Workplane("XY").union(
                cadquery.CQ(cadquery.Solid.makeTorus(
                    r1, r2, # radii
                    pnt=FreeCAD.Base.Vector(0,0,0),
                    dir=FreeCAD.Base.Vector(0,0,1),
                    angleDegrees1=0.,
                    angleDegrees2=360.
                )).translate((0, 0, -(self.height + d_height)))
            )
            head = head.cut(torus)

        return head

    def make_cutter(self):
        """
        Add countersunk cone to cutter
        """
        obj = super(CounterSunkFastenerHead, self).make_cutter()
        cone = cadquery.CQ(cadquery.Solid.makeCone(
            radius1=self.diameter / 2,
            radius2=0,
            height=self.height,
            dir=cadquery.Vector(0,0,-1),
        ))
        return obj.union(cone)

    def get_face_offset(self):
        return (0, 0, self.raised)


@register(name='countersunk_raised')
class CounterSunkRaisedFastenerHead(CounterSunkFastenerHead):
    """
    .. image:: /_static/img/fastenerheads/countersunk_raised.png
    """
    raised = PositiveFloat(None)  # defaults to diameter / 10


@register(name='countersunk_bugle')
class CounterSunkBugleFastenerHead(CounterSunkFastenerHead):
    """
    .. image:: /_static/img/fastenerheads/countersunk_bugle.png
    """
    bugle = Boolean(True)
