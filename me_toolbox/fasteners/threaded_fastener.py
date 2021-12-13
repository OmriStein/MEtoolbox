"""module containing the ThreadedFastener class used for strength analysis"""
from math import tan, radians, pi, log

from numpy import array

from me_toolbox.fatigue import EnduranceLimit, FatigueAnalysis
from me_toolbox.fasteners import MetricBolt, UNBolt
from me_toolbox.tools import print_atributes


class ThreadedFastener:
    # TODO: add pre-torque calculation
    def __init__(self, bolt, layers, pre_load, load, nut=True,
                 endurance_limit=None, reliability=50, temp=25, surface_finish='hot-rolled'):
        """Initialize threaded fastener with a nut
        :param MetricBolt or UNBolt bolt: A bolt object
        :param list[list] layers: list containing lists of layers thicknesses and materials
        :param float pre_load: the initial loading of the bolt
        :param float load: the load on the fastener
        :param Boolean nut: True if a nut is used, False if the last layer is threaded
        :param float endurance_limit: Bolt's endurance limit (Not required)
        :param float reliability: Bolt's reliability (for Se calc)
        :param float temp: Working temp (for Se calc)
        :param str surface_finish: 'machined' or 'hot-rolled' (for Se calc)
        """
        self.bolt = bolt
        self.layers = layers
        self.grip_length = sum([lyr[0] for lyr in layers])
        self.pre_load = pre_load
        self.load = load
        self.nut = nut
        self.reliability = reliability
        self.temp = temp
        self.surface_finish = surface_finish
        self.endurance_limit = endurance_limit  # TODO: think about moving to Bolt

        # FIXME: make this note less annoying
        # unit = 'mm' if isinstance(bolt, MetricBolt) else 'in'
        # print(f"Note: the space left for the nut is: {bolt.length - griped_length}{unit}")
        # lt = self.griped_threads

    def get_info(self):
        """print all the spring properties"""
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
        head_diam = self.bolt.head_diam
        if not self.nut:
            # if the fastener has no bolt but the last layer is threaded instead
            if layers[-1][0] < self.bolt.diameter:
                # replace the last layer for half its size
                grip_length = sum([lyr[0] for lyr in layers[:-1]]) + 0.5*layers[-1][0]
                layers[-1][0] *= 0.5
            else:
                # replace the last layer for half the nominal diameter size
                grip_length = sum([lyr[0] for lyr in layers[:-1]]) + 0.5 * self.bolt.diameter
                layers[-1][0] = 0.5 * self.bolt.diameter

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

    @property
    def bolt_load(self):
        """The load on the bolt (Fb)"""
        return self.fastener_stiffness * self.load + self.pre_load

    @property
    def substrate_load(self):
        """The load on the substrate (Fm)"""
        return (1 - self.fastener_stiffness) * self.load - self.pre_load

    @property
    def separation_safety_factor(self):
        """Safety factor against joint separation"""
        return self.pre_load / (self.load * (1 - self.fastener_stiffness))

    def calc_pre_load(self, n0):
        """calculating preload using
        Safety factor against joint separation
        :param float n0: joint separation safety factor
        """
        return n0 * self.load * (1 - self.fastener_stiffness)

    @property
    def load_safety_factor(self):
        """Safety factor for load (nL)"""
        return (self.bolt.proof_load - self.pre_load) / (self.fastener_stiffness * self.load)

    @property
    def proof_safety_factor(self):
        """Safety factor for proof stress (np)"""
        return self.bolt.proof_load / self.bolt_load

    def calc_number_of_bolts(self, total_force, load_safety_factor, preload):
        """Returns the number of bolts needed for a given load factor, total force and preload
         on the fastener
         :param float total_force: Total force on the fastener
         :param float load_safety_factor: The fastener load safety factor
         :param float preload: Preload of the bolt
         """
        return (load_safety_factor*self.fastener_stiffness*total_force) / \
               (self.bolt.proof_strength-preload)

    @property
    def endurance_limit(self):
        return self._endurance_limit

    @endurance_limit.setter
    def endurance_limit(self, Se):
        if Se is None:
            self._endurance_limit = self.calc_endurance_limit()
        else:
            self._endurance_limit = Se

    def calc_endurance_limit(self):
        """Calculate endurance limit for"""
        sigma = self.bolt_load / self.bolt.stress_area
        Se = EnduranceLimit(Sut=self.bolt.tensile_strength, surface_finish=self.surface_finish,
                            rotating=False, max_normal_stress=sigma, max_bending_stress=0,
                            stress_type='multiple', temp=self.temp,
                            reliability=self.reliability, material='steel',
                            diameter=self.bolt.stress_area)

        se_vals = {'5': (18.6, 16.3), '7': 20.6, '8': 23.2, '8.8': 129, '9.8': 140, '10.9': 162,
                   '12.9': 190}

        grade = self.bolt.grade

        if grade in se_vals:
            if grade == '5':
                if 0.25 < self.bolt.diameter < 1:
                    return se_vals['5'][0] * Se.Kd * Se.Ke
                else:
                    return se_vals['5'][1] * Se.Kd * Se.Ke
            else:
                return se_vals[grade] * Se.Kd * Se.Ke
        else:
            return Se.modified

    def fatigue_analysis(self, max_force, min_force, reliability,
                         criterion='modified goodman', verbose=False, metric=True):
        """ Returns safety factors for fatigue and
        for first cycle according to Langer
        :param float max_force: Maximal max_force acting on the spring
        :param float min_force: Minimal max_force acting on the spring
        :param float reliability: in percentage
        :param str criterion: fatigue criterion
        :param bool verbose: print more details
        :param bool metric: Metric or imperial

        :returns: static and dynamic safety factor
        :rtype: tuple[float, float]
        """
        # calculating mean and alternating forces
        alt_force = abs(max_force - min_force) / 2
        mean_force = (max_force + min_force) / 2

        alt_bolt_force = alt_force * self.fastener_stiffness
        mean_bolt_force = mean_force * self.fastener_stiffness + self.pre_load

        kf = 1
        alt_stress = kf * (alt_bolt_force / self.bolt.stress_area)
        mean_stress = (mean_bolt_force / self.bolt.stress_area)

        fatigue = FatigueAnalysis(endurance_limit=self.endurance_limit, ductile=True,
                                  Sy=self.bolt.yield_strength, Kf_normal=kf,
                                  alt_normal_stress=alt_stress, mean_normal_stress=mean_stress)
        Sut = self.bolt.tensile_strength
        Se = self.endurance_limit
