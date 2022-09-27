"""module containing the ThreadedFastener class used for strength analysis"""
from math import tan, radians, pi, log

from numpy import array

from me_toolbox.fatigue import FatigueAnalysis
from me_toolbox.fasteners import MetricBolt, UNBolt
from me_toolbox.tools import print_atributes


class ThreadedFastener:
    # TODO: add pre-torque calculation
    def __repr__(self):
        return f"Fastener(M{self.bolt.diameter})"

    def __init__(self, bolt, layers, pre_load=None, load=None, nut=True):
        """Initialize threaded fastener with a nut
        :param MetricBolt or UNBolt bolt: A bolt object
        :param list[list] layers: list containing lists of layers thicknesses and elastic modulus
        :param float pre_load: the initial loading of the bolt
        :param float load: the load on the fastener
        :param Boolean nut: True if a nut is used, False if the last layer is threaded
        """
        self.bolt = bolt
        self.layers = layers
        self.pre_load = pre_load
        self.load = load
        self.nut = nut

        # FIXME: make this note less annoying
        # unit = 'mm' if isinstance(bolt, MetricBolt) else 'in'
        # print(f"Note: the space left for the nut is: {bolt.length - griped_length}{unit}")
        # lt = self.griped_thread_length

    def get_info(self):
        """print all the fastener properties"""
        print_atributes(self)

    @property
    def grip_length(self):
        """griped length in the substrate (l)"""
        if self.nut:
            return sum([layer[0] for layer in self.layers])
        else:
            if self.layers[-1][0] < self.bolt.diameter:
                grip_length = sum([layer[0] for layer in self.layers[:-1]]) + 0.5*self.layers[-1][0]
                # replace the last layer for half its size
                self.layers[-1][0] *= 0.5
            else:
                grip_length = sum([layer[0] for layer in self.layers[:-1]]) + 0.5 * self.bolt.diameter
                # replace the last layer for half the nominal diameter size
                self.layers[-1][0] = 0.5 * self.bolt.diameter
            return grip_length

    @property
    def griped_thread_length(self):
        """threaded section in grip (lt)"""
        lt = self.grip_length - self.bolt.shank_length
        if lt <= 0:
            raise ValueError("the shank_length (the shank) "
                             "is larger than the griped_length, Tip: use shorter bolt")
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
        return (Ad * At * E) / ((Ad * lt) + (At * ld))

    @property
    def substrate_stiffness(self):
        """Substrate stiffness (Kb)"""
        angle = self.bolt.angle
        layers = self.layers
        grip_length = self.grip_length
        diameter = self.bolt.diameter
        head_diam = self.bolt.head_diam
        # if not self.nut:
        #     # if the fastener has no nut, i.e. the last layer is threaded.
        #     if layers[-1][0] < self.bolt.diameter:
        #         grip_length = sum([layer[0] for layer in layers[:-1]]) + 0.5*layers[-1][0]
        #         # replace the last layer for half its size
        #         layers[-1][0] *= 0.5
        #     else:
        #         grip_length = sum([layer[0] for layer in layers[:-1]]) + 0.5 * self.bolt.diameter
        #         # replace the last layer for half the nominal diameter size
        #         layers[-1][0] = 0.5 * self.bolt.diameter

        return self.calc_substrate_stiffness(diameter, head_diam, grip_length, layers, angle)

    @staticmethod
    def calc_substrate_stiffness(diameter, head_diam, grip_length, layers, angle, verbose=False):
        """Calculates substrate stiffness (Kb)
        :param float diameter: Bolt's nominal diameter
        :param float head_diam: Bolt's head diameter
        :param float grip_length: Length of gripped material
        :param tuple[tuple or list] or list[tuple or list] layers: tuple (or list)
            containing a tuple (or list) of layer thickness and material
        :param int angle: Thread angle
        :param bool verbose: print details for each layer
        
        :returns: Substrate stiffness
        :rtype: float
        """
        alpha = radians(angle / 2)  # angle of the approximated stress shape

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
        return self.bolt_stiffness / (self.substrate_stiffness + self.bolt_stiffness)

    def bolt_load(self, bolt_load):
        """The load on the bolt (Fb)"""
        return self.fastener_stiffness * bolt_load + self.bolt.preload

    def substrate_load(self, bolt_load):
        """The load on the substrate (Fm)"""
        return (1 - self.fastener_stiffness) * bolt_load - self.bolt.preload

    def load_safety_factor(self, equivalent_stresses):
        """Safety factor for load (nL)"""
        return (self.bolt.proof_load - self.bolt.preload) / (
                (equivalent_stresses * self.bolt.stress_area) - self.bolt.preload)

    def separation_safety_factor(self, bolt_load):
        """Safety factor against joint separation (n0)"""
        return self.bolt.preload / (bolt_load * (1 - self.fastener_stiffness))

    def proof_safety_factor(self, equivalent_stress):
        """Safety factor for proof strength (np)"""
        return self.bolt.proof_strength / equivalent_stress
