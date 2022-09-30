"""module containing the MetricBolt class"""
from collections import namedtuple
from math import pi

from me_toolbox.fasteners import Bolt


class MetricBolt(Bolt):
    """MetricBolt contains the attributes for a metric bolt
        (stresses are in MPa, sizes are in mm)"""
    grade = namedtuple('Grade', ['low', 'high', 'Sp', 'Sut', 'Sy'])
    grade_list = {'4.6': grade(5, 36, 225, 400, 240),
                  '4.8': grade(1.6, 16, 310, 420, 340),
                  '5.8': grade(5, 24, 380, 520, 420),
                  '8.8': grade(16, 36, 600, 830, 660),
                  '9.8': grade(1.6, 16, 650, 900, 720),
                  '10.9': grade(5, 36, 830, 1040, 940),
                  '12.9': grade(1.6, 36, 970, 1220, 1100)}

    def __repr__(self):
        return f"MetricBolt(M{self.diameter}x{self.pitch}x{self.length})"

    def __init__(self, diameter, pitch, length, grade, elastic_modulus=210e3, endurance_limit=None,
                 reliability=50, temp=25, surface_finish='hot-rolled', Sy=None,
                 preload=None, reused=True):
        """Initializing a Bolt object

        :param float diameter: Nominal diameter
        :param float pitch: Thread's pitch
        :param float length: Bolt's length
        :param str grade: Bolt's grade
        :param float elastic_modulus: Bolt's elastic modulus
        :param float Sy: yield strength for non-steel bolt in order to approximate proof strength
        :param float endurance_limit: Bolt's endurance limit
        :param float reliability: Bolt's reliability (for Se calc)
        :param float temp: Working temp (for Se calc)
        :param str surface_finish: 'machined' or 'hot-rolled' (for Se calc)
        :param float preload: Preload of the bolt
        :param bool reused: is the bolt ment to be reused or permanent
        """
        self.yield_strength = self.grade_list[grade].Sy if Sy is None else Sy
        self._is_yield = False if Sy is None else True
        super().__init__(diameter, pitch, length, grade, elastic_modulus, endurance_limit,
                         reliability, temp, surface_finish, preload, reused)

    @property
    def thread_length(self):
        """length of the threaded (L_T) section in [mm]"""
        # TODO add option to enter the thread length manually (may differ by standard)
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
        """Root diameter area (Ar)"""
        dr = self.diameter - 1.226869 * self.pitch
        return 0.25 * pi * dr ** 2

    @property
    def proof_strength(self):
        """The minimum proof strength (Sp)"""
        if not self._is_yield:
            # if steel
            return self.grade_list[self.grade].Sp
        else:
            # other materials
            return 0.85*self.yield_strength

    @property
    def tensile_strength(self):
        """Minimum tensile strength (Sut)"""
        return self.grade_list[self.grade].Sut

    @property
    def yield_strength(self):
        """Yield strength"""
        return self._yield_strength

    @yield_strength.setter
    def yield_strength(self, Sy):
        """Yield strength setter"""
        self._yield_strength = Sy
