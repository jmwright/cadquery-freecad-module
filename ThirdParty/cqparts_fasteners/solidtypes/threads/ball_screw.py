import cadquery
from cqparts.params import *

from .base import Thread, register


@register(name='ball_screw')
class BallScrewThread(Thread):
    """
    .. image:: /_static/img/threads/ball_screw.png
    """
    ball_radius = Float(0.25, doc="ball's radius")

    def build_profile(self):
        """
        .. image:: /_static/img/threads/ball_screw.profile.png
        """
        profile = cadquery.Workplane("XZ") \
            .moveTo(self.diameter / 2, self.pitch - self.ball_radius)
        # cylindrical face
        if (2 * self.ball_radius) < self.pitch:
            profile = profile.lineTo(self.diameter / 2, self.ball_radius)
        # rail for balls
        profile = profile.threePointArc(
                ((self.diameter / 2) - self.ball_radius, 0),
                (self.diameter / 2, -self.ball_radius)
            )
        return profile.wire()

    def get_radii(self):
        return (
            (self.diameter / 2) - self.ball_radius,  # inner
            self.diameter / 2,  # outer
        )
