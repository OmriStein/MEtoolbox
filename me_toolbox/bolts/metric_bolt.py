"""module containing the MetricBolt class"""
from math import pi

from me_toolbox.bolts import Bolt


class MetricBolt(Bolt):
    """MetricBolt contains the attributes for a metric bolt"""
    def __repr__(self):
        return f"MetricBolt(M{self.diameter}x{self.pitch} {self.fit} {self.tolerance})"

    def __init__(self, diameter, pitch, fit, tolerance, length):
        """Initializing a UnBolt object

        :param float diameter: Major nominal diameter
        :param float pitch: Thread's pitch
        :param str fit: the fit between the nut and bolt
        :param int tolerance: The fit tolerance
        """
        super().__init__(diameter, pitch, length)
        self.fit = fit
        self.tolerance = tolerance

    @property
    def thread_length(self):
        """length of the threaded (L_T) section in [mm]"""
        if self.length <= 125 and self.diameter <= 48:
            return 2 * self.diameter + 6
        elif 125 < self.length <= 200:
            return 2 * self.diameter + 12
        elif self.length > 200:
            return 2 * self.diameter + 25

    @property
    def stress_area(self):
        """Tensile stress area (At)
        as calculated in Table 8-1 of Shigley"""
        dr = self.diameter - 1.226869 * self.pitch
        dp = self.diameter - 0.649519 * self.pitch
        dt = 0.5 * (dr + dp)
        return 0.25 * pi * dt ** 2

    @property
    def minor_area(self):
        """Minor diameter area (Ar)"""
        dr = self.diameter - 1.226869 * self.pitch
        return 0.25 * pi * dr ** 2
