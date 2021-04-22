from unittest import TestCase
from math import log, pi, tan, radians
import numpy as np

from me_toolbox.fasteners import MetricBolt, UnBolt
from me_toolbox.fasteners import ThreadedFastener


def stiffness(d, Diam, thickness, Elastic):
    stiff = []
    for D, t, E in zip(Diam, thickness, Elastic):
        ln = log(((1.115 * t + D - d) * (D + d)) / ((1.115 * t + D + d) * (D - d)))
        stiff.append(0.5774 * pi * E * d / ln)
    km_inv = sum(1 / np.array(stiff))
    return 1 / km_inv


class TestThreadedFastener(TestCase):
    angle = 60
    alpha = radians(angle / 2)
    tan_alpha = tan(radians(30))

    def setUp(self):
        self.bolt = MetricBolt(10, 1.5, 'e', 3, 20)
        # self.bolt = UnBolt(3/8, 24, True, 3, True,  1)

        thickness = [2, 3, 3, 2, 3]
        Elastic = [200e3, 70e3, 200e3, 200e3, 200e3]
        layers = [(t, E) for t, E in zip(thickness, Elastic)]
        grip_len = (sum([layer[0] for layer in layers]))
        self.fastener = ThreadedFastener(self.bolt, grip_len, layers)

    def test_griped_thread(self):
        self.assertAlmostEqual(self.fastener.griped_threads, 19)

    def test_fastener_stiffness(self):
        self.assertAlmostEqual(self.fastener.fastener_stiffness, 796017.9937058988)

    def test_substrate_stiffness_1(self):
        # test if the first substrate is smaller than half the material
        thickness = [2, 3, 3, 2, 3]
        Elastic = [200e3, 70e3, 200e3, 200e3, 200e3]
        layers = [(t, E) for t, E in zip(thickness, Elastic)]

        D1, D6 = 15, 15
        D2 = D1 + 2 * thickness[0] * self.tan_alpha
        D3 = D2 + 2 * thickness[1] * self.tan_alpha
        D5 = D6 + 2 * thickness[2] * self.tan_alpha
        D4 = D5 + 2 * thickness[3] * self.tan_alpha
        Diam = [D1, D2, D3, D4, D5, D6]
        grip_len = (sum([layer[0] for layer in layers]))
        km = stiffness(self.bolt.diameter, Diam, [2, 3, 1.5, 1.5, 2, 3], Elastic)
        self.fastener.grip_length = grip_len
        self.fastener.layers = layers
        self.assertAlmostEqual(self.fastener.substrate_stiffness, km)

    def test_substrate_stiffness_2(self):
        # test if the first substrate is smaller than half the material
        thickness = [2, 4, 4]
        Elastic = [200e3, 70e3, 200e3]
        layers = [(t, E) for t, E in zip(thickness, Elastic)]
        D1, D4 = 15, 15
        D2 = D1 + 2 * thickness[0] * self.tan_alpha
        D3 = D4 + 2 * thickness[2] * self.tan_alpha
        Diam = [D1, D2, D3, D4]
        grip_len = (sum([layer[0] for layer in layers]))
        km = stiffness(self.bolt.diameter, Diam, [2, 3, 1, 4], Elastic)
        self.fastener.grip_length = grip_len
        self.fastener.layers = layers
        self.assertAlmostEqual(self.fastener.substrate_stiffness, km)

    def test_substrate_stiffness_3(self):
        # test if the first substrate is larger than half the material
        thickness = [5, 1, 2]
        Elastic = [200e3, 70e3, 200e3]
        layers = [(t, E) for t, E in zip(thickness, Elastic)]
        D1, D4 = 15, 15
        D3 = D4 + 2 * thickness[2] * self.tan_alpha
        D2 = D3 + 2 * thickness[1] * self.tan_alpha
        Diam = [D1, D2, D3, D4]
        grip_len = (sum([layer[0] for layer in layers]))
        km = stiffness(self.bolt.diameter, Diam, [4, 1, 1, 2], Elastic)
        self.fastener.grip_length = grip_len
        self.fastener.layers = layers
        self.assertAlmostEqual(self.fastener.substrate_stiffness, km)

    def test_substrate_stiffness_4(self):
        # test symmetric layers
        thickness = [2, 4, 2]
        Elastic = [200e3, 70e3, 200e3]
        layers = [(t, E) for t, E in zip(thickness, Elastic)]
        D1, D4 = 15, 15
        D2 = D1 + 2 * thickness[0] * self.tan_alpha
        D3 = D4 + 2 * thickness[2] * self.tan_alpha
        Diam = [D1, D2, D3, D4]
        grip_len = (sum([layer[0] for layer in layers]))
        km = stiffness(self.bolt.diameter, Diam, [2, 2, 2, 2], Elastic)
        self.fastener.grip_length = grip_len
        self.fastener.layers = layers
        self.assertAlmostEqual(self.fastener.substrate_stiffness, km)

    def test_substrate_stiffness_5(self):
        # test center between layers
        thickness = [2, 3, 3, 2]
        Elastic = [200e3, 70e3, 200e3, 200e3]
        layers = [(t, E) for t, E in zip(thickness, Elastic)]
        D1, D4 = 15, 15
        D2 = D1 + 2 * 2 * self.tan_alpha
        D3 = D4 + 2 * 2 * self.tan_alpha
        Diam = [D1, D2, D3, D4]
        grip_len = (sum([layer[0] for layer in layers]))
        km = stiffness(self.bolt.diameter, Diam, thickness, Elastic)
        self.fastener.grip_length = grip_len
        self.fastener.layers = layers
        self.assertAlmostEqual(self.fastener.substrate_stiffness, km)

