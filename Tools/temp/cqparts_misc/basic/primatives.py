import cadquery

import cqparts
from cqparts.params import *
from cqparts.search import register, common_criteria
from cqparts.constraint import Mate
from cqparts.utils import CoordSystem


# basic.primatives registration utility
module_criteria = {
    'lib': 'basic',
    'type': 'primative',
    'module': __name__,
}
_register = common_criteria(**module_criteria)(register)


# ------------- Primative Shapes ------------
@_register(shape='cube')
class Cube(cqparts.Part):
    """
    Cube centered on the XY plane
    """
    size = PositiveFloat(1, doc="length of all sides")

    def make(self):
        return cadquery.Workplane('XY').box(
            self.size, self.size, self.size,
        )

    @property
    def mate_top(self):
        """
        :return: mate at top of cube, z-axis upward
        :rtype: :class:`Mate <cqparts.constraint.Mate>`
        """
        return Mate(self, CoordSystem((0, 0, self.size / 2)))

    @property
    def mate_bottom(self):
        """
        :return: mate at base of cube, z-axis upward
        :rtype: :class:`Mate <cqparts.constraint.Mate>`
        """
        return Mate(self, CoordSystem((0, 0, -self.size / 2)))

    @property
    def mate_pos_x(self):
        """
        :return: mate on positive X face
        :rtype: :class:`Mate <cqparts.constraint.Mate>`
        """
        return Mate(self, CoordSystem(
            origin=(self.size/2,0,0), xDir=(0,0,1), normal=(1,0,0)
        ))

    @property
    def mate_neg_x(self):
        """
        :return: mate on negative X face
        :rtype: :class:`Mate <cqparts.constraint.Mate>`
        """
        return Mate(self, CoordSystem(
            origin=(-self.size/2,0,0), xDir=(0,0,1), normal=(-1,0,0)
        ))

    @property
    def mate_pos_y(self):
        """
        :return: mate on positive Y face
        :rtype: :class:`Mate <cqparts.constraint.Mate>`
        """
        return Mate(self, CoordSystem(
            origin=(0,self.size/2,self.size/2), xDir=(0,0,1), normal=(0,1,0)
        ))

    @property
    def mate_neg_y(self):
        """
        :return: mate on negative Y face
        :rtype: :class:`Mate <cqparts.constraint.Mate>`
        """
        return Mate(self, CoordSystem(
            origin=(0,-self.size/2,self.size/2), xDir=(0,0,1), normal=(0,-1,0)
        ))


@_register(shape='box')
class Box(cqparts.Part):
    """
    Box with its base on XY plane.
    """
    length = PositiveFloat(1, doc="box dimension along x-axis")
    width = PositiveFloat(1, doc="box dimension along y-axis")
    height = PositiveFloat(1, doc="box dimension along z-axis")

    def make(self):
        return cadquery.Workplane('XY').box(
            self.length, self.width, self.height,
            centered=(True, True, False)
        )

    @property
    def mate_top(self):
        """
        :return: mate at top of box
        :rtype: :class:`Mate <cqparts.constraint.Mate>`
        """
        return Mate(self, CoordSystem((0, 0, self.height)))

    @property
    def mate_bottom(self):
        """
        :return: mate at base of box
        :rtype: :class:`Mate <cqparts.constraint.Mate>`
        """
        return Mate(self, CoordSystem((0, 0, 0)))

    @property
    def mate_pos_x(self):
        """
        :return: mate on positive X face
        :rtype: :class:`Mate <cqparts.constraint.Mate>`
        """
        return Mate(self, CoordSystem(
            origin=(self.length/2,0,self.height/2), xDir=(0,0,1), normal=(1,0,0)
        ))

    @property
    def mate_neg_x(self):
        """
        :return: mate on negative X face
        :rtype: :class:`Mate <cqparts.constraint.Mate>`
        """
        return Mate(self, CoordSystem(
            origin=(-self.length/2,0,self.height/2), xDir=(0,0,1), normal=(-1,0,0)
        ))

    @property
    def mate_pos_y(self):
        """
        :return: mate on positive Y face
        :rtype: :class:`Mate <cqparts.constraint.Mate>`
        """
        return Mate(self, CoordSystem(
            origin=(0,self.width/2,self.height/2), xDir=(0,0,1), normal=(0,1,0)
        ))

    @property
    def mate_neg_y(self):
        """
        :return: mate on negative Y face
        :rtype: :class:`Mate <cqparts.constraint.Mate>`
        """
        return Mate(self, CoordSystem(
            origin=(0,-self.width/2,self.height/2), xDir=(0,0,1), normal=(0,-1,0)
        ))


@_register(shape='sphere')
class Sphere(cqparts.Part):
    """
    Sphere sitting on the XY plane
    """
    radius = PositiveFloat(1, doc="sphere radius")
    def make(self):
        return cadquery.Workplane('XY', origin=(0, 0, self.radius)) \
            .sphere(self.radius)


@_register(shape='cylinder')
class Cylinder(cqparts.Part):
    """
    Cylinder with its base on the XY plane
    """
    radius = PositiveFloat(1, doc="cylinder radius")
    length = PositiveFloat(1, doc="cylinder length")

    def make(self):
        return cadquery.Workplane('XY') \
            .circle(self.radius).extrude(self.length)

    @property
    def mate_bottom(self):
        return self.mate_origin

    @property
    def mate_top(self):
        return Mate(self, CoordSystem(origin=(0, 0, self.length)))
