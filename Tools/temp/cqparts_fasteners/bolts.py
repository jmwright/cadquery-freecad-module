
from cqparts.params import *

from .male import MaleFastenerPart
from .params import *


class Bolt(MaleFastenerPart):
    length = PositiveFloat(20, doc="length from xy plane to tip")

    head = HeadType(
        default=('hex', {
            'width': 8,
            'height': 3.0,
        }),
        doc="head type and parameters",
    )
    drive = DriveType(doc="screw drive type and parameters")
    thread = ThreadType(
        default=('iso68', {  # M5
            'diameter': 5.0,
            'pitch': 0.5,
        }),
        doc="thread type and parameters",
    )


class SquareBolt(Bolt):
    head = HeadType(
        default=('square', {
            'width': 8,
            'height': 3.0,
        }),
        doc="head type and parameters",
    )


class HexBolt(Bolt):
    head = HeadType(
        default=('hex', {
            'width': 8,
            'height': 3.0,
        }),
        doc="head type and parameters",
    )
