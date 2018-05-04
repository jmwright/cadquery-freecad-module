from .params import ParametricObject
from .constraint import Mate
from .utils import CoordSystem


class Component(ParametricObject):
    """
    .. note::

        Both the :class:`Part` and :class:`Assembly` classes inherit
        from ``Component``.

        Wherever the term "*component*" is used, it is in reference to an
        instance of either :class:`Part` **or** :class:`Assembly`.
    """

    def __init__(self, *largs, **kwargs):
        super(Component, self).__init__(*largs, **kwargs)

        # Initializing Instance State
        self._world_coords = None

    def build(self, recursive=True):
        """
        :raises NotImplementedError: must be overridden by inheriting classes to function
        """
        raise NotImplementedError("build not implemented for %r" % type(self))

    def _placement_changed(self):
        # called when:
        #   - world_coords is set
        # (intended to be overridden by inheriting classes)
        pass

    @property
    def world_coords(self):
        """
        Component's placement in word coordinates
        (:class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`)

        :return: coordinate system in the world, ``None`` if not set.
        :rtype: :class:`CoordSystem <cqparts.utils.geometry.CoordSystem>`
        """
        return self._world_coords

    @world_coords.setter
    def world_coords(self, value):
        self._world_coords = value
        self._placement_changed()

    @property
    def mate_origin(self):
        """
        :return: mate at object's origin
        :rtype: :class:`Mate`
        """
        return Mate(self, CoordSystem())

    # ----- Export / Import
    def exporter(self, exporter_name=None):
        """
        Get an exporter instance to write the component's content to file.

        :param exporter_name: registered name of exporter to use, see
                              :meth:`register_exporter() <cqparts.codec.register_exporter>`
                              for more information.
        :type exporter_name: :class:`str`

        For example, to get a
        :class:`ThreejsJSONExporter <cqparts.codec.ThreejsJSONExporter>`
        instance to import a ``json`` file:

        .. doctest::

            >>> from cqparts_misc.basic.primatives import Box
            >>> box = Box()
            >>> json_exporter = box.exporter('json')

            >>> # then each exporter will behave differently
            >>> json_exporter('out.json')  # doctest: +SKIP

        To learn more: :ref:`parts_import-export`
        """
        from .codec import get_exporter
        return get_exporter(self, exporter_name)

    @classmethod
    def importer(cls, importer_name=None):
        """
        Get an importer instance to instantiate a component from file.

        :param importer_name: registered name of importer to use, see
                              :meth:`register_importer() <cqparts.codec.register_importer>`
                              for more information.
        :type importer_name: :class:`str`

        For example, to get an importer to instantiate a :class:`Part` from a
        ``STEP`` file:

        .. doctest::

            >>> from cqparts import Part
            >>> step_importer = Part.importer('step')

            >>> # then each importer will behave differently
            >>> my_part = step_importer('my_file.step')  # doctest: +SKIP

        To learn more: :ref:`parts_import-export`
        """
        from .codec import get_importer
        return get_importer(cls, importer_name)
