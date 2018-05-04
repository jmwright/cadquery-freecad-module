import cadquery
import random

# FIXME: remove freecad dependency from this module...
#        right now I'm just trying to get it working.
import FreeCAD


class CoordSystem(cadquery.Plane):
    """
    Defines the location, and rotation of an orthogonal 3 dimensional coordinate
    system.
    """

    def __init__(self, origin=(0,0,0), xDir=(1,0,0), normal=(0,0,1)):
        # impose a default to: XY plane, zero offset
        super(CoordSystem, self).__init__(origin, xDir, normal)

    @classmethod
    def from_plane(cls, plane):
        """
        :param plane: cadquery plane instance to base coordinate system on
        :type plane: :class:`cadquery.Plane`
        :return: duplicate of the given plane, in this class
        :rtype: :class:`CoordSystem`

        usage example:

        .. doctest::

            >>> import cadquery
            >>> from cqparts.utils.geometry import CoordSystem
            >>> obj = cadquery.Workplane('XY').circle(1).extrude(5)
            >>> plane = obj.faces(">Z").workplane().plane
            >>> isinstance(plane, cadquery.Plane)
            True
            >>> coord_sys = CoordSystem.from_plane(plane)
            >>> isinstance(coord_sys, CoordSystem)
            True
            >>> coord_sys.origin.z
            5.0
        """
        return cls(
            origin=plane.origin.toTuple(),
            xDir=plane.xDir.toTuple(),
            normal=plane.zDir.toTuple(),
        )

    @classmethod
    def from_transform(cls, matrix):
        r"""
        :param matrix: 4x4 3d affine transform matrix
        :type matrix: :class:`FreeCAD.Matrix`
        :return: a unit, zero offset coordinate system transformed by the given matrix
        :rtype: :class:`CoordSystem`

        Individual rotation & translation matricies are:

        .. math::

            R_z & = \begin{bmatrix}
                cos(\alpha) & -sin(\alpha) & 0 & 0 \\
                sin(\alpha) & cos(\alpha) & 0 & 0 \\
                0 & 0 & 1 & 0 \\
                0 & 0 & 0 & 1
            \end{bmatrix} \qquad & R_y & = \begin{bmatrix}
                cos(\beta) & 0 & sin(\beta) & 0 \\
                0 & 1 & 0 & 0 \\
                -sin(\beta) & 0 & cos(\beta) & 0 \\
                0 & 0 & 0 & 1
            \end{bmatrix} \\
            \\
            R_x & = \begin{bmatrix}
                1 & 0 & 0 & 0 \\
                0 & cos(\gamma) & -sin(\gamma) & 0 \\
                0 & sin(\gamma) & cos(\gamma) & 0 \\
                0 & 0 & 0 & 1
            \end{bmatrix} \qquad & T_{\text{xyz}} & = \begin{bmatrix}
                1 & 0 & 0 & \delta x \\
                0 & 1 & 0 & \delta y \\
                0 & 0 & 1 & \delta z \\
                0 & 0 & 0 & 1
            \end{bmatrix}

        The ``transform`` is the combination of these:

        .. math::

            transform = T_{\text{xyz}} \cdot R_z \cdot R_y \cdot R_x = \begin{bmatrix}
                a & b & c & \delta x \\
                d & e & f & \delta y \\
                g & h & i & \delta z \\
                0 & 0 & 0 & 1
            \end{bmatrix}

        Where:

        .. math::

            a & = cos(\alpha) cos(\beta) \\
            b & = cos(\alpha) sin(\beta) sin(\gamma) - sin(\alpha) cos(\gamma) \\
            c & = cos(\alpha) sin(\beta) cos(\gamma) + sin(\alpha) sin(\gamma) \\
            d & = sin(\alpha) cos(\beta) \\
            e & = sin(\alpha) sin(\beta) sin(\gamma) + cos(\alpha) cos(\gamma) \\
            f & = sin(\alpha) sin(\beta) cos(\gamma) - cos(\alpha) sin(\gamma) \\
            g & = -sin(\beta) \\
            h & = cos(\beta) sin(\gamma) \\
            i & = cos(\beta) cos(\gamma)
        """
        # Create reference points at origin
        offset = FreeCAD.Vector(0, 0, 0)
        x_vertex = FreeCAD.Vector(1, 0, 0)  # vertex along +X-axis
        z_vertex = FreeCAD.Vector(0, 0, 1)  # vertex along +Z-axis

        # Transform reference points
        offset = matrix.multiply(offset)
        x_vertex = matrix.multiply(x_vertex)
        z_vertex = matrix.multiply(z_vertex)

        # Get axis vectors (relative to offset vertex)
        x_axis = x_vertex - offset
        z_axis = z_vertex - offset

        # Return new instance
        vect_tuple = lambda v: (v.x, v.y, v.z)
        return cls(
            origin=vect_tuple(offset),
            xDir=vect_tuple(x_axis),
            normal=vect_tuple(z_axis),
        )

    @classmethod
    def random(cls, span=1, seed=None):
        """
        Creates a randomized coordinate system.

        Useful for confirming that an *assembly* does not rely on its
        origin coordinate system to remain intact.

        For example, the :class:`CoordSysIndicator` *assembly* aligns 3 boxes
        along each of the :math:`XYZ` axes.
        Positioning it randomly by setting its ``world_coords`` shows that each
        box is always positioned orthogonally to the other two.

        .. doctest::

            from cqparts_misc.basic.indicators import CoordSysIndicator
            from cqparts.display import display
            from cqparts.utils import CoordSystem

            cs = CoordSysIndicator()
            cs.world_coords = CoordSystem.random()

            display(cs)  # doctest: +SKIP


        :param span: origin of return will be :math:`\pm span` per axis
        :param seed: if supplied, return is psudorandom (repeatable)
        :type seed: hashable object
        :return: randomized coordinate system
        :rtype: :class:`CoordSystem`
        """
        if seed is not None:
            random.seed(seed)

        def rand_vect(min, max):
            return (
                random.uniform(min, max),
                random.uniform(min, max),
                random.uniform(min, max),
            )

        while True:
            try:
                return cls(
                    origin=rand_vect(-span, span),
                    xDir=rand_vect(-1, 1),
                    normal=rand_vect(-1, 1),
                )
            except RuntimeError:  # Base.FreeCADError inherits from RuntimeError
                # Raised if xDir & normal vectors are parallel.
                # (the chance is very low, but it could happen)
                continue

    @property
    def world_to_local_transform(self):
        """
        :return: 3d affine transform matrix to convert world coordinates to local coorinates.
        :rtype: :class:`cadquery.Matrix`

        For matrix structure, see :meth:`from_transform`.
        """
        return self.fG

    @property
    def local_to_world_transform(self):
        """
        :return: 3d affine transform matrix to convert local coordinates to world coorinates.
        :rtype: :class:`cadquery.Matrix`

        For matrix structure, see :meth:`from_transform`.
        """
        return self.rG

    def __add__(self, other):
        """
        For ``A`` + ``B``. Where ``A`` is this coordinate system,
        and ``B`` is ``other``.

        :raises TypeError: if addition for the given type is not supported

        Supported types:

        ``A`` (:class:`CoordSystem`) + ``B`` (:class:`CoordSystem`):

        :return: world coordinates of ``B`` in ``A``'s coordinates
        :rtype: :class:`CoordSystem`

        ``A`` (:class:`CoordSystem`) + ``B`` (:class:`cadquery.Vector`):

        :return: world coordinates of ``B`` represented in ``A``'s coordinate system
        :rtype: :class:`cadquery.Vector`

        ``A`` (:class:`CoordSystem`) + ``B`` (:class:`cadquery.CQ`):

        remember: :class:`cadquery.Workplane` inherits from :class:`cadquery.CQ`

        :return: content of ``B`` moved to ``A``'s coordinate system
        :rtype: :class:`cadquery.Workplane`
        """
        if isinstance(other, CoordSystem):
            # CoordSystem + CoordSystem
            self_transform = self.local_to_world_transform
            other_transform = other.local_to_world_transform
            return self.from_transform(
                self_transform.multiply(other_transform)
            )

        elif isinstance(other, cadquery.Vector):
            # CoordSystem + cadquery.Vector
            transform = self.local_to_world_transform
            return type(other)(
                transform.multiply(other.wrapped)
            )

        elif isinstance(other, cadquery.CQ):
            # CoordSystem + cadquery.CQ
            transform = self.local_to_world_transform
            return other.newObject([
                obj.transformShape(transform)
                for obj in other.objects
            ])

        else:
            raise TypeError("adding a {other_cls!r} to a {self_cls!r} is not supported".format(
                self_cls=type(self), other_cls=type(other),
            ))

    def __sub__(self, other):
        """
        For ``A`` - ``B``. Where ``A`` is this coordinate system,
        and ``B`` is ``other``.

        :raises TypeError: if subtraction for the given type is not supported

        Supported types:

        ``A`` (:class:`CoordSystem`) + ``B`` (:class:`CoordSystem`):

        :return: local coordinate system of ``A`` from ``B``'s coordinate system
        :rtype: :class:`CoordSystem`
        """
        if isinstance(other, CoordSystem):
            # CoordSystem - CoordSystem
            self_transform = self.local_to_world_transform
            other_transform = other.world_to_local_transform
            return self.from_transform(
                other_transform.multiply(self_transform)
            )

        else:
            raise TypeError("subtracting a {other_cls!r} from a {self_cls!r} is not supported".format(
                self_cls=type(self), other_cls=type(other),
            ))

    def __repr__(self):
        return "<{cls_name}: origin={origin} xDir={xDir} zDir={zDir}>".format(
            cls_name=type(self).__name__,
            origin="(%s)" % (', '.join("%g" % (round(v, 3)) for v in self.origin.toTuple())),
            xDir="(%s)" % (', '.join("%g" % (round(v, 3)) for v in self.xDir.toTuple())),
            zDir="(%s)" % (', '.join("%g" % (round(v, 3)) for v in self.zDir.toTuple())),
        )
