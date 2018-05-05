import os
import json
from io import StringIO

import logging
log = logging.getLogger(__name__)

import cadquery

from . import Exporter, register_exporter
from .. import Component, Part, Assembly


@register_exporter('json', Part)
class ThreejsJSONExporter(Exporter):
    """
    Export the :class:`Part <cqparts.Part>` to a *three.js JSON v3* file format.

    =============== ======================
    **Name**        ``json``
    **Exports**     :class:`Part <cqparts.Part>`
    **Spec**        `three.js JSON model format v3 specification <https://github.com/mrdoob/three.js/wiki/JSON-Model-format-3>`_
    =============== ======================

    For information on how to load in a webpage, look to your WebGL framework
    of choice:

    * ThreeJS: https://threejs.org/docs/#api/loaders/ObjectLoader
    * A-Frame: https://aframe.io/docs/0.7.0/core/asset-management-system.html#lt-a-asset-item-gt

    """

    def __call__(self, filename="out.json", world=False):
        """
        Write to file.

        :param filename: file to write
        :type filename: :class:`str`
        :param world: if True, use world coordinates, otherwise use local
        :type world: :class:`bool`
        """
        log.debug("exporting: %r", self.obj)
        log.debug("       to: %s", filename)
        with open(filename, 'w') as fh:
            fh.write(self.get_str(world=world))

    def get_str(self, *args, **kwargs):
        """
        Get file string.

        (same arguments as :meth:`get_export_gltf_dict`)

        :return: JSON string
        :rtype: :class:`str`
        """
        data = self.get_dict(*args, **kwargs)
        return json.dumps(data)

    def get_dict(self, world=False):
        """
        Get the part's geometry as a :class:`dict`

        :param world: if True, use world coordinates, otherwise use local
        :type world: :class:`bool`
        :return: JSON model format
        :rtype: :class:`dict`
        """
        data = {}
        with StringIO() as stream:
            obj = self.obj.world_obj if world else self.obj.local_obj
            cadquery.exporters.exportShape(obj, 'TJS', stream)
            stream.seek(0)
            data = json.load(stream)

        # Change diffuse colour to that in render properties
        data['materials'][0]['colorDiffuse'] = [
            val / 255. for val in self.obj._render.rgb
        ]
        data['materials'][0]['transparency'] = self.obj._render.alpha

        return data


@register_exporter('json', Assembly)
class ThreejsJSONAssemblyExporter(Exporter):
    """
    Export an :class:`Assembly` into **multiple** ``json`` files.

    =============== ======================
    **Name**        ``json``
    **Exports**     :class:`Assembly`
    **Spec**        `three.js JSON model format v3 specification <https://github.com/mrdoob/three.js/wiki/JSON-Model-format-3>`_
    =============== ======================

    .. warning::

        The *three.js JSON v3* format does not support multiple models (or, at
        least, not as far as I can tell).

        So this exporter will create multiple files, one per part.

        If you're after a more modern WebGL supported export, consider using
        :class:`GLTFExporter <cqparts.codec.GLTFExporter>` instead.

    """

    def __call__(self, filename='out.json', world=False):
        self._write_file(self.obj, filename, world=world)

    @classmethod
    def _write_file(cls, obj, filename, world=False):
        # recursive method to iterate through children
        if isinstance(obj, Assembly):
            # Object has no geometry, iter through components
            obj.solve()
            for (name, child) in obj.components.items():
                s = os.path.splitext(filename)
                cls._write_file(child, "%s.%s%s" % (s[0], name, s[1]), world=True)
        else:
            ThreejsJSONExporter(obj)(filename, world=world)
