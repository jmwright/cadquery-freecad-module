import cadquery
from math import radians, tan

from cqparts.params import *

from .base import Thread, register


@register(name='triangular')
class TriangularThread(Thread):
    """
    .. image:: /_static/img/threads/triangular.png
    """
    diameter_core = Float(None, doc="diamter of core")
    angle = PositiveFloat(30, doc="pressure angle of thread")

    def initialize_parameters(self):
        super(TriangularThread, self).initialize_parameters()
        if self.diameter_core is None:
            self.diameter_core = self.diameter * (2. / 3)

    def build_profile(self):
        """
        .. image:: /_static/img/threads/triangular.profile.png
        """
        # Determine thread's length along z-axis
        thread_height = tan(radians(self.angle)) * (self.diameter - self.diameter_core)
        if thread_height > self.pitch:
            raise ValueError("thread's core diameter of %g cannot be achieved with an outer diameter of %g and an angle of %g" % (
                self.diameter_core, self.diameter, self.angle
            ))

        points = [
            (self.diameter_core / 2, 0),
            (self.diameter / 2, thread_height / 2),
            (self.diameter_core / 2, thread_height),
        ]
        if thread_height < self.pitch:
            points.append((self.diameter_core / 2, self.pitch))

        profile = cadquery.Workplane("XZ") \
            .moveTo(*points[0]).polyline(points[1:]) \
            .wire()
        return profile

    def get_radii(self):
        # irrespective of self.inner flag
        return (
            self.diameter_core / 2,  # inner
            self.diameter / 2  # outer
        )
