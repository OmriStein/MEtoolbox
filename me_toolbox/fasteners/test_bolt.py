from unittest import TestCase
from math import pi, sqrt

from me_toolbox.fasteners import MetricBolt, UNBolt


class TestThreadedFastener(TestCase):

    def setUp(self):
        self.metric_bolt = MetricBolt(10, 1.5, 20, '8.8')
        self.un_bolt = UNBolt(3 / 8, 24, True, 3, True, 1, '1')

    def test_height(self):
        self.assertAlmostEqual(self.metric_bolt.height, self.metric_bolt.pitch * sqrt(3) / 2)
        self.assertAlmostEqual(self.un_bolt.height, self.un_bolt.pitch * sqrt(3) / 2)

    def test_mean_diam(self):
        self.assertAlmostEqual(self.metric_bolt.mean_diam,
                               self.metric_bolt.diameter - (5 / 8) * self.metric_bolt.height)
        self.assertAlmostEqual(self.un_bolt.mean_diam,
                               self.un_bolt.diameter - (5 / 8) * self.un_bolt.height)

    def test_root_diam(self):
        self.assertAlmostEqual(self.metric_bolt.root_diam,
                               self.metric_bolt.diameter - (5 / 4) * self.metric_bolt.height)
        self.assertAlmostEqual(self.un_bolt.root_diam,
                               self.un_bolt.diameter - (5 / 4) * self.un_bolt.height)

    def test_pitch_diam(self):
        self.assertAlmostEqual(self.metric_bolt.pitch_diam,
                               self.metric_bolt.diameter - (3 / 8) * self.metric_bolt.height)
        self.assertAlmostEqual(self.un_bolt.pitch_diam,
                               self.un_bolt.diameter - (3 / 8) * self.un_bolt.height)

    def test_head_diam(self):
        self.assertAlmostEqual(self.metric_bolt.head_diam, 1.5 * self.metric_bolt.diameter)
        self.assertAlmostEqual(self.un_bolt.head_diam, 1.5 * self.un_bolt.diameter)

    def test_unthreaded_length(self):
        self.assertAlmostEqual(self.metric_bolt.unthreaded_length,
                               self.metric_bolt.length - self.metric_bolt.thread_length)
        self.assertAlmostEqual(self.un_bolt.unthreaded_length,
                               self.un_bolt.length - self.un_bolt.thread_length)

    def test_nominal_area(self):
        self.assertAlmostEqual(self.metric_bolt.nominal_area,
                               0.25 * pi * self.metric_bolt.diameter ** 2)
        self.assertAlmostEqual(self.un_bolt.nominal_area, 0.25 * pi * self.un_bolt.diameter ** 2)

    def test_thread_length(self):
        self.assertAlmostEqual(self.metric_bolt.thread_length, 26)
        self.assertAlmostEqual(self.un_bolt.thread_length, 1.0)

    def test_stress_area(self):
        self.assertAlmostEqual(self.metric_bolt.stress_area, 57.9895969018452)
        self.assertAlmostEqual(self.un_bolt.stress_area, 0.08782852079016222)

    def test_minor_area(self):
        self.assertAlmostEqual(self.metric_bolt.minor_area, 52.29231784971083)
        self.assertAlmostEqual(self.un_bolt.minor_area, 0.08086439817949277)
