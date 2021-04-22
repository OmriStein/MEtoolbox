"""module containing the bolts base class Bolt"""
from math import sqrt, pi

from me_toolbox.tools import print_atributes


class Bolt:
    """Bolt class containing basic geometry attributes
    that are identical in metric and unified national(NU)"""
    angle = 60

    def __repr__(self):
        return f"Bolt({self.diameter}, {self.pitch}, {self.length})"

    def __len__(self):
        return self.length

    def __init__(self, diameter, pitch, length, elastic_modulus=200e3):
        """Initialise Bolt object

        :param float diameter: nominal diameter
        :param float pitch: Thread's pitch
        """
        self.diameter = diameter
        self.pitch = pitch
        self.length = length
        self.elastic_modulus = elastic_modulus

    def get_info(self):
        """print all of the spring properties"""
        print_atributes(self)

    @property
    def height(self):
        """Height of fundamental triangle (H)"""
        return self.pitch * sqrt(3) / 2

    @property
    def mean_diam(self):
        "Mean diameter(dm) of the nominal and root diameters(dr)"""
        return self.diameter - (5 / 8) * self.height

    @property
    def root_diam(self):
        """Minor diameter (dr)"""
        return self.diameter - (5 / 4) * self.height

    @property
    def pitch_diam(self):
        """Pitch diameter(dp)"""
        return self.diameter - (3 / 8) * self.height

    @property
    def head_diam(self):
        """Contact area diameter of bolt head (D)"""
        return 1.5 * self.diameter

    @property
    def thread_length(self):
        """place holder"""
        return

    @property
    def unthreaded_length(self):
        """the unthreaded section of the bolt (ld)
        Note: the unthreaded length can be zero"""
        return self.length - self.thread_length

    @property
    def nominal_area(self):
        """area of the bolt's nominal diameter (Ad)"""
        return 0.25 * pi * self.diameter ** 2
