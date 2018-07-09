"""
cp parts
base shaft collection
# 2018 Simon Kirkby obeygiantrobot@gmail.com
"""

# TODO
# need tip , base and offset mate points
# maybe shaft needs to go into it's own module
#
# there are lots of types of shafts and extras
# need a clean way to build shafts

import cadquery as cq

import cqparts
from cqparts.params import PositiveFloat
from cqparts.display import render_props

# base shaft type
class Shaft(cqparts.Part):
    " base shaft , override ME"
    length = PositiveFloat(24, doc="shaft length")
    diam = PositiveFloat(5, doc="shaft diameter")

    _render = render_props(color=(50, 255, 255))

    def make(self):
        shft = cq.Workplane("XY")\
            .circle(self.diam/2)\
            .extrude(self.length)\
            .faces(">Z")\
            .chamfer(0.4)
        return shft

    def cut_out(self):
        cutout = cq.Workplane("XY")\
            .circle(self.diam/2)\
            .extrude(self.length)
        return cutout 

    # TODO , mate for shafts

    def get_cutout(self, clearance=0):
        " clearance cut out for shaft "
        return cq.Workplane('XY', origin=(0, 0, 0)) \
            .circle((self.diam / 2) + clearance) \
            .extrude(self.length*2)
