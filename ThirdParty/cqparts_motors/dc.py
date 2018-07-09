"""
DC motor cqparts model
2018 Simon Kirkby obeygiantrobot@gmail.com
"""

import math
import cadquery as cq

import cqparts
from cqparts.params import PositiveFloat, String
from cqparts.display import render_props
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

from cqparts_motors import shaft, motor


# defines the profile of the motor , returns a wire
def _profile(shape, diam, thickness):
    work_plane = cq.Workplane("XY")
    if shape == "circle":
        profile = work_plane.circle(diam/2)

    if shape == "flat":
        radius = diam / 2
        half_thickness = thickness / 2
        intersect = math.sqrt(radius*radius-half_thickness*half_thickness)
        profile = work_plane.moveTo(0, half_thickness)\
           .lineTo(intersect, half_thickness)\
           .threePointArc((radius, 0), (intersect, -half_thickness))\
           .lineTo(0, -half_thickness)\
           .mirrorY()

    if shape == "rect":
        profile = work_plane.rect(thickness/2, diam/2)
    return profile

# the motor cup
class _Cup(cqparts.Part):
    height = PositiveFloat(25.1, doc="cup length")
    diam = PositiveFloat(20.4, doc="cup diameter")
    thickness = PositiveFloat(15.4, doc="cup thickness for flat profile")
    hole_spacing = PositiveFloat(12.4, doc="distance between the holes")
    hole_size = PositiveFloat(2, doc="hole size")
    step_diam = PositiveFloat(12, doc="step diameter")
    step_height = PositiveFloat(0, doc="height if step, if zero no step")
    bush_diam = PositiveFloat(6.15, doc="diameter of the bush")
    bush_height = PositiveFloat(1.6, doc="height of the bush")

    profile = String("flat", doc="profile shape (circle|flat|rect)")

    def make(self):
        # grab the correct profile
        work_plane = cq.Workplane("XY")
        cup = _profile(self.profile, self.diam, self.thickness)\
            .extrude(-self.height)
        if self.step_height > 0:
            step = work_plane.circle(self.step_diam/2).extrude(self.step_height)
            cup = cup.union(step)
        bush = work_plane.workplane(
            offset=self.step_height)\
            .circle(self.bush_diam/2)\
            .extrude(self.bush_height)
        cup = cup.union(bush)
        return cup

    def get_cutout(self, clearance=0):
        " get the cutout for the shaft"
        return cq.Workplane('XY', origin=(0, 0, 0)) \
            .circle((self.diam / 2) + clearance) \
            .extrude(10)

    @property
    def mate_bottom(self):
        " connect to the bottom of the cup"
        return Mate(self, CoordSystem(\
            origin=(0, 0, -self.height),\
            xDir=(1, 0, 0),\
            normal=(0, 0, 1)))


class _BackCover(cqparts.Part):
    height = PositiveFloat(6, doc="back length")
    diam = PositiveFloat(20.4, doc="back diameter")
    thickness = PositiveFloat(15.4, doc="back thickness for flat profile")
    profile = String("flat", doc="profile shape (circle|flat|rect)")
    bush_diam = PositiveFloat(6.15, doc="diameter of the bush")
    bush_height = PositiveFloat(1.6, doc="height of the bush")

    _render = render_props(color=(50, 255, 255))

    def make(self):
        # grab the correct profile
        work_plane = cq.Workplane("XY")
        back = work_plane.workplane(offset=-self.height)\
            .circle(self.bush_diam/2)\
            .extrude(-self.bush_height)
        if self.height > 0:
            back = _profile(self.profile, self.diam, self.thickness)\
            .extrude(-self.height)
            back = back.union(back)
        return back


class DCMotor(motor.Motor):
    """
    DC motors for models

    .. image:: /_static/img/motors/DCMotor.png
    """
    height = PositiveFloat(25.1, doc="motor length")
    diam = PositiveFloat(20.4, doc="motor diameter")
    thickness = PositiveFloat(15.4, doc="back thickness for flat profile")
    profile = String("flat", doc="profile shape (circle|flat|rect)")

    bush_diam = PositiveFloat(6.15, doc="diameter of the bush")
    bush_height = PositiveFloat(1.6, doc="height of the bush")

    shaft_type = shaft.Shaft #replace with other shaft
    shaft_length = PositiveFloat(11.55, doc="length of the shaft")
    shaft_diam = PositiveFloat(2, doc="diameter of the shaft")

    cover_height = PositiveFloat(0, doc="back cover height")

    # a step on the top surface
    step_height = PositiveFloat(0, doc="height if step, if zero no step")
    step_diam = PositiveFloat(12, doc="step diameter")

    def get_shaft(self):
        return self.shaft_type

    def mount_points(self):
        # TODO handle mount points
        pass

    def make_components(self):
        return {
            'body': _Cup(
                height=self.height,
                thickness=self.thickness,
                diam=self.diam,
                profile=self.profile,
                bush_diam=self.bush_diam,
                bush_height=self.bush_height,
                step_height=self.step_height
            ),
            'shaft': self.shaft_type(length=self.shaft_length, diam=self.shaft_diam),
            'back': _BackCover(
                height=self.cover_height,
                thickness=self.thickness,
                diam=self.diam,
                profile=self.profile,
                bush_diam=self.bush_diam,
                bush_height=self.bush_height
            )
        }

    def make_constraints(self):
        return [
            Fixed(self.components['body'].mate_origin),
            Coincident(
                self.components['shaft'].mate_origin,
                self.components['body'].mate_origin,
            ),
            Coincident(
                self.components['back'].mate_origin,
                self.components['body'].mate_bottom,
            )
        ]
