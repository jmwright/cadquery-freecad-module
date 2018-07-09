
""" cqparts motors
 2018 Simon Kirkby obeygiantrobot@gmail.com
 stepper motor generic
"""

# TODO
# even 4 fasteners so it auto mounts to whatever it is parented to.

import cadquery as cq

import cqparts
from cqparts.params import PositiveFloat
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.display import render_props
from cqparts.utils.geometry import CoordSystem

import shaft
import motor

class _EndCap(cqparts.Part):
    # Parameters
    width = PositiveFloat(42.3, doc="Motor Size")
    length = PositiveFloat(10, doc="End length")
    cham = PositiveFloat(3, doc="chamfer")

    # _render = render_props(color=(50, 50, 50),alpha=0.4)
    def make(self):
        base = cq.Workplane("XY")\
            .box(self.width, self.width, self.length)\
            .edges("|Z")\
            .chamfer(self.cham)
        return base

    @property
    def mate_top(self):
        " connect to the end of the top cap"
        return Mate(self, CoordSystem(
            origin=(0, 0, -self.length/2),
            xDir=(0, 1, 0),
            normal=(0, 0, -1)
            ))

    @property
    def mate_bottom(self):
        " bottom of the top cap"
        return Mate(self, CoordSystem(
            origin=(0, 0, -self.length/2),
            xDir=(0, 1, 0),
            normal=(0, 0, 1)
            ))


class _Stator(cqparts.Part):
    # Parameters
    width = PositiveFloat(40.0, doc="Motor Size")
    length = PositiveFloat(20, doc="stator length")
    cham = PositiveFloat(3, doc="chamfer")

    _render = render_props(color=(50, 50, 50))

    def make(self):
        base = cq.Workplane("XY")\
            .box(self.width, self.width, self.length,centered=(True,True,True))\
            .edges("|Z")\
            .chamfer(self.cham)
        return base

    @property
    def mate_top(self):
        " top of the stator"
        return Mate(self, CoordSystem(
            origin=(0, 0, self.length/2),
            xDir=(0, 1, 0),
            normal=(0, 0, 1)
            ))

    @property
    def mate_bottom(self):
        " bottom of the stator"
        return Mate(self, CoordSystem(
            origin=(0, 0, -self.length/2),
            xDir=(1, 0, 0),
            normal=(0, 0, -1)
            ))


class _StepperMount(_EndCap):
    spacing = PositiveFloat(31, doc="hole spacing")
    hole_size = PositiveFloat(3, doc="hole size")
    boss = PositiveFloat(22, doc="boss size")
    boss_length = PositiveFloat(2, doc="boss_length")

    def make(self):
        obj = super(_StepperMount, self).make()
        obj.faces(">Z").workplane() \
            .rect(self.spacing, self.spacing, forConstruction=True)\
            .vertices() \
            .hole(self.hole_size)
        obj.faces(">Z").workplane()\
            .circle(self.boss/2).extrude(self.boss_length)
        return obj

    @property
    def mate_top(self):
        " top of the mount"
        return Mate(self, CoordSystem(
            origin=(0, 0, self.length/2),
            xDir=(0, 1, 0),
            normal=(0, 0, 1)
            ))

    @property
    def mate_bottom(self):
        " bottom of the mount"
        return Mate(self, CoordSystem(
            origin=(0, 0,-self.length/2),
            xDir=(0, 1, 0),
            normal=(0, 0, 1)
            ))


class _Back(_EndCap):
    spacing = PositiveFloat(31, doc="hole spacing")
    hole_size = PositiveFloat(3, doc="hole size")

    def make(self):
        obj = super(_Back, self).make()
        obj.faces(">Z").workplane() \
            .rect(self.spacing, self.spacing, forConstruction=True)\
            .vertices() \
            .hole(self.hole_size)
        return obj


class Stepper(motor.Motor):
    " Stepper Motor , simple rendering "
    shaft_type = shaft.Shaft

    width = PositiveFloat(42.3, doc="width and depth of the stepper")
    length = PositiveFloat(50, doc="length of the stepper")
    hole_spacing = PositiveFloat(31.0, doc="distance between centers")
    hole_size = PositiveFloat(3, doc="hole diameter , select screw with this")
    boss_size = PositiveFloat(22, doc="diameter of the raise circle")
    boss_length = PositiveFloat(2, doc="length away from the top surface")

    shaft_diam = PositiveFloat(5, doc="diameter of the the shaft ")
    shaft_length = PositiveFloat(24, doc="length from top surface")

    def get_shaft(self):
        return self.components['shaft']

    def mount_points(self):
        " return mount points"
        wp = cq.Workplane("XY")
        h = wp.rect(self.hole_spacing,self.hole_spacing
                    ,forConstruction=True).vertices()
        return h.objects

    def make_components(self):
        sec = self.length / 6
        return {
            'topcap': _StepperMount(
                width=self.width,
                length=sec,
                spacing=self.hole_spacing,
                hole_size=self.hole_size,
                boss=self.boss_size
            ),
            'stator': _Stator(width=self.width-3, length=sec*4),
            'botcap': _Back(
                width=self.width,
                length=sec,
                spacing=self.hole_spacing,
                hole_size=self.hole_size,
            ),
            'shaft': self.shaft_type(
                length=self.shaft_length,
                diam=self.shaft_diam)
            }

    def make_constraints(self):
        return [
            Fixed(self.components['topcap'].mate_top),
            Coincident(
                self.components['stator'].mate_top,
                self.components['topcap'].mate_bottom,
            ),
            Coincident(
                self.components['botcap'].mate_bottom,
                self.components['stator'].mate_bottom
            ),
            Coincident(
                self.components['shaft'].mate_origin,
                self.components['topcap'].mate_top
            ),
            ]

    def apply_cutout(self):
        " shaft cutout "
        stepper_shaft = self.components['shaft']
        top = self.components['topcap']
        local_obj = top.local_obj
        local_obj = local_obj.cut(stepper_shaft.get_cutout(clearance=0.5))

    def make_alterations(self):
        self.apply_cutout()

    def boss_cutout(self,clearance=0):
        bc = cq.Workplane("XY")\
            .circle(self.boss_size/2)\
            .extrude(self.shaft_length)
        return bc

    def cut_boss(self,part,clearance=0):
        co = self.boss_cutout(clearance=clearance)
        lo = part.local_obj\
            .cut((self.world_coords - part.world_coords)+co)

if __name__ == "__main__":
    from cqparts.display import display
    st = Stepper()
    display(st)

