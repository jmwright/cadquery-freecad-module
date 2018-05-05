
from .evaluator import Evaluator

class Selector(object):
    """
    Facilitates the selection and placement of a *fastener's* components
    based on an *evaluation*.

    Each *selector* instance has an :class:`Evaluator` for reference,
    and must have both the methods :meth:`get_components` and
    :meth:`get_constraints` overridden.
    """
    def __init__(self, evaluator, parent=None):
        """
        :param evaluator: evaluator of fastener parts
        :type evaluator: :class:`Evaluator`
        :param parent: parent object
        :type parent: :class:`Fastener <cqparts_fasteners.fasteners.base.Fastener>`
        """
        self.evaluator = evaluator
        self.parent = parent

        self._components = None
        self._constraints = None

    # ---- Components
    def get_components(self):
        """
        Return fastener's components

        .. note::

            Must be overridden by inheriting class.

            Read :ref:`cqparts_fasteners.build_cycle` to learn more.

        :return: components for the *fastener*
        :rtype: :class:`dict` of :class:`Component <cqparts.Component>` instances

        """
        return {}

    @property
    def components(self):
        if self._components is None:
            self._components = self.get_components()
        return self._components

    # ---- Constraints
    def get_constraints(self):
        """
        Return fastener's constraints

        .. note::

            Must be overridden by inheriting class.

            Read :ref:`cqparts_fasteners.build_cycle` to learn more.

        :return: list of *constraints*
        :rtype: :class:`list` of :class:`Constraint <cqparts.constraint.Constraint>` instances
        """
        return []

    @property
    def constraints(self):
        if self._constraints is None:
            self._constraints = self.get_constraints()
        return self._constraints
