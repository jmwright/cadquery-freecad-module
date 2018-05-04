import os
import re

import cadquery

from . import Exporter, register_exporter
from . import Importer, register_importer
from .. import Part


@register_exporter('step', Part)
class STEPExporter(Exporter):
    """
    Export shape to STEP format.

    =============== ======================
    **Name**        ``step``
    **Exports**     :class:`Part`
    =============== ======================

    .. note::

        Object is passed to :meth:`cadquery.freecad_impl.exporters.exportShape`
        for exporting.

    """

    def __call__(self, filename='out.step', world=False):

        # Getting cadquery Shape
        workplane = self.obj.world_obj if world else self.obj.local_obj
        shape = workplane.val()

        # call cadquery exporter
        with cadquery.freecad_impl.suppress_stdout_stderr():
            with open(filename, 'w') as fh:
                cadquery.freecad_impl.exporters.exportShape(
                    shape=shape,
                    exportType='STEP',
                    fileLike=fh,
                )


@register_importer('step', Part)
class STEPImporter(Importer):
    """
    Import a shape from a STEP formatted file.

    =============== ======================
    **Name**        ``step``
    **Imports**     :class:`Part`
    =============== ======================

    .. note::

        Step file is passed to :meth:`cadquery.freecad_impl.importers.importShape`
        to create the shape.
    """

    def __call__(self, filename):
        if not os.path.exists(filename):
            raise ValueError("given file does not exist: '%s'" % filename)

        # Create a class inheriting from our class
        imported_type = type(self._mangled_filename(filename), (self.cls,), {
            'make': lambda self: cadquery.freecad_impl.importers.importShape(
                importType='STEP',
                fileName=filename,
            ),
        })
        return imported_type()

    @classmethod
    def _mangled_filename(cls, filename):
        return re.sub(r'(^\d|[^a-z0-9_\-+])', '_', filename, flags=re.I)
