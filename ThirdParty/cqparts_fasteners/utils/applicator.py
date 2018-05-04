from .evaluator import VectorEvaluator, CylinderEvaluator

class Applicator(object):
    """
    The *applicator* performs 2 roles to *apply* a fastener to workpieces

    #. Translate & rotate given *fastener*
    #. Change workpieces to suit a given *fastener*

    Translation is done first because the fastener is sometimes used as a
    cutting tool to subtract from mating part(s) (eg: thread tapping).
    """

    def __init__(self, evaluator, selector, parent=None):
        """
        :param evaluator: evaluator for fastener
        :type evaluator: :class:`Evaluator <cqparts_fasteners.utils.Evaluator>`
        :param selector: selector for fastener
        :type selector: :class:`Selector <cqparts_fasteners.utils.Selector>`
        :param parent: parent object
        :type parent: :class:`Fastener <cqparts_fasteners.fasteners.base.Fastener>`
        """
        self.evaluator = evaluator
        self.selector = selector
        self.parent = parent

    def apply_alterations(self):
        """
        Apply alterations to relevant parts based on the selected parts
        """
        pass
