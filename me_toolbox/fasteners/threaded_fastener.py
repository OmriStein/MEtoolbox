"""module containing the ThreadedFastener class used for fastener strength analysis"""
from copy import deepcopy

from math import tan, radians, pi, log

from numpy import array

# from me_toolbox.fatigue import FatigueAnalysis
from me_toolbox.fasteners import Bolt
from me_toolbox.tools import print_atributes


class ThreadedFastener:
    # TODO: add pre-torque calculation
    def __repr__(self):
        return f"Fastener(M{self.bolt.diameter})"

    def __init__(self, bolt, layers, nut, preload=None):
        """Initialize threaded fastener object
        :param Bolt bolt: A bolt object
        :param list[list] layers: lists of layers thicknesses and elastic modulus
        e.g. [[10,207e3], [5,70e3], [5,207e3]]
        :param bool nut: True if a nut is used, False if the last layer is threaded
        :param float or none preload: The initial load on the bolt
        """

        self.bolt = bolt
        self.layers = layers
        self.nut = nut
        if preload is None:
            self.preload = bolt.estimate_preload(True)
            print(f"{self} - No preload was entered so an estimated value was used"
                  f"({round(self.preload,2)})"
                  f" under the assumption that the bolt is reusable ")
        else:
            self.preload = preload

    def get_info(self):
        """print all the fastener properties"""
        print_atributes(self)

    @property
    def grip_length(self):
        """griped length in the member (l)"""
        if self.nut:
            return sum([layer[0] for layer in self.layers])
        else:
            sum_of_unthreaded_layers = sum([layer[0] for layer in self.layers[:-1]])
            if self.layers[-1][0] < self.bolt.diameter:
                grip_length = sum_of_unthreaded_layers + 0.5 * self.layers[-1][0]
            else:
                grip_length = sum_of_unthreaded_layers + 0.5 * self.bolt.diameter
            return grip_length

    @property
    def griped_thread_length(self):
        """threaded section in grip (lt)"""
        lt = self.grip_length - self.bolt.shank_length
        if lt <= 0:
            raise ValueError(f"The bolt's shank length ({self.bolt.shank_length}) "
                             f"is larger than the griped length({self.grip_length})")
        return lt

    @property
    def bolt_stiffness(self):
        """bolt stiffness (Kb)"""
        bolt = self.bolt
        Ad = bolt.nominal_area
        At = bolt.stress_area
        E = bolt.elastic_modulus
        ld = bolt.shank_length
        lt = self.griped_thread_length
        # print(f"Ad={Ad},At={At},E={E},ld={ld},lt={lt},L={bolt.length},LT={bolt.thread_length},l={self.grip_length}")
        return (Ad * At * E) / ((Ad * lt) + (At * ld))

    @property
    def member_stiffness(self):
        """ member stiffness (Kb) """
        d = self.bolt.diameter
        D1 = self.bolt.head_diameter
        lt = self.grip_length

        return self.calc_member_stiffness(d, D1, lt, self.layers, self.nut)

    @staticmethod
    def calc_member_stiffness(diameter, head_diam, grip_length, Layers, nut=True, verbose=False):
        """Calculates member stiffness (Kb)
        :param float diameter: Bolt's nominal diameter
        :param float head_diam: Bolt's head diameter
        :param float grip_length: Length of gripped material
        :param list[list] Layers: tuple (or list)
            containing a tuple (or list) of layer thickness and material
        :param bool nut: True if fastener has a nut, False if the last layer is threaded
        :param bool verbose: print details for each layer

        :returns: Substrate stiffness
        :rtype: float
        """
        alpha = radians(30)  # angle of the approximated stress cone
        layers = deepcopy(Layers)

        if not nut:
            if layers[-1][0] < diameter:
                # replace the last layer for a layer half its size
                layers[-1][0] *= 0.5
            else:
                # replace the last layer for a layer half the nominal diameter size
                layers[-1][0] = 0.5 * diameter

        thicknesses = [layer[0] for layer in layers]
        elastic_modulus = [layer[1] for layer in layers]

        # finding the layer divided by the center line
        half_grip_len = 0.5 * grip_length
        tot = 0
        middle_index = 0
        for index, width in enumerate(thicknesses):
            tot += width
            if tot >= half_grip_len:
                middle_index = index
                break

        thickness_before_center_layer = sum(thicknesses[:middle_index])
        thickness_including_center_layer = tot

        if (thickness_including_center_layer - half_grip_len) != 0:
            # if half the grip length is not equal exactly
            # to the sum of layers composing it, split middle layer in to two parts
            thicknesses[middle_index] = (half_grip_len - thickness_before_center_layer)
            thicknesses.insert(middle_index + 1, thickness_including_center_layer - half_grip_len)
            elastic_modulus.insert(middle_index + 1, elastic_modulus[middle_index])

        diam = [head_diam]
        for index, thickness in enumerate(thicknesses):
            if index <= middle_index:
                diam.append(diam[index] + 2 * thickness * tan(alpha))
            else:
                diam.append(diam[index] - 2 * thickness * tan(alpha))

        diam.pop(middle_index + 1)  # removing the center line diameter

        stiffness = []
        d = diameter
        for D, t, E in zip(diam, thicknesses, elastic_modulus):
            ln = log(((1.155 * t + D - d) * (D + d)) / ((1.155 * t + D + d) * (D - d)))
            ki = (0.5774 * pi * E * d) / ln
            stiffness.append(ki)

            if verbose:
                print(f"d={d}, D={D}, t={t}, E={E}, ki={ki:.2f}")

        km_inv = sum(1 / array(stiffness))
        if verbose:
            print(f"Km={1 / km_inv:.2f}")
        return 1 / km_inv

    @property
    def fastener_stiffness(self):
        """Fastener stiffness of the joint (C),
        the fraction of external load carried by bolt
        """
        return self.bolt_stiffness / (self.member_stiffness + self.bolt_stiffness)

    def bolt_load(self, external_force):
        """The load on the bolt (Fb)"""
        return self.fastener_stiffness * external_force + self.preload

    def member_load(self, bolt_load):
        """The load on the member (Fm)"""
        return (1 - self.fastener_stiffness) * bolt_load - self.preload

    @staticmethod
    def bolt_stress(bolt_load, stress_area):
        """Bolt stress from pure tension"""
        return bolt_load/stress_area

    def load_safety_factor(self, equivalent_stress):
        """Safety factor for load (nL)"""
        return (self.bolt.proof_load - self.preload) / (
                (equivalent_stress * self.bolt.stress_area) - self.preload)

    def separation_safety_factor(self, external_force):
        """Safety factor against joint separation (n0)"""
        return self.preload / (external_force * (1 - self.fastener_stiffness))

    def proof_safety_factor(self, equivalent_stress):
        """Safety factor for proof strength (np)"""
        return self.bolt.proof_strength / equivalent_stress
