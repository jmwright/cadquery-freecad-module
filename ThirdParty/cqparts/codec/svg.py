
import re

import cadquery

from . import Exporter, register_exporter
from .. import Part


@register_exporter('svg', Part)
class SVGExporter(Exporter):
    """
    Export shape to AMF format.

    =============== ======================
    **Name**        ``svg``
    **Exports**     :class:`Part`
    =============== ======================

    .. note::

        Object is passed to :meth:`cadquery.freecad_impl.exporters.exportShape`
        for exporting.

    """

    def __call__(self, filename='out.svg', world=False):

        # Getting cadquery Shape
        workplane = self.obj.world_obj if world else self.obj.local_obj
        shape = workplane.val()

        # call cadquery exporter
        with open(filename, 'w') as fh:
            cadquery.freecad_impl.exporters.exportShape(
                shape=shape,
                exportType='SVG',
                fileLike=fh,
            )
