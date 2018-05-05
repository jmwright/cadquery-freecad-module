
from cqparts.params import *

from .female import FemaleFastenerPart


class SquareNut(FemaleFastenerPart):
    edges = PositiveInt(4, doc="number of sides")


class HexNut(FemaleFastenerPart):
    edges = PositiveInt(6, doc="number of sides")


class HexFlangeNut(FemaleFastenerPart):
    edges = PositiveInt(6, doc="number of sides")
    chamfer_base = Boolean(False, doc="if chamfer is set, base edges are chamfered")
    washer = Boolean(True, doc="if True, washer created at base")
