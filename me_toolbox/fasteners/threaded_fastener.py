"""module containing the ThreadedFastener class used for strength analysis"""
from math import tan, radians, pi, log
import numpy as np

from me_toolbox.fasteners import Bolt
from me_toolbox.tools import print_atributes


class ThreadedFastener:
    def __init__(self, bolt, grip_length, layers):
        """Initialize threaded fastener with a nut
        :param Bolt bolt: A bolt object
        :param float grip_length: Length of all material squeezed
            between face of bolt and face of nut
        :param tuple[tuple or list] or list[tuple or list] layers: a tuple (or list)
            containing a tuple (or list) of layer thickness and material
        """
        self.bolt = bolt
        self.grip_length = grip_length
        self.layers = layers

    @classmethod
    def threaded_plate(cls, bolt, plate_thickness, h):
        """Create threaded fastener with threaded plate
        :param Bolt bolt: Bolt object
        :param float plate_thickness: threaded section length
        :param float h: thickness of all materials squeezed between
            the face of the bolt and the face of the threaded plate
        """
        t2 = plate_thickness
        grip_length = h + 0.5 * t2 if t2 < bolt.diameter else h + 0.5 * bolt.diameter
        return ThreadedFastener(bolt, grip_length)

    def get_info(self):
        """print all of the spring properties"""
        print_atributes(self)

    @property
    def griped_threads(self):
        """threaded section in grip"""
        return self.grip_length - self.bolt.unthreaded_length

    @property
    def fastener_stiffness(self):
        """fastener stiffness (Kb)"""
        bolt = self.bolt
        Ad = bolt.nominal_area
        At = bolt.stress_area
        E = bolt.elastic_modulus
        ld = bolt.unthreaded_length
        lt = self.grip_length - ld
        return (Ad * At * E) / ((Ad * lt) + (At * ld))

    @property
    def substrate_stiffness(self):
        angle = self.bolt.angle
        alpha = radians(angle / 2)

        thicknesses = [layer[0] for layer in self.layers]
        elastic_modulus = [layer[1] for layer in self.layers]

        # finding the layer divided by the center line
        half_grip_len = 0.5 * self.grip_length
        for index in range(len(thicknesses)):
            tot = 0
            for k in range(index + 1):
                tot += thicknesses[k]
            if tot >= half_grip_len:
                middle_index = index
                break

        thickness_before_center_layer = sum(thicknesses[:middle_index])
        thickness_including_center_layer = sum(thicknesses[:middle_index + 1])

        if (thickness_including_center_layer - half_grip_len) != 0:
            # if half the grip length is not equal exactly
            # to the sum layers composing it split the middle layer to two
            thicknesses[middle_index] = (half_grip_len - thickness_before_center_layer)
            thicknesses.insert(middle_index + 1, thickness_including_center_layer - half_grip_len)

        diam = [self.bolt.head_diam]
        for index, thickness in enumerate(thicknesses):
            if index <= middle_index:
                diam.append(diam[index] + 2 * thickness * tan(alpha))
            else:
                diam.append(diam[index] - 2 * thickness * tan(alpha))

        diam.pop(middle_index + 1)

        d = self.bolt.diameter
        stiffness = []
        for D, t, E in zip(diam, thicknesses, elastic_modulus):
            ln = log(((1.115 * t + D - d) * (D + d)) / ((1.115 * t + D + d) * (D - d)))
            stiffness.append(0.5774 * pi * E * d / ln)
        km_inv = sum(1 / np.array(stiffness))
        return 1 / km_inv
