"""module containing the ThreadedFastener class used for strength analysis"""
from math import tan, radians, pi, log

from numpy import array

from me_toolbox.fasteners import MetricBolt, UnBolt
from me_toolbox.tools import print_atributes


class ThreadedFastener:
    def __init__(self, bolt, griped_length, layers):
        """Initialize threaded fastener with a nut
        :param MetricBolt or UnBolt bolt: A bolt object
        :param float griped_length: Length of all material squeezed
            between face of bolt and face of nut
        :param tuple[tuple or list] or list[tuple or list] layers: tuple (or list)
            containing a tuple (or list) of layer thickness and material
        """
        self.bolt = bolt
        self.grip_length = griped_length
        self.layers = layers

        # FIXME: make this note less annoying
        unit = 'mm' if isinstance(bolt, MetricBolt) else 'in'
        print(f"Note: the space left for the nut is: {len(bolt) - griped_length}{unit}")
        lt = self.griped_threads

    @classmethod
    def threaded_plate(cls, bolt, plate_thickness, h, layers):
        """Create threaded fastener with threaded plate
        :param MetricBolt or UnBolt bolt: Bolt object
        :param float plate_thickness: threaded section length
        :param float h: thickness of all materials squeezed between
            the face of the bolt and the face of the threaded plate
        :param tuple[tuple or list] or list[tuple or list] layers: tuple (or list)
            containing a tuple (or list) of layer thickness and material
        """
        t2 = plate_thickness
        grip_length = h + 0.5 * t2 if t2 < bolt.diameter else h + 0.5 * bolt.diameter
        return ThreadedFastener(bolt, grip_length, layers)

    def get_info(self):
        """print all of the spring properties"""
        print_atributes(self)

    @property
    def griped_threads(self):
        """threaded section in grip (lt)"""
        lt = self.grip_length - self.bolt.unthreaded_length
        if lt <= 0:
            raise ValueError("the unthreaded_length (the shank) "
                             "is larger than the griped_length, Tip: use shorter bolt")
        return lt

    @property
    def bolt_stiffness(self):
        """bolt stiffness (Kb)"""
        bolt = self.bolt
        Ad = bolt.nominal_area
        At = bolt.stress_area
        E = bolt.elastic_modulus
        ld = bolt.unthreaded_length
        lt = self.grip_length - ld
        return (Ad * At * E) / ((Ad * lt) + (At * ld))

    @property
    def substrate_stiffness(self):
        """Substrate stiffness (Kb)"""
        angle = self.bolt.angle
        layers = self.layers
        grip_length = self.grip_length
        diameter = self.bolt.diameter
        return self.calc_substrate_stiffness(diameter, grip_length, layers, angle)

    @staticmethod
    def calc_substrate_stiffness(diameter, grip_length, layers, angle, verbose=False):
        """Calculates substrate stiffness (Kb)

        :param float diameter: Bolt's nominal diameter
        :param float grip_length: Length of gripped material
        :param tuple[tuple or list] or list[tuple or list] layers: tuple (or list)
            containing a tuple (or list) of layer thickness and material
        :param int angle: Thread angle
        :param bool verbose: print details for each layer
        
        :returns: Substrate stiffness
        :rtype: float
        """
        alpha = radians(angle / 2)

        thicknesses = [layer[0] for layer in layers]
        elastic_modulus = [layer[1] for layer in layers]

        # finding the layer divided by the center line
        half_grip_len = 0.5 * grip_length
        middle_index = 0
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
            elastic_modulus.insert(middle_index + 1, elastic_modulus[middle_index])

        diam = [1.5 * diameter]
        for index, thickness in enumerate(thicknesses):
            if index <= middle_index:
                diam.append(diam[index] + 2 * thickness * tan(alpha))
            else:
                diam.append(diam[index] - 2 * thickness * tan(alpha))

        diam.pop(middle_index + 1)

        stiffness = []
        d = diameter
        for D, t, E in zip(diam, thicknesses, elastic_modulus):
            ln = log(((1.155 * t + D - d) * (D + d)) / ((1.155 * t + D + d) * (D - d)))
            ki = (0.5774 * pi * E * d) / ln
            stiffness.append(ki)

            if verbose:
                print(f"d={d}, D={D}, t={t}, E={E}, ki={ki}")

        km_inv = sum(1 / array(stiffness))
        return 1 / km_inv

    @property
    def fastener_stiffness(self):
        """Fastener stiffness const (C),
        the fraction of external load carried by bolt
        """
        return self.bolt_stiffness / (self.substrate_stiffness + self.bolt_stiffness)
