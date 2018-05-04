
from cqparts.constraint import Mate, Coincident

from .base import Fastener
from ..utils import VectorEvaluator, Selector, Applicator
from ..nuts import HexNut
from ..bolts import HexBolt


class NutAndBoltFastener(Fastener):
    """
    Nut and Bolt fastener assembly.

    Example usage can be found here: :ref:`cqparts_fasteners.built-in.nut-bolt`
    """
    Evaluator = VectorEvaluator

    class Selector(Selector):
        def get_components(self):
            effect_length = abs(self.evaluator.eval[-1].end_point - self.evaluator.eval[0].start_point)

            nut = HexNut()
            bolt = HexBolt(
                length=effect_length + nut.height,
            )

            return {
                'bolt': bolt,
                'nut': nut,
            }

        def get_constraints(self):
            # bind fastener relative to its anchor; the part holding it in.
            first_part = self.evaluator.eval[0].part
            last_part = self.evaluator.eval[-1].part  # last effected part

            return [
                Coincident(
                    self.components['bolt'].mate_origin,
                    Mate(first_part, self.evaluator.eval[0].start_coordsys - first_part.world_coords)
                ),
                Coincident(
                    self.components['nut'].mate_origin,
                    Mate(last_part, self.evaluator.eval[-1].end_coordsys - last_part.world_coords)
                ),
            ]


    class Applicator(Applicator):
        def apply_alterations(self):
            bolt = self.selector.components['bolt']
            nut = self.selector.components['nut']
            bolt_cutter = bolt.make_cutter()  # cutter in local coords
            nut_cutter = nut.make_cutter()

            for effect in self.evaluator.eval:
                # bolt
                bolt_coordsys = bolt.world_coords - effect.part.world_coords
                effect.part.local_obj = effect.part.local_obj.cut(bolt_coordsys + bolt_cutter)

                # nut
                nut_coordsys = nut.world_coords - effect.part.world_coords
                effect.part.local_obj = effect.part.local_obj.cut(nut_coordsys + nut_cutter)
