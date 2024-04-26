"""A module containing the helical push spring class"""
from math import pi, sqrt
from sympy import sqrt

from me_toolbox.fatigue import FailureCriteria
from me_toolbox.springs import Spring
from me_toolbox.tools import percent_to_decimal


class HelicalCompressionSpring(Spring):
    """A helical push spring object"""
    def __repr__(self):
        return f"HelicalCompressionSpring(max_force={self.max_force}, " \
               f"wire_diameter={self.wire_diameter}, spring_diameter={self.diameter}, " \
               f"ultimate_tensile_strength={self.ultimate_tensile_strength}, " \
               f"shear_yield_percent={self.shear_yield_percent}, " \
               f"shear_modulus={self.shear_modulus}, elastic_modulus={self.elastic_modulus}, " \
               f"end_type={self.end_type}, spring_rate={self.spring_rate}, " \
               f"set_removed={self.set_removed}, shot_peened={self.shot_peened}, " \
               f"density={self.density}, working_frequency={self.working_frequency}, " \
               f"anchors={self.anchors}, zeta={self.zeta})"

    def __str__(self):
        return f"HelicalCompressionSpring(d={self.wire_diameter}, D={self.diameter}, " \
               f"k={self.spring_rate}, L0={self.free_length})"

    def __init__(self, max_force, wire_diameter, spring_diameter, ultimate_tensile_strength,
                 shear_yield_percent, shear_modulus, elastic_modulus, end_type,
                 spring_rate, set_removed=False, shot_peened=False,
                 density=None, working_frequency=None, anchors=None, zeta=0.15):
        """Instantiate helical push spring object with the given parameters.

        :param float max_force: The maximum load on the spring [N]
        :param float wire_diameter: Spring wire diameter [mm]
        :param float spring_diameter: Spring diameter measured from [mm]
            the center point of the wire diameter
        :param float ultimate_tensile_strength: Ultimate tensile strength of the material [MPa]
        :param float shear_yield_percent: Yield percent used to estimate shear_yield_stress
        :param float shear_modulus: Shear modulus [MPa]
        :param float or None elastic_modulus: Elastic modulus (used for buckling calculations) [MPa]
        :param str end_type: What kind of ending the spring has (effects length and number of coils)
            ,the options are: 'plain', 'plain and ground', 'squared or closed', 'squared and ground'
        :param float or None spring_rate: Spring rate (k) [N/mm]
        :param bool set_removed: If True adds to STATIC strength
            (must NOT use for fatigue application)
        :param bool shot_peened: If True adds to fatigue strength
        :param float or None density: Material density (used for finding natural frequency) [kg/m^3]
        :param float or None working_frequency: the spring working frequency [Hz]
        :param str or None anchors: How the spring is anchored (for buckling test),
            The options are: 'fixed-fixed', 'fixed-hinged', 'hinged-hinged', 'clamped-free'

            (used for buckling calculations)
        :param float zeta: Overrun safety factor

        :returns: HelicalCompressionSpring object
        """

        super().__init__(max_force, wire_diameter, spring_diameter, spring_rate,
                         ultimate_tensile_strength, shear_modulus, elastic_modulus,
                         shot_peened, density, working_frequency)

        if set_removed:
            print("Note: set should ONLY be removed for static loading"
                  "and NOT for periodical loading")

        self.set_removed = set_removed
        self.shear_yield_percent = shear_yield_percent
        self.zeta = zeta  # overrun safety factor
        self.end_type = end_type.lower()

        end_types = ('plain', 'plain and ground', 'squared or closed', 'squared and ground')
        if self.end_type not in end_types:
            raise ValueError(f"{end_type} not one of this: {end_types}")

        self.anchors = anchors

        self.check_design()

    def check_design(self):
        """Check if the spring index,active_coils,zeta and free_length
        are in acceptable range for good design

        :returns: True if all the checks are good
        :rtype: bool
        """
        good_design = True
        C = self.spring_index  # pylint: disable=invalid-name
        if isinstance(C, float) and not 4 <= C <= 12 and self.set_removed:
            print("Note: C - spring index should be in range of [4,12],"
                  "lower C causes surface cracks,\n"
                  "higher C causes the spring to tangle and requires separate packing")
            good_design = False
        elif isinstance(C, float) and not 3 <= C <= 12:
            print("Note: C - spring index should be in range of [3,12],"
                  "lower C causes surface cracks,\n"
                  "higher C causes the spring to tangle and requires separate packing")
            good_design = False

        active_coils = self.active_coils
        if isinstance(active_coils, float) and not 3 <= active_coils <= 15:
            print(f"Note: active_coils={active_coils:.2f} is not in range [3,15],"
                  f"this can cause non linear behavior")
            good_design = False

        zeta = self.zeta
        if zeta < 0.15:
            print(f"Note: zeta={zeta:.2f} is smaller then 0.15,"
                  f"the spring could reach its solid length")
            good_design = False
        if (self.free_length is not None) and (self.anchors is not None) \
                and (self.elastic_modulus is not None):
            buckling, safe_length = self.buckling(self.anchors, verbose=False)
            if buckling:
                print(f"Note: buckling is accruing, max free length"
                      f"(free_length)= {safe_length:.2f}, "
                      f"free_length= {self.free_length:.2f}")
                good_design = False

        if (self.density is not None) and (self.working_frequency is not None):
            natural_freq = self.natural_frequency
            if natural_freq <= 20 * self.working_frequency:
                print(
                    f"Note: the natural frequency={natural_freq:.2f} is less than 20*working"
                    f"frequency={20 * self.working_frequency:.2f} which is not good")
                good_design = False

        return good_design

    @property
    def free_length(self):
        """Calculates the free length of the spring"""
        return (self.Fsolid / self.spring_rate) + self.solid_length

    @property
    def solid_length(self):
        """Ls - the solid length of the spring
        (if the spring is fully compressed so the coils are touching each other)

        :returns: Spring solid length (when all the coils are touching)
        :rtype: float
        """
        diameter = self.wire_diameter
        total_coils = self.total_coils
        options = {'plain': diameter * (total_coils + 1),
                   'plain and ground': diameter * total_coils,
                   'squared or closed': diameter * (total_coils + 1),
                   'squared and ground': diameter * total_coils}
        return options.get(self.end_type)

    @property
    def Fsolid(self):  # pylint: disable=invalid-name
        """calculate the max_force necessary to bring the spring to solid length
        it is good practice for the max_force that compresses the spring to
        solid state to be greater than the maximum max_force anticipated, so we
        use this calculation: Fs=(1+zeta)Fmax in case the free length is unknown

        Note: zeta is the overrun safety factor, it's customary that zeta=0.15 so Fs=1.15Fmax

        :returns: The max_force it takes to get the spring to solid length
        :rtype: float
        """
        return (1 + self.zeta) * self.max_force

    @property
    def active_coils(self):
        """Calculate active_coils which is the number of active coils (using Castigliano's theorem)

        :returns: number of active coils
        :rtype: float
        """
        return ((self.shear_modulus * self.wire_diameter) /
                (8 * self.spring_index ** 3 * self.spring_rate)) * (
                       (2 * self.spring_index ** 2) / (1 + 2 * self.spring_index ** 2))

    @property
    def end_coils(self):
        """Ne - the end coils of the spring

        :returns: Number of the spring end coils
        :rtype: float
        """
        options = {'plain': 0,
                   'plain and ground': 1,
                   'squared or closed': 2,
                   'squared and ground': 2}
        return options.get(self.end_type)

    @property
    def total_coils(self):
        """Nt - the total coils of the spring

        :returns: Number of the spring total coils
        :rtype: float
        """
        return self.end_coils + self.active_coils

    @property
    def pitch(self):
        """ p - pitch of the spring (the distance between the coils)

        :returns: Pitch
        :rtype: float
        """
        options = {'plain': (self.free_length - self.wire_diameter) / self.active_coils,
                   'plain and ground': self.free_length / (self.active_coils + 1),
                   'squared or closed': ((self.free_length - 3 * self.wire_diameter) /
                                         self.active_coils),
                   'squared and ground': ((self.free_length - 2 * self.wire_diameter) /
                                          self.active_coils)}
        return options.get(self.end_type)

    @property
    def shear_yield_strength(self):
        """ Ssy - yield strength for shear
        (shear_yield_stress = % * ultimate_tensile_strength))

        :returns: yield strength for shear stress
        :rtype: float
        """
        try:
            return percent_to_decimal(self.shear_yield_percent) * self.ultimate_tensile_strength
        except TypeError:
            return self.shear_yield_percent * self.ultimate_tensile_strength

    @property
    def factor_Ks(self):  # pylint: disable=invalid-name
        """factor_Ks - Static shear stress concentration factor

        :returns: Static shear stress concentration factor
        :rtype: float
        """
        return (2 * self.spring_index + 1) / (2 * self.spring_index)

    @property
    def factor_Kw(self):  # pylint: disable=invalid-name
        """K_W - Wahl shear stress concentration factor

        :returns: Wahl shear stress concentration factor
        :rtype: float
        """
        return (4 * self.spring_index - 1) / (4 * self.spring_index - 4) + \
               (0.615 / self.spring_index)

    @property
    def factor_KB(self):  # pylint: disable=invalid-name
        """K_B - Bergstrasser shear stress concentration factor (very close to factor_Kw)

        NOTE:for the sake of completion NOT IMPLEMENTED!!!

        :returns: Bergstrasser shear stress concentration factor
        :rtype: float
        """
        return (4 * self.spring_index + 2) / (4 * self.spring_index - 3)

    @property
    def max_shear_stress(self):
        """ Return's the shear stress

        :returns: Shear stress
        :rtype: float
        """
        k_factor = self.factor_Ks if self.set_removed else self.factor_Kw
        return self.calc_shear_stress(self.max_force, k_factor)

    def calc_shear_stress(self, force, k_factor):
        """Calculates the max shear stress based on the max_force applied.

        :param float force: Working max_force of the spring
        :param float k_factor: the appropriate k factor for the calculation

        :returns: Shear stress
        :rtype: float
        """
        return (k_factor * 8 * force * self.diameter) / (pi * self.wire_diameter ** 3)

    @property
    def natural_frequency(self):
        """Figures out what is the natural frequency of the spring"""
        d = self.wire_diameter
        D = self.diameter
        Na = self.active_coils
        G = self.shear_modulus
        try:
            return (d * 1e-3 / (2 * D * 1e-3 ** 2 * Na * pi)) * sqrt(G / (2 * self.density))
        except TypeError:
            return None

    @property
    def max_deflection(self):
        """Returns the spring max_deflection, It's change in length

        :returns: Spring max_deflection
        :rtype: float
        """
        return self.calc_deflection(self.max_force)

    def calc_deflection(self, force):
        """Calculate the spring deflection (change in length) due to specific max_force.

        :param float force: Spring working max_force

        :returns: Spring deflection
        :rtype: float
        """
        C = self.spring_index
        d = self.wire_diameter
        G = self.shear_modulus
        Na = self.active_coils
        return ((8 * force * C ** 3 * Na) / (G * d)) * ((1 + 2 * C ** 2) / (2 * C ** 2))

    @property
    def weight(self):
        """Return's the spring *active coils* weight according to the specified density

        :returns: Spring weight
        :type: float
        """
        area = 0.25 * pi * (self.wire_diameter * 1e-3) ** 2  # cross-section area
        length = pi * self.diameter * 1e-3  # the circumference of the spring
        coil_volume = area * length
        if self.density is not None:
            return coil_volume * self.total_coils * self.density
        else:
            raise ValueError(f"Can't calculate weight, no density is specified")

    def static_safety_factor(self, solid=False):
        """ Returns the static safety factor according to the object attributes

        :returns: static factor of safety
        :type: float
        """
        k_factor = self.factor_Ks if self.set_removed else self.factor_Kw
        if solid:
            shear_stress = self.calc_shear_stress(self.Fsolid, k_factor)
        else:
            shear_stress = self.max_shear_stress
        return self.shear_yield_strength / shear_stress

    def fatigue_analysis(self, max_force, min_force, reliability,
                         criterion='modified goodman', verbose=False, metric=True):
        """ Returns safety factors for fatigue and for first cycle according to Lange failure
        criteria.

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
        alternating_force = abs(max_force - min_force) / 2
        mean_force = (max_force + min_force) / 2

        # calculating mean and alternating stresses
        k_factor = self.factor_Ks if self.set_removed else self.factor_Kw
        alt_shear_stress = self.calc_shear_stress(alternating_force, k_factor)
        mean_shear_stress = self.calc_shear_stress(mean_force, k_factor)

        Sse = self.shear_endurance_limit(reliability, metric)
        Ssu = self.shear_ultimate_strength
        Ssy = self.shear_yield_strength
        nf, nl = FailureCriteria.get_safety_factors(Ssy, Ssu, Sse, alt_shear_stress,
                                                    mean_shear_stress, criterion)
        if verbose:
            print(f"Alternating force = {alternating_force:.2f}, Mean force = {mean_force:.2f}\n"
                  f"Alternating shear stress = {alt_shear_stress:.2f}, "
                  f"Mean shear stress = {mean_shear_stress:.2f}\n"
                  f"Sse = {Sse:.2f}")
        return nf, nl

    def min_wire_diameter(self, Ap, m, safety_factor, diameter=None, spring_index=None,
                          solid=False):
        """The minimal wire diameter for given
        safety factor in order to avoid failure,
        according to the spring parameters.
        if solid is True the calculation uses :attr:`Fsolid`
        instead of :attr:`max_force`

        Note: In order for the calculation to succeed the spring
            diameter or the spring index should be known

        :param float Ap: for Sut calc
        :param float m: for Sut calc
        :param float safety_factor: Static safety factor
        :param float diameter: The spring diameter
        :param float spring_index: The spring index
        :param bool solid: If true calculate to according to the solid max_force

        :returns: The minimal wire diameter
        :rtype: float
        """
        if spring_index is not None:
            factor_ks = (2 * spring_index + 1) / (2 * spring_index)
            factor_kw = (4 * spring_index - 1) / (4 * spring_index - 4) + (0.615 / spring_index)
            factor_k = factor_ks if self.set_removed else factor_kw
            force = self.Fsolid if solid else self.max_force
            return ((8 * factor_k * force * spring_index * safety_factor) / (
                    self.shear_yield_percent * Ap * pi)) ** (1 / (2 - m))

        elif spring_index is None and diameter is not None:

            factor_k, temp_k = 1.1, 0
            diam = 0
            while abs(factor_k - temp_k) > 1e-4:
                # waiting for k to converge
                diam = ((8 * self.max_force * diameter * safety_factor * factor_k) / (
                        pi * self.shear_yield_percent * Ap)) ** (1 / (3 - m))
                temp_k = factor_k
                factor_ks = (2 * diameter + diam) / (2 * diameter)
                factor_kb = (4 * diameter + 2 * diam) / (4 * diameter - 3 * diam)
                factor_k = factor_ks if self.set_removed else factor_kb
            return diam
        else:
            print("Need to know spring index or spring diameter to calculate wire diameter")

    def min_spring_diameter(self, safety_factor, wire_diameter, solid=False):
        """return the minimum spring diameter to avoid static failure
        according to the specified safety factor, if the solid flag is True :attr:'Fsolid'
        is used instead of :attr:`max_force`.

        :param float safety_factor: static safety factor
        :param float wire_diameter: Spring's wire diameter
        :param bool solid: If true calculate to according to the solid max_force

        :returns: The minimal spring diameter
        :rtype: float
        """
        force = self.Fsolid if solid else self.max_force
        d = wire_diameter
        if self.set_removed:
            Ssy = self.shear_yield_strength
            return 0.5 * ((Ssy / safety_factor) * ((pi * d ** 3) / (4 * force)) - d)
        else:
            # derived using the KB factor (because it was easier)
            Sut = self.ultimate_tensile_strength
            alpha = (Sut * pi * d ** 3) / (8 * self.max_force * safety_factor)
            return 0.25 * ((2 * alpha - d) + sqrt((d - 2 * alpha) ** 2 - 24 * alpha * d))

    def buckling(self, anchors, verbose=True):
        """ Checks if the spring will buckle and find the
        maximum free length to avoid buckling
        :param str or None anchors: How the spring is anchored
            (The options are: 'fixed-fixed', 'fixed-hinged', 'hinged-hinged', 'clamped-free')
        :param bool verbose: Print buckling test result
        :returns: True if buckling occurring and The maximum safe length (free_length)
            to avoid buckling
        :rtype: tuple(bool, float)
        """
        # alpha values from table 10-2
        options = {'fixed-fixed': 0.5, 'fixed-hinged': 0.707, 'hinged-hinged': 1, 'clamped-free': 2}

        try:
            D = self.diameter
            E = self.elastic_modulus
            G = self.shear_modulus
            alpha = options[anchors.lower()]
            max_safe_length = (pi * D / alpha) * sqrt((2 * (E - G)) / (2 * G + E))
        except ValueError as err:
            print(f"{err}, make sure E and G have the same units (Mpa)")
        except KeyError as key:
            print(f"Ends: {key} is unknown ")
        except AttributeError:
            print("Anchors not specified")
        else:
            if verbose:
                if self.free_length >= max_safe_length:
                    print(f"Buckling is accruing, the max safe length = {max_safe_length:.2f}, ",
                          f"but the free_length = {self.free_length:.2f}")

                else:
                    print(
                        f"Buckling is NOT accruing, the max safe length = {max_safe_length:.2f}, ",
                        f"and the free_length = {self.free_length:.2f}")

            return self.free_length >= max_safe_length, max_safe_length

    @staticmethod
    def calc_spring_rate(wire_diameter, spring_diameter, shear_modulus, active_coils):
        """Calculate spring constant (using Castigliano's theorem)

        :returns: The spring constant
        :rtype: float
        """
        d = wire_diameter
        D = spring_diameter
        G = shear_modulus
        C = D / d
        Na = active_coils
        return ((G * d) / (8 * C ** 3 * Na)) * ((2 * C ** 2) / (1 + 2 * C ** 2))
