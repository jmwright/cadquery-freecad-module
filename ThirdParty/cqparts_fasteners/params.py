import six

from cqparts.params import Parameter, ParametricObject

# Types of things... not parts on their own, but utilised in many
from .solidtypes import fastener_heads
from .solidtypes import screw_drives
from .solidtypes import threads


# --------- Custom Parameter types ---------
class FastenerComponentParam(Parameter):
    """
    Custom fastener component as a parameter.
    (not to be confused with a *Part*)
    """
    name = None
    finder_callback = None
    component_base = None

    def type(self, value):
        if isinstance(value, self.component_base):
            # component's instance explicitly provided.
            return value

        elif isinstance(value, (tuple, list)):
            # split value
            if len(value) != 2:
                raise ParameterError("given tuple must have 2 elements ({name}_type, dict(params)): {val!r}".format(
                    name=self.name, val=value
                ))
            (component_type, params) = value

            # Get component's class (or raise an exception trying)
            component_class = None
            if type(component_type) is type:  # given value is a class
                if issubclass(component_type, self.component_base):
                    # component class is explicitly defined
                    component_class = component_type
                else:
                    raise ParameterError(
                        "given {name} type class {cls!r} does not inherit from {base!r}".format(
                            name=self.name, cls=type(component_type), base=self.component_base
                        )
                    )
            elif isinstance(component_type, six.string_types):
                # name of component type given, use callback to find it
                try:
                    component_class = self.finder_callback(name=component_type)
                except ValueError as e:
                    raise ParameterError(
                        ("{name} type of '{type}' cannot be found. ".format(name=self.name, type=component_type)) +
                        "is it spelt correctly (case sensitive)?, has the library defining it been imported?"
                    )
            else:
                raise ParameterError(
                    "{name} type {val!r} must be a str, or a class inheriting from {base!r}".format(
                        name=self.name, val=component_type, base=self.component_base
                    )
                )

            # Verify parameters (very loosely)
            if not isinstance(params, dict):
                raise ParameterError("parameters must be a dict: {!r}".format(params))

            # Create instance & return it
            return component_class(**params)

    # Serialize / Deserialize
    @classmethod
    def serialize(cls, value):
        if value is None:
            return value
        return value.serialize()  # divert to ParametricObject's serialize()

    @classmethod
    def deserialize(cls, value):
        if value is None:
            return value
        return ParametricObject.deserialize(value)


class HeadType(FastenerComponentParam):
    name = 'head'
    finder_callback = staticmethod(fastener_heads.find)
    component_base = fastener_heads.FastenerHead

    _doc_type = "``value`` for :meth:`HeadType.type <cqparts_fasteners.params.HeadType.type>`"

    def type(self, value):
        """
        :param value: defined type of male fastener head
        :type value: see below

        ``value`` can be any of:

        - :class:`FastenerHead <cqparts.solidtypes.fastener_heads.FastenerHead>` instance
        - :class:`tuple` of (``head type``, ``parameters``) where:

          - ``head type`` is one of

            - :class:`str` name of fastener head (registered with :meth:`register <cqparts.solidtypes.fastener_heads.register>`)
            - :class:`FastenerHead <cqparts.solidtypes.fastener_heads.FastenerHead>` subclass

          - ``parameters`` is a :class:`dict`
        """
        return super(HeadType, self).type(value)


class DriveType(FastenerComponentParam):
    name = 'drive'
    finder_callback = staticmethod(screw_drives.find)
    component_base = screw_drives.ScrewDrive

    _doc_type = "``value`` for :meth:`DriveType.type <cqparts_fasteners.params.DriveType.type>`"

    def type(self, value):
        """
        :param value: defined type of screw-drive
        :type value: see below

        ``value`` can be any of:

        - :class:`ScrewDrive <cqparts.solidtypes.screw_drives.ScrewDrive>` instance
        - :class:`tuple` of (``drive type``, ``parameters``) where

          - ``drive type`` is one of

            - ``str``: name of screw-drive (registered with :meth:`register <cqparts.solidtypes.screw_drives.register>`)
            - :class:`ScrewDrive <cqparts.solidtypes.screw_drives.ScrewDrive>` subclass

          - ``parameters`` is a :class:`dict`
        """
        return super(DriveType, self).type(value)


class ThreadType(FastenerComponentParam):
    name = 'thread'
    finder_callback = staticmethod(threads.find)
    component_base = threads.Thread

    _doc_type = "``value`` for :meth:`ThreadType.type <cqparts_fasteners.params.ThreadType.type>`"

    def type(self, value):
        """
        :param value: defined type of thread
        :type value: see below

        ``value`` can be any of:

        - :class:`Thread <cqparts.solidtypes.threads.Thread>` instance
        - :class:`tuple` of (``thread type``, ``parameters``) where:

          - ``thread type`` is one of

            - ``str``: name of thread type (registered with :meth:`register <cqparts.solidtypes.threads.register>`)
            - :class:`Thread <cqparts.solidtypes.threads.Thread>` subclass

          - ``parameters`` is a :class:`dict`
        """
        return super(ThreadType, self).type(value)
