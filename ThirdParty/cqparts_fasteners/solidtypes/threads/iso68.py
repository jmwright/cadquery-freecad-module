import cadquery
from math import pi, sin, cos, tan, sqrt

from cqparts.params import *

from .base import Thread, register


@register(name='iso68')
class ISO68Thread(Thread):
    """
    .. image:: /_static/img/threads/iso68.png
    """
    # rounding ratio:
    #   0.0 = no rounding; peaks and valeys are flat
    #   1.0 = fillet is flush with thread's edges
    # rounding is applied to:
    #   - peak for inner threads
    #   - valley for outer threads
    rounding_ratio = FloatRange(0, 1, 0.5)

    def build_profile(self):
        """
        Build a thread profile in specified by ISO 68

        .. image:: /_static/img/threads/iso68.profile.png
        """
        # height of sawtooth profile (along x axis)
        # (to be trunkated to make a trapezoidal thread)
        height = self.pitch * cos(pi/6)  # ISO 68
        r_maj = self.diameter / 2
        r_min = r_maj - ((5./8) * height)

        profile = cadquery.Workplane("XZ").moveTo(r_min, 0)

        # --- rising edge
        profile = profile.lineTo(r_maj, (5./16) * self.pitch)

        # --- peak
        if self.inner and (self.rounding_ratio > 0):
            # undercut radius (to fit flush with thread)
            # (effective radius will be altered by rounding_ratio)
            cut_radius = (self.pitch / 16) / cos(pi/6)
            # circle's center relative to r_maj
            cut_center_under_r_maj = (self.pitch / 16) * tan(pi/6)
            undercut_depth = self.rounding_ratio * (cut_radius - cut_center_under_r_maj)
            profile = profile.threePointArc(
                (r_maj + undercut_depth, (6./16) * self.pitch),
                (r_maj, (7./16) * self.pitch)
            )
        else:
            profile = profile.lineTo(r_maj, (7./16) * self.pitch)

        # --- falling edge
        profile = profile.lineTo(r_min, (12./16) * self.pitch)

        # --- valley
        if self.inner and (self.rounding_ratio > 0):
            profile = profile.lineTo(r_min, self.pitch)
        else:
            # undercut radius (to fit flush with thread)
            # (effective radius will be altered by rounding_ratio)
            cut_radius = (self.pitch / 8) / cos(pi/6)
            # circle's center relative to r_maj
            cut_center_under_r_maj = (self.pitch / 8) * tan(pi/6)
            undercut_depth = self.rounding_ratio * (cut_radius - cut_center_under_r_maj)
            profile = profile.threePointArc(
                (r_min - undercut_depth, (14./16) * self.pitch),
                (r_min, self.pitch)
            )

        return profile.wire()

    def get_radii(self):
        # irrespective of self.inner flag
        height = self.pitch * cos(pi/6)
        return (
            (self.diameter / 2) - ((5./8) * height),  # inner
            self.diameter / 2  # outer
        )
