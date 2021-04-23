"""module containing the MetricBolt class"""
from collections import namedtuple
from math import pi

from me_toolbox.fasteners import Bolt


class MetricBolt(Bolt):
    """MetricBolt contains the attributes for a metric bolt"""
    grade = namedtuple('Grade', ['low', 'high', 'Sp', 'Sut', 'Sy'])
    grade_list = {'4.6': grade(5, 36, 225, 400, 240),
                  '4.8': grade(1.6, 16, 310, 420, 340),
                  '5.8': grade(5, 24, 380, 520, 420),
                  '8.8': grade(16, 36, 600, 830, 660),
                  '9.8': grade(1.6, 16, 650, 900, 720),
                  '10.9': grade(5, 36, 830, 1040, 940),
                  '12.9': grade(1.6, 36, 970, 1220, 1100)}

    def __repr__(self):
        return f"MetricBolt(M{self.diameter}x{self.pitch} {self.fit} {self.tolerance})"

    def __init__(self, diameter, pitch, fit, tolerance, length, grade, elastic_modulus=210e3):
        """Initializing a UnBolt object

        :param float diameter: Major nominal diameter
        :param float pitch: Thread's pitch
        :param str fit: The fit between the nut and bolt
        :param int tolerance: Bolt's fit tolerance
        :param float length: Bolt's length
        :param str grade: Bolt's grade
        """
        super().__init__(diameter, pitch, length, elastic_modulus)
        self.fit = fit
        self.tolerance = tolerance
        self.grade = grade

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

    @property
    def proof_strength(self):
        """Minimum proof strength"""
        return self.grade_list[self.grade].Sp

    @property
    def tensile_strength(self):
        """Minimum tensile strength"""
        return self.grade_list[self.grade].Sut
