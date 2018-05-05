import cadquery
from copy import copy

import logging

from cqparts.utils import CoordSystem
from cqparts.utils.misc import property_buffered
from . import _casting

log = logging.getLogger(__name__)


# --------------------- Effect ----------------------
class Effect(object):
    pass


class VectorEffect(Effect):
    """
    An evaluator effect is the conclusion to an evaluation with regard to
    a single solid.

    Effects are sortable (based on proximity to evaluation origin)
    """
    def __init__(self, location, part, result):
        """
        :param location: where the fastener is to be applied (eg: for a screw
                         application will be along the -Z axis)
        :type location: :class:`CoordSystem`
        :param part: effected solid
        :type  part: cadquery.Workplane
        :param result: result of evaluation
        :type  result: cadquery.Workplane
        """
        self.location = location
        self.part = part
        self.result = result

    @property
    def start_point(self):
        """
        Start vertex of effect

        :return: vertex (as vector)
        :rtype: :class:`cadquery.Vector`
        """
        edge = self.result.wire().val().Edges()[0]
        return edge.Vertices()[0].Center()

    @property
    def start_coordsys(self):
        """
        Coordinate system at start of effect.

        All axes are parallel to the original vector evaluation location, with
        the origin moved to this effect's start point.

        :return: coordinate system at start of effect
        :rtype: :class:`CoordSys`
        """
        coordsys = copy(self.location)
        coordsys.origin = self.start_point
        return coordsys

    @property
    def end_point(self):
        """
        End vertex of effect

        :return: vertex (as vector)
        :rtype: :class:`cadquery.Vector`
        """
        edge = self.result.wire().val().Edges()[-1]
        return edge.Vertices()[-1].Center()

    @property
    def end_coordsys(self):
        """
        Coordinate system at end of effect.

        All axes are parallel to the original vector evaluation location, with
        the origin moved to this effect's end point.

        :return: coordinate system at end of effect
        :rtype: :class:`CoordSys`
        """
        coordsys = copy(self.location)
        coordsys.origin = self.end_point
        return coordsys

    @property
    def origin_displacement(self):
        """
        planar distance of start point from self.location along :math:`-Z` axis
        """
        return self.start_point.sub(self.location.origin).dot(-self.location.zDir)

    @property
    def wire(self):
        edge = cadquery.Edge.makeLine(self.start_point, self.end_point)
        return cadquery.Wire.assembleEdges([edge])

    @property
    def _wire_wp(self):
        """Put self.wire in it's own workplane for display purposes"""
        return cadquery.Workplane('XY').newObject([self.wire])

    # bool
    def __bool__(self):
        if self.result.edges().objects:
            return True
        return False

    __nonzero__ = __bool__

    # Comparisions
    def __lt__(self, other):
        return self.origin_displacement < other.origin_displacement

    def __le__(self, other):
        return self.origin_displacement <= other.origin_displacement

    def __gt__(self, other):
        return self.origin_displacement > other.origin_displacement

    def __ge__(self, other):
        return self.origin_displacement >= other.origin_displacement


# --------------------- Evaluator ----------------------
class Evaluator(object):
    """
    An evaluator determines which parts may be effected by a fastener, and how.
    """

    # Constructor
    def __init__(self, parts, parent=None):
        """
        :param parts: parts involved in fastening
        :type parts: list of :class:`cqparts.Part`
        :param parent: parent object
        :type parent: :class:`Fastener <cqparts_fasteners.fasteners.base.Fastener>`
        """
        # All evaluators will take a list of parts
        self.parts = parts
        self.parent = parent

    def perform_evaluation(self):
        """
        Evaluate the given parts using any additional parameters passed
        to this instance.

        .. note::

            Override this funciton in your *evaluator* class to assess what
            parts are effected, and how.

        Default behaviour: do nothing, return nothing

        :return: ``None``
        """
        return None

    @property_buffered
    def eval(self):
        """
        Return the result of :meth:`perform_evaluation`, and buffer it so it's
        only run once per :class:`Evaluator` instance.

        :return: result from :meth:`perform_evaluation`
        """
        return self.perform_evaluation()


class VectorEvaluator(Evaluator):

    effect_class = VectorEffect

    def __init__(self, parts, location, parent=None):
        """
        :param parts: parts involved in fastening
        :type parts: list of :class:`cqparts.Part`
        :param location: where the fastener is to be applied (eg: for a screw
                         application will be along the -Z axis)
        :type location: :class:`CoordSystem`
        :param parent: parent object
        :type parent: :class:`Fastener <cqparts_fasteners.fasteners.base.Fastener>`

        **Location**

        The orientation of ``location`` may not be important; it may be for a
        basic application of a screw, in which case the :math:`-Z` axis will be
        used to perform the evaluation, and the :math:`X` and :math`Y` axes are
        of no consequence.

        For *some* fasteners, the orientation of ``location`` will be
        important.
        """
        super(VectorEvaluator, self).__init__(
            parts=parts,
            parent=parent,
        )
        self.location = location

    @property_buffered
    def max_effect_length(self):
        """
        :return: The longest possible effect vector length.
        :rtype: float

        In other words, the *radius* of a sphere:

            - who's center is at ``start``.
            - all ``parts`` are contained within the sphere.
        """
        # Method: using each solid's bounding box:
        #   - get vector from start to bounding box center
        #   - get vector from bounding box center to any corner
        #   - add the length of both vectors
        #   - return the maximum of these from all solids
        def max_length_iter():
            for part in self.parts:
                if part.local_obj.findSolid():
                    bb = part.local_obj.findSolid().BoundingBox()
                    yield abs(bb.center - self.location.origin) + (bb.DiagonalLength / 2)
        try:
            return max(max_length_iter())
        except ValueError as e:
            # if iter returns before yielding anything
            return 0

    def perform_evaluation(self):
        """
        Determine which parts lie along the given vector, and what length

        :return: effects on the given parts (in order of the distance from
                 the start point)
        :rtype: list(:class:`VectorEffect`)
        """
        # Create effect vector (with max length)
        if not self.max_effect_length:
            # no effect is possible, return an empty list
            return []
        edge = cadquery.Edge.makeLine(
            self.location.origin,
            self.location.origin + (self.location.zDir * -(self.max_effect_length + 1))  # +1 to avoid rounding errors
        )
        wire = cadquery.Wire.assembleEdges([edge])
        wp = cadquery.Workplane('XY').newObject([wire])

        effect_list = []  # list of self.effect_class instances
        for part in self.parts:
            solid = part.world_obj.translate((0, 0, 0))
            intersection = solid.intersect(copy(wp))
            effect = self.effect_class(
                location=self.location,
                part=part,
                result=intersection,
            )
            if effect:
                effect_list.append(effect)

        return sorted(effect_list)


class CylinderEvaluator(Evaluator):

    effect_class = VectorEffect
