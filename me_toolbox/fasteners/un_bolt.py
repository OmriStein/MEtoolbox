"""module containing the UnBolt class"""
from collections import namedtuple
from math import pi

from me_toolbox.fasteners import Bolt


class UnBolt(Bolt):
    """UnBolt contains the attributes for a Unified National(UN) bolt"""
    grade = namedtuple('Grade', ['low', 'high', 'Sp', 'Sut', 'Sy'])
    grade_list = {'1': grade(0.25, 1.5, 33, 60, 36),
                  '2': (grade(0.25, 0.75, 55, 74, 57), grade(7 / 8, 1.5, 33, 60, 36)),
                  '4': grade(0.25, 1.5, 65, 115, 100),
                  '5': (grade(0.25, 1, 85, 120, 92), grade(9 / 8, 1.5, 74, 105, 81)),
                  '5.2': grade(0.25, 1, 85, 120, 92),
                  '7': grade(0.25, 1.5, 105, 133, 115),
                  '8': grade(0.25, 1, 120, 150, 130)}

    def __repr__(self):
        return f"UnBolt({self.diameter}\"-{self.tpi} " \
               f"{'UNF' if self.fine else 'UNC'} {self.fit}" \
               f"{'B' if self.bolt else 'A'})"

    def __init__(self, diameter, tpi, fine, fit, bolt, length, grade, elastic_modulus=30):
        """Initializing a UnBolt object

        :param float diameter: major nominal diameter
        :param float tpi: Tooth per inch
        :param bool fine: True if fine or False if course
        :param int fit: Fit between the nut and bolt (1/2/3)
        :param bool bolt: True if bolt False if nut
        :param float length: Bolt's length
        :param str grade: Bolt's grade
        """
        super().__init__(diameter, 1 / tpi, length, elastic_modulus)
        self.tpi = tpi
        self.fine = fine
        self.fit = fit
        self.bolt = bolt
        self.grade = grade

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

    @property
    def proof_strength(self):
        """Minimum proof strength"""
        d = self.diameter
        if len(self.grade_list[self.grade]) == 2:
            for i in range(2):
                if self.grade_list[self.grade][i].low < d < self.grade_list[self.grade][i].high:
                    return self.grade_list[self.grade][i].Sp
            raise ValueError("The bolt diameter don't match bolt grade")
        else:
            return self.grade_list[self.grade].Sp

    @property
    def tensile_strength(self):
        """Minimum tensile strength"""
        d = self.diameter
        if len(self.grade_list[self.grade]) == 2:
            for i in range(2):
                if self.grade_list[self.grade][i].low < d < self.grade_list[self.grade][i].high:
                    return self.grade_list[self.grade][i].Sp
            raise ValueError("The bolt diameter don't match bolt grade")
        else:
            return self.grade_list[self.grade].Sut
