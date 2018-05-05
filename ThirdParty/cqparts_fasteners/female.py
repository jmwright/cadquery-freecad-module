
from .params import *
from .solidtypes.fastener_heads.driven import DrivenFastenerHead

from cqparts.params import *


class FemaleFastenerPart(DrivenFastenerHead):
    """
    Female fastener part; with an internal thread.

    A female fastener part can only be externally driven, which is why this
    object inherits from :class:`DrivenFastenerHead`.

    .. doctest::

        from cqparts_fasteners.female import FemaleFastenerPart
        from cqparts.display import display
        nut = FemaleFastenerPart()
        display(nut)  # doctest: +SKIP

    .. image:: /_static/img/fastenerpart/female.default.png

    You can also simplify the internal thread for rendering purposes with::

        nut.thread._simple = True

    .. image:: /_static/img/fastenerpart/female.default.simple.png

    Instances of this class can also be customized during instantiation.

    For example::

        nut = FemaleFastenerPart(
            width=8.1,  # distance between parallel edges
            edges=6,  # hex bolt
            washer=True,  # washer as part of the bolt
            washer_diameter=11,
            washer_height=0.5,
            chamfer_base=False,  # don't chamfer under the washer
            thread=('triangular', {
                'diameter': 6,
                'diameter_core': 4.5,
                'pitch': 1.3,
                'angle': 20,
            }),
        )
        display(nut)

    .. image:: /_static/img/fastenerpart/female.hex_flange.png

    """

    width = PositiveFloat(8, doc="width of tool reqiured to fasten nut")
    height = PositiveFloat(3, doc="height of nut")
    chamfer_top = Boolean(True, doc="if chamfer is set, top edges are chamfered")
    chamfer_base = Boolean(True, doc="if chamfer is set, base edges are chamfered")

    thread = ThreadType(
        default=('iso68', {  # M5
            'diameter': 5,
            'pitch': 0.5,
        }),
        doc="thread type and parameters",
    )

    def initialize_parameters(self):
        super(FemaleFastenerPart, self).initialize_parameters()

        # force thread parameters
        self.thread.inner = True
        self.thread.length = self.height + 0.001
        if self._simple:  # if nut is simplified, thread must also be simplified
            self.thread._simple = True

    def make(self):
        # mirror inherited object
        nut = super(FemaleFastenerPart, self).make() \
            .rotate((0, 0, 0), (1, 0, 0), 180)
        # +z direction is maintained for male & female parts, but the object
        # resides on the opposite side of the XY plane

        # Cut thread
        thread = self.thread.local_obj.translate((0, 0, -self.height))
        nut = nut.cut(thread)
        return nut

    def make_simple(self):
        return super(FemaleFastenerPart, self).make_simple() \
            .rotate((0, 0, 0), (1, 0, 0), 180)

    def make_cutter(self):
        return super(FemaleFastenerPart, self).make_cutter() \
            .rotate((0, 0, 0), (1, 0, 0), 180)
