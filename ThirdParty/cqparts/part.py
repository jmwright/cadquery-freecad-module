import cadquery
import six
from copy import copy

from .params import Boolean
from .display.material import (
    RenderParam,
    TEMPLATE as RENDER_TEMPLATE,
)
from .errors import MakeError, ParameterError, AssemblyFindError
from .constraint import Constraint, Mate

from .utils.geometry import CoordSystem

import logging
log = logging.getLogger(__name__)


from .component import Component

class Part(Component):

    # Parameters common to every Part
    _simple = Boolean(False, doc="if set, simplified geometry is built")
    _render = RenderParam(RENDER_TEMPLATE['default'], doc="render properties")

    def __init__(self, *largs, **kwargs):
        super(Part, self).__init__(*largs, **kwargs)

        # Initializing Instance State
        self._local_obj = None
        self._world_obj = None

    def make(self):
        """
        Create and return solid part

        :return: cadquery.Workplane of the part in question
        :rtype: subclass of :class:`cadquery.CQ`, usually a :class:`cadquery.Workplane`

        .. important::
            This must be overridden in your ``Part``

        The outcome of this function should be accessed via cqparts.Part.object
        """
        raise NotImplementedError("make function not implemented")

    def make_simple(self):
        """
        Create and return *simplified* solid part.

        The simplified representation of a ``Part`` is to lower the export
        quality of an ``Assembly`` or ``Part`` for rendering.

        Overriding this is optional, but highly recommended.

        The default behaviour returns the full complexity object's bounding box.
        But to do this, theh full complexity object must be generated first.

        There are 2 main problems with this:

        #. building the full complexity part is not efficient.
        #. a bounding box may not be a good representation of the part.

        **Bolts**

        A good example of this is a bolt.

        * building a bolt's thread is not a trivial task;
          it can take some time to generate.
        * a box is not a good visual representation of a bolt

        So for the ``Fastener`` parts, all ``make_simple`` methods are overridden
        to provide 2 cylinders, one for the bolt's head, and another for the thread.
        """
        complex_obj = self.make()
        bb = complex_obj.findSolid().BoundingBox()
        simple_obj = cadquery.Workplane('XY', origin=(bb.xmin, bb.ymin, bb.zmin)) \
            .box(bb.xlen, bb.ylen, bb.zlen, centered=(False, False, False))
        return simple_obj

    def build(self, recursive=False):
        """
        Building a part buffers the ``local_obj`` attribute.

        Running ``.build()`` is optional, it's mostly used to test that
        there aren't any critical runtime issues with it's construction.

        :param recursive: (:class:`Part` has no children, parameter ignored)
        """
        self.local_obj  # force object's construction, but don't do anything with it

    # ----- Local Object
    @property
    def local_obj(self):
        """
        Buffered result of :meth:`make` which is (probably) a
        :class:`cadquery.Workplane` instance. If ``_simple`` is ``True``, then
        :meth:`make_simple` is returned instead.

        .. note::
            This is usually the correct way to get your part's object
            for rendering, exporting, or measuring.

            Only call :meth:`cqparts.Part.make` directly if you explicitly intend
            to re-generate the model from scratch, then dispose of it.
        """
        if self._local_obj is None:
            # Simplified or Complex
            if self._simple:
                value = self.make_simple()
            else:
                value = self.make()
            # Verify type
            if not isinstance(value, cadquery.CQ):
                raise MakeError("invalid object type returned by make(): %r" % value)
            # Buffer object
            self._local_obj = value
        return self._local_obj

    @local_obj.setter
    def local_obj(self, value):
        self._local_obj = value
        self._world_obj = None

    # ----- World Object
    @property
    def world_obj(self):
        """
        The :meth:`local_obj <local_obj>` object in the
        :meth:`world_coords <Component.world_coords>` coordinate system.

        .. note::

            This is automatically generated when called, and
            :meth:`world_coords <Component.world_coords>` is not ``Null``.
        """
        if self._world_obj is None:
            local_obj = self.local_obj
            world_coords = self.world_coords
            if (local_obj is not None) and (world_coords is not None):
                # Copy local object, apply transform to move to its new home.
                self._world_obj = world_coords + local_obj
        return self._world_obj

    @world_obj.setter
    def world_obj(self, value):
        # implemented just for this helpful message
        raise ValueError("can't set world_obj directly, set local_obj instead")

    @property
    def bounding_box(self):
        """
        Generate a bounding box based on the full complexity part.

        :return: bounding box of part
        :rtype: cadquery.BoundBox
        """
        return self.local_obj.findSolid().BoundingBox()

    def _placement_changed(self):
        self._world_obj = None
