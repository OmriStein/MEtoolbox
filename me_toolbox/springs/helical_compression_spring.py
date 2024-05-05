"""A module containing the helical push spring class"""
from math import pi  # , sqrt
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
               f"density={self.density}, zeta={self.zeta})"

    def __str__(self):
        return f"HelicalCompressionSpring(d={self.wire_diameter}, D={self.diameter}, " \
               f"k={self.spring_rate}, L0={self.free_length})"

    def __init__(self, max_force, wire_diameter, spring_diameter, ultimate_tensile_strength,
                 shear_yield_percent, shear_modulus, elastic_modulus, end_type,
                 spring_rate, set_removed=False, shot_peened=False,
                 density=None, zeta=0.15):
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
        :param float zeta: Overrun safety factor

        :returns: Helical Compression Spring object
        :rtype: HelicalCompressionSpring
        """

        super().__init__(max_force, wire_diameter, spring_diameter, spring_rate,
                         ultimate_tensile_strength, shear_modulus, elastic_modulus,
                         shot_peened, density)

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

        self.check_design()

    def check_design(self):
        """Check if the spring index,active coils, zeta and free length
         are in the acceptable range for good design.

        :returns: True if pass all checks
        :rtype: bool
        """
        return all([self._check_spring_index(), self._check_active_coils(), self._check_zeta()])

    def _check_spring_index(self) -> bool:
        in_range = True
        C = self.spring_index  # pylint: disable=invalid-name
        if isinstance(C, float) and not 4 <= C <= 12 and self.set_removed:
            print("Note: C - spring index should be in range of [4,12],"
                  "lower C causes surface cracks,\n"
                  "higher C causes the spring to tangle and requires separate packing")
            in_range = False
        elif isinstance(C, float) and not 3 <= C <= 12:
            print("Note: C - spring index should be in range of [3,12],"
                  "lower C causes surface cracks,\n"
                  "higher C causes the spring to tangle and requires separate packing")
            in_range = False
        return in_range

    def _check_active_coils(self) -> bool:
        in_range = True
        active_coils = self.active_coils
        if isinstance(active_coils, float) and not 3 <= active_coils <= 15:
            print(f"Note: active_coils={active_coils:.2f} is not in range [3,15],"
                  f"this can cause non linear behavior")
            in_range = False
        return in_range

    def _check_zeta(self) -> bool:
        in_range = True
        zeta = self.zeta
        if zeta < 0.15:
            print(f"Note: zeta={zeta:.2f} is smaller then 0.15,"
                  f"the spring could reach its solid length")
            in_range = False
        return in_range

    @property
    def free_length(self) -> float:
        """Calculates the free length of the spring"""
        return (self.Fsolid / self.spring_rate) + self.solid_length

    @property
    def solid_length(self) -> float:
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
    def active_coils(self) -> float:
        """Number of active coils (derived using Castigliano's theorem)"""

        # The full calculation
        # full = ((self.shear_modulus * self.wire_diameter) /
        #         (8 * self.spring_index ** 3 * self.spring_rate)) * (
        #                (2 * self.spring_index ** 2) / (1 + 2 * self.spring_index ** 2))

        # The accepted approximation
        return ((self.shear_modulus * self.wire_diameter) /
                (8 * self.spring_index ** 3 * self.spring_rate))

    @property
    def end_coils(self) -> float:
        """Number of the spring's end coils (Ne)"""

        options = {'plain': 0,
                   'plain and ground': 1,
                   'squared or closed': 2,
                   'squared and ground': 2}
        return options.get(self.end_type)

    @property
    def total_coils(self) -> float:
        """Number of the spring's total coils (Nt)"""

        return self.end_coils + self.active_coils

    @property
    def pitch(self) -> float:
        """The spring's pitch (the distance between the coils)"""
        options = {'plain': (self.free_length - self.wire_diameter) / self.active_coils,
                   'plain and ground': self.free_length / (self.active_coils + 1),
                   'squared or closed': ((self.free_length - 3 * self.wire_diameter) /
                                         self.active_coils),
                   'squared and ground': ((self.free_length - 2 * self.wire_diameter) /
                                          self.active_coils)}
        return options.get(self.end_type)

    @property
    def shear_yield_strength(self) -> float:
        """ The material shear yield strength (Ssy)
        (shear_yield_stress = % * ultimate_tensile_strength))"""
        try:
            return percent_to_decimal(self.shear_yield_percent) * self.ultimate_tensile_strength
        except TypeError:
            return self.shear_yield_percent * self.ultimate_tensile_strength

    @property
    def factor_Ks(self) -> float:  # pylint: disable=invalid-name
        """Static shear stress concentration factor"""
        return (2 * self.spring_index + 1) / (2 * self.spring_index)

    @property
    def factor_Kw(self) -> float:  # pylint: disable=invalid-name
        """Wahl shear stress concentration factor (K_W)"""
        return (4 * self.spring_index - 1) / (4 * self.spring_index - 4) + \
               (0.615 / self.spring_index)

    @property
    def factor_KB(self) -> float:  # pylint: disable=invalid-name
        """Bergstrasser shear stress concentration factor(K_B) (very close to factor_Kw)

        NOTE: included for the sake of completion NOT USED!!!
        """
        return (4 * self.spring_index + 2) / (4 * self.spring_index - 3)

    @property
    def max_shear_stress(self) -> float:
        """ Return's the maximum shear stress"""
        k_factor = self.factor_Ks if self.set_removed else self.factor_Kw
        return self.calc_shear_stress(self.max_force, k_factor)

    def calc_shear_stress(self, force, k_factor) -> float:
        """Calculates the shear stress based on the force applied.

        :param float force: Force in [N]
        :param float k_factor: The appropriate k factor for the calculation
        """
        return (k_factor * 8 * force * self.diameter) / (pi * self.wire_diameter ** 3)

    @property
    def max_deflection(self) -> float:
        """Returns the spring maximum deflection (It's change in length)"""
        return self.calc_deflection(self.max_force)

    def calc_deflection(self, force) -> float:
        """Calculate the spring's deflection (change in length) due to specific force.

        :param float force: Force in [N]
        """
        C = self.spring_index
        d = self.wire_diameter
        G = self.shear_modulus
        Na = self.active_coils
        return ((8 * force * C ** 3 * Na) / (G * d)) * ((1 + 2 * C ** 2) / (2 * C ** 2))

    @property
    def weight(self) -> float:
        """Return's the spring's weight according to it's specified density"""
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
        :param str criterion: fatigue criterion ('modified goodman', 'soderberg', 'gerber',
                                                 'asme-elliptic')
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

    def natural_frequency(self, density, working_frequency, verbose=True) -> dict[str:float] or None:
        """Figures out what is the natural frequency of the spring
        :param float density: Spring's material density
        :param float working_frequency: The expected frequency the spring is used for
        :param bool verbose: Print if spring frequency is not in range
        """
        d = self.wire_diameter
        D = self.diameter
        Na = self.active_coils
        G = self.shear_modulus

        omega = lambda alpha: ((d * 1e-3) / (alpha * pi * (D * 1e-3) ** 2 * Na)) * sqrt(G / (2 * density))
        results = {'fixed-fixed': omega(2), 'fixed-free': omega(4)}

        if verbose:
            if results['fixed-fixed'] > 20 * working_frequency:
                print(f"The spring's natural frequency for fixed ends is much grater than the "
                      f"working frequency \nwhich is good\n")
            else:
                print(f"Note: the natural frequency={results['fixed-fixed']:.2f} "
                      f"for fixed ends is not larger than 20*working frequency="
                      f"{20 * working_frequency:.2f} \nwhich means the spring can resonance\n")

            if results['fixed-free'] > 20 * working_frequency:
                print(f"The spring's natural frequency for one fixed and one free ends is much"
                      f"grater than the working frequency \nwhich is good\n")
            else:
                print(f"Note: the natural frequency={results['fixed-free']:.2f} "
                      f"for one fixed and one free ends is not larger than 20*working frequency="
                      f"{20 * working_frequency:.2f} \nwhich means the spring can resonance\n")

        return results

    @staticmethod
    def calc_spring_rate(wire_diameter, spring_diameter, shear_modulus, active_coils):
        """Calculate spring constant using the geometric properties

        :returns: The spring constant
        :rtype: float
        """
        d = wire_diameter
        D = spring_diameter
        G = shear_modulus
        C = D / d
        Na = active_coils
        return ((G * d) / (8 * C ** 3 * Na)) * ((2 * C ** 2) / (1 + 2 * C ** 2))
