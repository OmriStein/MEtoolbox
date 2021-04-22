"""module containing the UnBolt class"""
from math import pi

from me_toolbox.fasteners import Bolt


class UnBolt(Bolt):
    """UnBolt contains the attributes for a Unified National(UN) bolt"""

    def __repr__(self):
        return f"UnBolt({self.diameter}\"-{self.tpi} " \
               f"{'UNF' if self.fine else 'UNC'} {self.fit}" \
               f"{'B' if self.bolt else 'A'})"

    def __init__(self, diameter, tpi, fine, fit, bolt, length):
        """Initializing a UnBolt object

        :param float diameter: major nominal diameter
        :param float tpi: Tooth per inch
        :param bool fine: True if fine or False if course
        :param int fit: the fit between the nut and bolt (1/2/3)
        :param bool bolt: True if bolt False if nut
        """
        super().__init__(diameter, 1 / tpi, length)
        self.tpi = tpi
        self.fine = fine
        self.fit = fit
        self.bolt = bolt

    @property
    def thread_length(self):
        """length of the threaded section (L_T) in [in]"""
        return 2 * self.diameter + 0.25 if self.length <= 6 else 2 * self.diameter + 0.5

    @property
    def stress_area(self):
        """Tensile stress area (At)
        as calculated in Table 8-1 of Shigley"""
        dr = self.diameter - 1.299038 * self.pitch
        dp = self.diameter - 0.649519 * self.pitch
        dt = 0.5 * (dr + dp)
        return 0.25 * pi * dt ** 2

    @property
    def minor_area(self):
        """Minor diameter area (Ar)"""
        dr = self.diameter - 1.299038 * self.pitch
        return 0.25 * pi * dr ** 2
