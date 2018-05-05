import os
import struct
import base64
from io import BytesIO
from itertools import chain
from copy import copy, deepcopy
import json
from collections import defaultdict
import numpy

from cadquery import Vector

from . import Exporter, register_exporter
from .. import __version__
from .. import Component, Part, Assembly
from ..utils import CoordSystem, measure_time

import logging
log = logging.getLogger(__name__)


class WebGL:
    """
    Enumeration container (nothing special).

    .. doctest::

        >>> from cqparts.codec.gltf import WebGL
        >>> WebGL.ARRAY_BUFFER
        34962

    This class purely exists to make the code more readable.

    All enumerations transcribed from
    `the spec' <https://github.com/KhronosGroup/glTF/tree/master/specification/2.0>`_
    where needed.
    """

    # accessor.componentType
    BYTE = 5120
    UNSIGNED_BYTE = 5121
    SHORT = 5122
    UNSIGNED_SHORT = 5123
    UNSIGNED_INT = 5125
    FLOAT = 5126

    # bufferView.target
    ARRAY_BUFFER = 34962
    ELEMENT_ARRAY_BUFFER = 34963

    # mesh.primative.mode
    POINTS = 0
    LINES = 1
    LINE_LOOP = 2
    LINE_STRIP = 3
    TRIANGLES = 4
    TRIANGLE_STRIP = 5
    TRIANGLE_FAN = 6


def _list3_min(l_a, l_b):
    return [min((a, b)) for (a, b) in zip(l_a if l_a else l_b, l_b)]


def _list3_max(l_a, l_b):
    return [max((a, b)) for (a, b) in zip(l_a if l_a else l_b, l_b)]


class ShapeBuffer(object):
    """
    Write byte buffer for a set of polygons

    To create a buffer for a single polygon:

    .. doctest::

        >>> from cqparts.codec.gltf import ShapeBuffer
        >>> sb = ShapeBuffer()

        >>> # Populate data
        >>> sb.add_vertex(0, 0, 0)  # [0]
        >>> sb.add_vertex(1, 0, 0)  # [1]
        >>> sb.add_vertex(0, 1, 0)  # [2]
        >>> sb.add_poly_index(0, 1, 2)

        >>> # write to file
        >>> with open('single-poly.bin', 'wb') as fh:  # doctest: +SKIP
        ...     for chunk in sb.buffer_iter():  # doctest: +SKIP
        ...         fh.write(chunk)  # doctest: +SKIP

        >>> # get sizes (relevant for bufferViews, and accessors)
        >>> (sb.vert_len, sb.vert_offset, sb.vert_size)
        (36L, 0, 3L)
        >>> (sb.idx_len, sb.idx_offset, sb.idx_size)
        (3L, 36L, 3L)
    """
    def __init__(self, max_index=0xff):
        """
        :param max_index: maximum index number, if > 65535, 4-byte integers are used
        :type max_index: :class:`long`
        """
        self.vert_data = BytesIO()  # vertex positions
        self.idx_data = BytesIO()  # indices connecting vertices into polygons

        # vertices min/max2
        self.vert_min = None
        self.vert_max = None

        # indices number format
        self.max_index = max_index
        if max_index > 0xffff:
            (self.idx_fmt, self.idx_type, self.idx_bytelen) = ('<I', WebGL.UNSIGNED_INT, 4)
        elif max_index > 0xff:
            (self.idx_fmt, self.idx_type, self.idx_bytelen) = ('<H', WebGL.UNSIGNED_SHORT, 2)
        else:
            (self.idx_fmt, self.idx_type, self.idx_bytelen) = ('B', WebGL.UNSIGNED_BYTE, 1)

    @property
    def vert_len(self):
        """
        Number of bytes in ``vert_data`` buffer.
        """
        return self.vert_data.tell()

    @property
    def vert_offset(self):
        """
        Offset (in bytes) of the ``vert_data`` buffer.
        """
        return 0

    @property
    def vert_size(self):
        r"""
        Size of ``vert_data`` in groups of 3 floats
        (ie: number of :math:`3 \times 4` byte groups)

        See `Accessor Element Size <https://github.com/KhronosGroup/glTF/tree/master/specification/2.0#accessor-element-size>`_
        in the glTF docs for clarification.
        """
        # size of position buffer, in groups of 3 floats
        return self.vert_len / (3 * 4)

    @property
    def idx_len(self):
        """
        Number of bytes in ``idx_data`` buffer.
        """
        return self.idx_data.tell()

    @property
    def idx_offset(self):
        """
        Offset (in bytes) of the ``idx_data`` buffer.
        """
        # after vert_data
        return self.vert_offset + self.vert_len

    @property
    def idx_size(self):
        """
        Number of ``idx_data`` elements.
        (ie: number of 2 or 4 byte groups)

        See `Accessor Element Size <https://github.com/KhronosGroup/glTF/tree/master/specification/2.0#accessor-element-size>`_
        in the glTF docs for clarification.
        """
        return self.idx_len / self.idx_bytelen

    def __len__(self):
        return self.vert_len + self.idx_len

    def add_vertex(self, x, y, z):
        """
        Add a ``VEC3`` of ``floats`` to the ``vert_data`` buffer
        """
        self.vert_data.write(
            struct.pack('<f', x) +
            struct.pack('<f', y) +
            struct.pack('<f', z)
        )

        # retain min/max values
        self.vert_min = _list3_min(self.vert_min, (x, y, z))
        self.vert_max = _list3_max(self.vert_max, (x, y, z))

    def add_poly_index(self, i, j, k):
        """
        Add 3 ``SCALAR`` of ``uint`` to the ``idx_data`` buffer.
        """
        self.idx_data.write(
            struct.pack(self.idx_fmt, i) +
            struct.pack(self.idx_fmt, j) +
            struct.pack(self.idx_fmt, k)
        )

    def buffer_iter(self, block_size=1024):
        """
        Iterate through chunks of the vertices, and indices buffers seamlessly.

        .. note::

            To see a usage example, look at the :class:`ShapeBuffer` description.
        """
        streams = (
            self.vert_data,
            self.idx_data,
        )

        # Chain streams seamlessly
        for stream in streams:
            stream.seek(0)
            while True:
                chunk = stream.read(block_size)
                if chunk:
                    yield chunk
                else:
                    break

        # When complete, each stream position should be reset;
        #   back to the end of the stream.

    def read(self):
        """
        Read buffer out as a single stream.

        .. warning::

            Avoid using this function!

            **Why?** This is a *convenience* function; it doesn't encourage good
            memory management.

            All memory required for a mesh is duplicated, and returned as a
            single :class:`str`. So at best, using this function will double
            the memory required for a single model.

            **Instead:** Wherever possible, please use :meth:`buffer_iter`.
        """
        buffer = BytesIO()
        for chunk in self.buffer_iter():
            log.debug('buffer.write(%r)', chunk)
            buffer.write(chunk)
        buffer.seek(0)
        return buffer.read()


@register_exporter('gltf', Component)
class GLTFExporter(Exporter):
    u"""
    Export :class:`Part <cqparts.Part>` or
    :class:`Assembly <cqparts.Assembly>` to a *glTF 2.0* format.

    =============== ======================
    **Name**        ``gltf``
    **Exports**     :class:`Part <cqparts.Part>` & :class:`Assembly <cqparts.Assembly>`
    **Spec**        `glTF 2.0 <https://github.com/KhronosGroup/glTF/tree/master/specification/2.0>`_
    =============== ======================

    **Embedding vs .bin Files:** default generates ``.bin`` files

    If ``embed`` is ``True`` when :meth:`calling <__call__>`, then all data is
    stored in the output ``.gltf`` file.
    However this is very inefficient, for larger, more complex models when
    loading on a web-interface.

    When not embedded, all geometry will be stored as binary ``.bin``
    files in the same directory as the root ``.gltf`` file.

    For example, if we use the ``car`` from :ref:`tutorial_assembly`,
    with the hierarchy::

        car
        \u251c\u25cb chassis
        \u251c\u2500 front_axle
        \u2502   \u251c\u25cb axle
        \u2502   \u251c\u25cb left_wheel
        \u2502   \u2514\u25cb right_wheel
        \u2514\u2500 rear_axle
            \u251c\u25cb axle
            \u251c\u25cb left_wheel
            \u2514\u25cb right_wheel

    When exported, a ``.bin`` file will be created for each
    :class:`Part <cqparts.Part>` (denoted by a ``\u25cb``).

    So the following files will be generated::

        car.gltf
        car.chassis.bin
        car.front_axle.axle.bin
        car.front_axle.left_wheel.bin
        car.front_axle.right_wheel.bin
        car.rear_axle.axle.bin
        car.rear_axle.left_wheel.bin
        car.rear_axle.right_wheel.bin

    The ``car.gltf`` will reference each of the ``.bin`` files.

    The ``car.gltf`` and **all** ``.bin`` files should be web-hosted to serve
    the scene correctly.

    .. todo::

        In this example, all *wheels* and *axles* are the same, they should
        only generate a single buffer.

        But how to definitively determine :class:`Part <cqparts.Part>`
        instance equality?


    """

    scale = 0.001  # mm to meters
    TEMPLATE = {
        # Static values
        "asset": {
            "generator": "cqparts_%s" % __version__,
            "version": "2.0"  # glTF version
        },
        "scene": 0,

        # Populated by adding parts
        "scenes": [{"nodes": [0]}],
        "nodes": [
            {
                "children": [],  # will be appended to before writing to file
                # scene rotation to suit glTF coordinate system
                # ref: https://github.com/KhronosGroup/glTF/tree/master/specification/2.0#coordinate-system-and-units
                "matrix": [
                    1.0 * scale, 0.0, 0.0, 0.0,
                    0.0, 0.0,-1.0 * scale, 0.0,
                    0.0, 1.0 * scale, 0.0, 0.0,
                    0.0, 0.0, 0.0, 1.0,
                ],
            },
        ],
        "meshes": [],
        "accessors": [],
        "materials": [],
        "bufferViews": [],
        "buffers": [],
    }

    # error tolerance of vertices to true face value, only relevant for curved surfaces.
    tolerance = 0.01

    def __init__(self, *args, **kwargs):
        super(GLTFExporter, self).__init__(*args, **kwargs)

        # Initialize
        self.gltf_dict = deepcopy(self.TEMPLATE)
        self.scene_min = None
        self.scene_max = None

    def __call__(self, filename='out.gltf', embed=False):
        """
        :param filename: name of ``.gltf`` file to export
        :type filename: :class:`str`
        :param embed: if True, binary content is embedded in json object.
        :type embed: :class:`bool`
        """

        def add(obj, filename, name, origin, parent_node_index=0):
            split = os.path.splitext(filename)

            if isinstance(obj, Assembly):
                # --- Assembly
                obj_world_coords = obj.world_coords
                if obj_world_coords is None:
                    obj_world_coords = CoordSystem()
                relative_coordsys = obj_world_coords - origin

                # Add empty node to serve as a parent
                node_index = len(self.gltf_dict['nodes'])
                node = {}
                node.update(self.coordsys_dict(relative_coordsys))
                if name:
                    node['name'] = name
                self.gltf_dict['nodes'].append(node)

                # Add this node to its parent
                parent_node = self.gltf_dict['nodes'][parent_node_index]
                parent_node['children'] = parent_node.get('children', []) + [node_index]

                for (child_name, child) in obj.components.items():
                    # Full name of child (including '.' separated list of all parents)
                    full_name = "%s.%s" % (name, child_name)

                    # Recursively add children
                    add(
                        child,
                        filename="%s.%s%s" % (split[0], child_name, split[1]),
                        name="%s.%s" % (name, child_name),
                        origin=obj_world_coords,
                        parent_node_index=node_index,
                    )

            else:
                # --- Part
                self.add_part(
                    obj,
                    filename=None if embed else filename,
                    name=name,
                    origin=origin,
                    parent_idx=parent_node_index,
                )

        split = os.path.splitext(filename)
        if self.obj.world_coords is None:
            self.obj.world_coords = CoordSystem()
        if isinstance(self.obj, Assembly):
            self.obj.solve()  # shoult this be obj.build()?
        add(
            obj=self.obj,
            filename="%s.bin" % split[0],
            origin=self.obj.world_coords,
            name=os.path.splitext(os.path.basename(filename))[0],
        )

        # Write self.gltf_dict to file as JSON string
        with open(filename, 'w') as fh:
            fh.write(json.dumps(self.gltf_dict, indent=2, sort_keys=True))

    @classmethod
    def coordsys_dict(cls, coord_sys, matrix=True):
        """
        Return coordinate system as
        `gltf node transform <https://github.com/KhronosGroup/glTF/tree/master/specification/2.0#transformations>`_

        :param coord_sys: Coordinate system to transform
        :type coord_sys: :class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`
        :return: node transform keys & values
        :rtype: :class:`dict`
        """
        node_update = {}
        if matrix:
            m = coord_sys.local_to_world_transform  # FreeCAD.Base.Matrix
            node_update.update({
                # glTF matrix is column major; needs to be tranposed
                'matrix': m.transposed().A,
            })
        else:
            raise NotImplementedError("only matrix export is supported (for now)")
            # The plan is to support something more like:
            #   {
            #       "rotation": [0, 0, 0, 1],
            #       "scale": [1, 1, 1],
            #       "translation": [-17.7082, -11.4156, 2.0922]
            #   }
            # This is preferable since it's more human-readable.
        return node_update

    @classmethod
    def part_mesh(cls, part):
        """
        Convert a part's object to a mesh.

        :param part: part being converted to a mesh
        :type part: :class:`Part <cqparts.Part>`
        :param world: if True, world coordinates are used
        :type world: :class:`bool`
        :return: list of (<vertices>, <indexes>)
        :rtype: :class:`tuple`

        Returned mesh format::

            <return value> = (
                [FreeCAD.Base.Vector(x, y, z), ... ],  # list of vertices
                [(i, j, k), ... ],  # indexes of vertices making a polygon
            )
        """
        with measure_time(log, 'buffers.part_mesh'):
            workplane = part.local_obj  # cadquery.CQ instance
            shape = workplane.val()  # expecting a cadquery.Solid instance
            tess = shape.tessellate(cls.tolerance)
            return tess

    @classmethod
    def part_buffer(cls, part):
        """
        Export part's geometry as a
        `glTF 2.0 <https://github.com/KhronosGroup/glTF/tree/master/specification/2.0>`_
        asset binary stream.

        :param world: if True, use world coordinates, otherwise use local
        :type world: :class:`bool`
        :return: byte sream of exported geometry
        :rtype: :class:`BytesIO`

        To embed binary model data into a 'uri', you can:

        .. doctest::

            >>> import cqparts
            >>> from cqparts_misc.basic.primatives import Cube

            >>> cube = Cube()
            >>> buff = cube.exporter('gltf').part_buffer(cube)

            >>> import base64
            >>> {'uri': "data:{mimetype};base64,{data}".format(
            ...     mimetype="application/octet-stream",
            ...     data=base64.b64encode(buff.read()).decode('ascii'),
            ... )}
            {'uri': 'data:application/octet-stream;base64,AAAAvwAAAD8AAAA/AAAAvwAAAD8AAAC/AAAAvwAAAL8AAAA/AAAAvwAAAL8AAAC/AAAAPwAAAL8AAAA/AAAAPwAAAD8AAAC/AAAAPwAAAD8AAAA/AAAAPwAAAL8AAAC/AAECAQMCBAUGBAcFAwcCAgcEAAUBBgUAAwEHBwEFBAACBgAE'}
        """
        # binary save done here:
        #    https://github.com/KhronosGroup/glTF-Blender-Exporter/blob/master/scripts/addons/io_scene_gltf2/gltf2_export.py#L112

        # Get shape's mesh
        (vertices, indices) = cls.part_mesh(part)

        # Create ShapeBuffer
        buff = ShapeBuffer(
            max_index=numpy.matrix(indices).max(),
        )

        # Push mesh to ShapeBuffer
        for vert in vertices:
            buff.add_vertex(vert.x, vert.y, vert.z)
        for (i, j, k) in indices:
            buff.add_poly_index(i, j, k)

        return buff

    def add_part(self, part, filename=None, name=None, origin=None, parent_idx=0):
        """
        Adds the given ``part`` to ``self.gltf_dict``.

        :param part: part to add to gltf export
        :type part: :class:`Part <cqparts.Part>`
        :param filename: name of binary file to store buffer, if ``None``,
                         binary data is embedded in the *buffer's 'uri'*
        :type filename: :class:`str`
        :param name: name given to exported mesh (optional)
        :type name: :class:`str`
        :param parent_idx: index of parent node (everything is added to a hierarchy)
        :type parent_idx: :class:`int`
        :return: information about additions to the gltf dict
        :rtype: :class:`dict`

        **Return Format:**

        The returned :class:`dict` is an account of what objects were added
        to the gltf dict, and the index they may be referenced::

            <return format> = {
                'buffers':     [(<index>, <object>), ... ],
                'bufferViews': [(<index>, <object>), ... ],
                'accessors':   [(<index>, <object>), ... ],
                'materials':   [(<index>, <object>), ... ],
                'meshes':      [(<index>, <object>), ... ],
                'nodes':       [(<index>, <object>), ... ],
            }

        .. note::

            The format of the returned :class:`dict` **looks similar** to the gltf
            format, but it **is not**.
        """
        info = defaultdict(list)

        log.debug("gltf export: %r", part)

        # ----- Adding to: buffers
        with measure_time(log, 'buffers'):
            buff = self.part_buffer(part)
            self.scene_min = _list3_min(
                self.scene_min,
                (Vector(buff.vert_min) + part.world_coords.origin).toTuple()
            )
            self.scene_max = _list3_max(
                self.scene_max,
                (Vector(buff.vert_max) + part.world_coords.origin).toTuple()
            )

            buffer_index = len(self.gltf_dict['buffers'])
            buffer_dict = {
                "byteLength": len(buff),
            }
            if filename:
                # write file
                with open(filename, 'wb') as fh:
                    for chunk in buff.buffer_iter():
                        fh.write(chunk)
                buffer_dict['uri'] = os.path.basename(filename)
            else:
                # embed buffer data in URI
                buffer_dict['uri'] = "data:{mimetype};base64,{data}".format(
                    mimetype="application/octet-stream",
                    data=base64.b64encode(buff.read()).decode('ascii'),
                )

            self.gltf_dict['buffers'].append(buffer_dict)
            info['buffers'].append((buffer_index, buffer_dict))

        # ----- Adding: bufferViews
        with measure_time(log, 'bufferViews'):
            bufferView_index = len(self.gltf_dict['bufferViews'])

            # vertices view
            view = {
                "buffer": buffer_index,
                "byteOffset": buff.vert_offset,
                "byteLength": buff.vert_len,
                "byteStride": 12,
                "target": WebGL.ARRAY_BUFFER,
            }
            self.gltf_dict['bufferViews'].append(view)
            bufferView_index_vertices = bufferView_index
            info['bufferViews'].append((bufferView_index_vertices, view))

            # indices view
            view = {
                "buffer": buffer_index,
                "byteOffset": buff.idx_offset,
                "byteLength": buff.idx_len,
                "target": WebGL.ELEMENT_ARRAY_BUFFER,
            }
            self.gltf_dict['bufferViews'].append(view)
            bufferView_index_indices = bufferView_index + 1
            info['bufferViews'].append((bufferView_index_indices, view))

        # ----- Adding: accessors
        with measure_time(log, 'accessors'):
            accessor_index = len(self.gltf_dict['accessors'])

            # vertices accessor
            accessor = {
                "bufferView": bufferView_index_vertices,
                "byteOffset": 0,
                "componentType": WebGL.FLOAT,
                "count": buff.vert_size,
                "min": [v - 0.1 for v in buff.vert_min],
                "max": [v + 0.1 for v in buff.vert_max],
                "type": "VEC3",
            }
            self.gltf_dict['accessors'].append(accessor)
            accessor_index_vertices = accessor_index
            info['accessors'].append((accessor_index_vertices, accessor))

            # indices accessor
            accessor = {
                "bufferView": bufferView_index_indices,
                "byteOffset": 0,
                "componentType": buff.idx_type,
                "count": buff.idx_size,
                "type": "SCALAR",
            }
            self.gltf_dict['accessors'].append(accessor)
            accessor_index_indices = accessor_index + 1
            info['accessors'].append((accessor_index_indices, accessor))

        # ----- Adding: materials
        with measure_time(log, 'materials'):
            material_index = len(self.gltf_dict['materials'])
            material = part._render.gltf_material
            self.gltf_dict['materials'].append(material)
            info['materials'].append((material_index, material))

        # ----- Adding: meshes
        with measure_time(log, 'meshes'):
            mesh_index = len(self.gltf_dict['meshes'])
            mesh = {
                "primitives": [
                    {
                        "attributes": {
                            "POSITION": accessor_index_vertices,
                        },
                        "indices": accessor_index_indices,
                        "mode": WebGL.TRIANGLES,
                        "material": material_index,
                    }
                ],
            }
            if name:
                mesh['name'] = name
            self.gltf_dict['meshes'].append(mesh)
            info['meshes'].append((mesh_index, mesh))

        # ----- Adding: nodes
        with measure_time(log, 'nodes'):
            node_index = len(self.gltf_dict['nodes'])
            node = {
                "mesh": mesh_index,
            }
            if name:
                node['name'] = name
            if origin:
                node.update(self.coordsys_dict(part.world_coords - origin))
            self.gltf_dict['nodes'].append(node)
            info['nodes'].append((node_index, node))

        # Appending child index to its parent's children list
        parent_node = self.gltf_dict['nodes'][parent_idx]
        parent_node['children'] = parent_node.get('children', []) + [node_index]

        return info
