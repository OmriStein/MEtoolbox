from unittest import TestCase
from math import pi, sqrt

from me_toolbox.fasteners import Bolt


class TestBolt(TestCase):

    def setUp(self):
        diameter = 10
        pitch = 1.5
        length = 20
        threaded_length = 15
        grade = '12.9'
        E = 207e3

        Sp, Sut, Sy = Bolt.get_strength_prop(diameter, grade)
        self.bolt = Bolt(diameter, pitch, length, threaded_length, Sy, Sut, Sp, E)

    def test_height(self):
        self.assertAlmostEqual(self.bolt.height, self.bolt.pitch * sqrt(3) / 2)

    def test_mean_diam(self):
        self.assertAlmostEqual(self.bolt.mean_diameter,
                               self.bolt.diameter - (5 / 8) * self.bolt.height)

    def test_root_diam(self):
        self.assertAlmostEqual(self.bolt.minor_diameter,
                               self.bolt.diameter - (5 / 4) * self.bolt.height)

    def test_pitch_diam(self):
        self.assertAlmostEqual(self.bolt.pitch_diameter,
                               self.bolt.diameter - (3 / 8) * self.bolt.height)

    def test_head_diam(self):
        self.assertAlmostEqual(self.bolt.head_diameter, 1.5 * self.bolt.diameter)

    def test_unthreaded_length(self):
        self.assertAlmostEqual(self.bolt.shank_length,
                               self.bolt.length - self.bolt.thread_length)

    def test_nominal_area(self):
        self.assertAlmostEqual(self.bolt.nominal_area,
                               0.25 * pi * self.bolt.diameter ** 2)

    def test_thread_length(self):
        self.assertAlmostEqual(self.bolt.thread_length, 26)

    def test_stress_area(self):
        self.assertAlmostEqual(self.bolt.stress_area, 57.9895969018452)

    def test_minor_area(self):
        self.assertAlmostEqual(self.bolt.minor_area, 52.29231784971083)
