import six
from math import tan
from math import radians

import cadquery
import cqparts
from cqparts.params import *

from ..utils import Evaluator, Selector, Applicator

import logging
log = logging.getLogger(__name__)


# ----------------- Fastener Base ---------------
class Fastener(cqparts.Assembly):
    # Parameters
    parts = PartsList(doc="List of parts being fastened")

    # Class assignment
    Evaluator = Evaluator
    Selector = Selector
    Applicator = Applicator

    def make_components(self):
        # --- Run evaluation
        self.evaluator = self.Evaluator(
            parts=self.parts,
            location=self.world_coords,
            parent=self,
        )

        # --- Select fastener (based on evaluation)
        self.selector = self.Selector(
            evaluator=self.evaluator,
            parent=self,
        )

        # --- Add components
        return self.selector.components

    def make_constraints(self):
        # --- Place fastener parts
        return self.selector.constraints

    def make_alterations(self):
        # --- Make alterations based on evaluation and selection
        self.applicator = self.Applicator(
            evaluator=self.evaluator,
            selector=self.selector,
            parent=self,
        )
        self.applicator.apply_alterations()
