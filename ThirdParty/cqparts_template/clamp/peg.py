
# TODO: illustrative model only; remove this file

import cadquery

import cqparts
from cqparts.params import *
from cqparts.display import render_props
from cqparts import constraint
from cqparts.utils import CoordSystem

from .. import register


class _PegSide(cqparts.Part):
    """
    One side of a wooden clothes peg.

    Note that this docstring does not get rendered in the sphinx automated
    documentation, this is because the class is prefixed with a ``_``.

    Also: idiomatic Python dictates that components with a ``_`` prefix are not
    intended for an end-user, which is why they're not documented.
    """

    length = PositiveFloat()
    width = PositiveFloat()
    depth = PositiveFloat()

    tip_chamfer = PositiveFloat()
    handle_tip_depth = PositiveFloat()
    handle_length = PositiveFloat()

    # spring
    spring_diam = PositiveFloat()
    spring_arm_length = PositiveFloat()
    spring_wire_diam = PositiveFloat()

    # major indent
    major_radius = PositiveFloat()
    major_depth = PositiveFloat()
    major_offset = PositiveFloat()

    # minor indent
    minor_radius = PositiveFloat()
    minor_depth = PositiveFloat()
    minor_offset = PositiveFloat()

    # Default material to render
    _render = render_props(template='wood')

    def make(self):
        # Main profile shape of peg
        points = [
            (0, 0), (self.length, 0),
            (self.length, self.handle_tip_depth),
            (self.length - self.handle_length, self.depth),
            (self.tip_chamfer, self.depth),
            (0, self.depth - self.tip_chamfer),
        ]

        side = cadquery.Workplane('XY') \
            .moveTo(*points[0]).polyline(points[1:]).close() \
            .extrude(self.width)

        # cut spring
        side = side.cut(cadquery.Workplane('XY') \
            .moveTo(self.length - self.handle_length, self.depth) \
            .circle(self.spring_diam / 2).extrude(self.width)
        )

        # cut indents
        def cut_indent(obj, radius, depth, offset):
            return obj.cut(cadquery.Workplane('XY') \
                .moveTo(offset, self.depth + (radius - depth)) \
                .circle(radius).extrude(self.width)
            )
        side = cut_indent(
            obj=side,
            radius=self.major_radius,
            depth=self.major_depth,
            offset=self.major_offset,
        )
        side = cut_indent(
            obj=side,
            radius=self.minor_radius,
            depth=self.minor_depth,
            offset=self.minor_offset,
        )

        return side

    @property
    def mate_spring_center(self):
        # mate in the center of the spring, z-axis along spring center
        return constraint.Mate(self, CoordSystem(
            origin=(self.length - self.handle_length, self.depth, self.width / 2),
        ))

    @property
    def mate_side(self):
        # mate in middle of outside edge, z-axis into peg
        return constraint.Mate(self, CoordSystem(
            origin=(self.length / 2, 0, self.width / 2),
            xDir=(0, 0, -1),
            normal=(0, 1, 0),
        ))


class _Spring(cqparts.Part):
    diam = PositiveFloat()
    arm_length = PositiveFloat()
    wire_diam = PositiveFloat()
    width = PositiveFloat()

    def make(self):
        spring = cadquery.Workplane('XY', origin=(0, 0, -(self.width / 2 + self.wire_diam))) \
            .circle(self.diam / 2).circle((self.diam / 2) - self.wire_diam) \
            .extrude(self.width + (2 * self.wire_diam))

        return spring


@register(module=__name__, name='clothespeg', type='peg_clamp')
class ClothesPeg(cqparts.Assembly):
    """
    A common household clothes-peg

    .. image:: /_static/img/template/peg.png
    """

    length = PositiveFloat(75, doc="length of peg side")
    width = PositiveFloat(10, doc="peg width")
    depth = PositiveFloat(7, doc="depth of peg side, half peg's full depth")

    tip_chamfer = PositiveFloat(5, doc="chamfer at tip")
    handle_tip_depth = PositiveFloat(2, doc="depth at handle's tip")
    handle_length = PositiveFloat(30, doc="length of tapered handle")

    # spring
    spring_diam = PositiveFloat(5, doc="diameter of spring's core")
    spring_arm_length = PositiveFloat(17.5, doc="length of spring's arm converting torque to closing force")
    spring_wire_diam = PositiveFloat(1.3, doc="diamter of spring's wire")

    # major indent
    major_radius = PositiveFloat(10, doc="large indentation's radius")
    major_depth = PositiveFloat(2, doc="large indentation's depth")
    major_offset = PositiveFloat(17, doc="large indentation center's distance from tip")

    # minor indent
    minor_radius = PositiveFloat(1, doc="small indentation's radius")
    minor_depth = PositiveFloat(1, doc="small indentation's depth")
    minor_offset = PositiveFloat(31, doc="small indentation center's distance from tip")

    def make_components(self):
        params = self.params(hidden=False)  # common to _PegSide
        return {
            'bottom': _PegSide(**params),
            'top': _PegSide(**params),
            'spring': _Spring(
                diam=self.spring_diam,
                arm_length=self.spring_arm_length,
                wire_diam=self.spring_wire_diam,
                width=self.width,
            ),
        }

    def make_constraints(self):
        bottom = self.components['bottom']
        top = self.components['top']
        spring = self.components['spring']
        return [
            constraint.Fixed(bottom.mate_side),
            constraint.Coincident(
                top.mate_spring_center,
                bottom.mate_spring_center + CoordSystem(normal=(0, 0, -1))
            ),
            constraint.Coincident(
                spring.mate_origin,
                bottom.mate_spring_center
            ),
        ]
