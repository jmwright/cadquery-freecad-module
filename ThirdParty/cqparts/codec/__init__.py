from collections import defaultdict

from .. import Component

# ----------------- Exporting -----------------
class Exporter(object):
    def __init__(self, obj):
        self.obj = obj

    def __call__(self):
        raise NotImplementedError("%r exporter is not callable" % (type(self)))


exporter_index = defaultdict(dict)
# format: {<name>: {<class_base>: <exporter_class>}}

def register_exporter(name, base_class):
    """
    Register an exporter to use for a :class:`Part <cqparts.Part>`,
    :class:`Assembly <cqparts.Assembly>`, or both
    (with :class:`Component <cqparts.Component>`).

    Registration is necessary to use with
    :meth:`Component.exporter() <cqparts.Component.exporter>`.

    :param name: name (or 'key') of exporter
    :type name: :class:`str`
    :param base_class: class of :class:`Component <cqparts.Component>` to export
    :type base_class: :class:`type`

    .. doctest::

        >>> from cqparts import Part
        >>> from cqparts.codec import Exporter, register_exporter

        >>> @register_exporter('my_type', Part)
        ... class MyExporter(Exporter):
        ...     def __call__(self, filename='out.mytype'):
        ...         print("export %r to %s" % (self.obj, filename))

        >>> from cqparts_misc.basic.primatives import Sphere
        >>> thing = Sphere(radius=5)
        >>> thing.exporter('my_type')('some-file.mytype')
        export <Sphere: radius=5.0> to some-file.mytype

    """
    # Verify params
    if not isinstance(name, str) or (not name):
        raise TypeError("invalid name: %r" % name)
    if not issubclass(base_class, Component):
        raise TypeError("invalid base_class: %r, must be a %r subclass" % (base_class, Component))

    def decorator(cls):
        # --- Verify
        # Can only be registered once
        if base_class in exporter_index[name]:
            raise TypeError("'%s' exporter type %r has already been registered" % (
                name, base_class
            ))

        # Verify class hierarchy will not conflict
        # (so you can't have an exporter for a Component, and a Part. must be
        #  an Assembly, and a Part, respectively)
        for key in exporter_index[name].keys():
            if issubclass(key, base_class) or issubclass(base_class, key):
                raise TypeError("'%s' exporter type %r is in conflict with %r" % (
                    name, base_class, key,
                ))

        # --- Index
        exporter_index[name][base_class] = cls

        return cls
    return decorator


def get_exporter(obj, name):
    """
    Get an exporter for the

    :param obj: object to export
    :type obj: :class:`Component <cqparts.Component>`
    :param name: registered name of exporter
    :type name: :class:`str`
    :return: an exporter instance of the given type
    :rtype: :class:`Exporter`
    :raises TypeError: if exporter cannot be found
    """
    if name not in exporter_index:
        raise TypeError(
            ("exporter type '%s' is not registered: " % name) +
            ("registered types: %r" % sorted(exporter_index.keys()))
        )

    for base_class in exporter_index[name]:
        if isinstance(obj, base_class):
            return exporter_index[name][base_class](obj)

    raise TypeError("exporter type '%s' for a %r is not registered" % (
        name, type(obj)
    ))


# ----------------- Importing -----------------
class Importer(object):
    def __init__(self, cls):
        self.cls = cls


importer_index = defaultdict(dict)
# format: {<name>: {<class_base>: <importer_class>}}


def register_importer(name, base_class):

    # Verify params
    if not isinstance(name, str) or (not name):
        raise TypeError("invalid name: %r" % name)
    if not issubclass(base_class, Component):
        raise TypeError("invalid base_class: %r, must be a %r subclass" % (base_class, Component))

    def decorator(cls):
        # --- Verify
        # Can only be registered once
        if base_class in importer_index[name]:
            raise TypeError("'%s' importer type %r has already been registered" % (
                name, base_class
            ))

        # Verify class hierarchy will not conflict
        # (so you can't have an importer for a Component, and a Part. must be
        #  an Assembly, and a Part, respectively)
        for key in importer_index[name].keys():
            if issubclass(key, base_class) or issubclass(base_class, key):
                raise TypeError("'%s' importer type %r is in conflict with %r" % (
                    name, base_class, key,
                ))

        # --- Index
        importer_index[name][base_class] = cls

        return cls
    return decorator


def get_importer(cls, name):
    """
    Get an importer for the given registered type.

    :param cls: class to import
    :type cls: :class:`type`
    :param name: registered name of importer
    :type name: :class:`str`
    :return: an importer instance of the given type
    :rtype: :class:`Importer`
    :raises TypeError: if importer cannot be found
    """
    if name not in importer_index:
        raise TypeError(
            ("importer type '%s' is not registered: " % name) +
            ("registered types: %r" % sorted(importer_index.keys()))
        )

    for base_class in importer_index[name]:
        if issubclass(cls, base_class):
            return importer_index[name][base_class](cls)

    raise TypeError("importer type '%s' for a %r is not registered" % (
        name, cls
    ))


# ----------------- housekeeping -----------------

__all__ = [
    # Tools
    'Exporter', 'register_exporter', 'get_exporter',
    'Importer', 'register_importer', 'get_importer',

    # Codecs
    'AMFExporter',
    'GLTFExporter',
    'STEPExporter', 'STEPImporter',
    'STLExporter',
    'SVGExporter',
    'ThreejsJSONExporter', 'ThreejsJSONAssemblyExporter',

]

from .amf import AMFExporter
from .gltf import GLTFExporter
from .step import STEPExporter, STEPImporter
from .stl import STLExporter
from .svg import SVGExporter
from .threejs_json import ThreejsJSONExporter, ThreejsJSONAssemblyExporter
