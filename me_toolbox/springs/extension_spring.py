"""A module containing the extension spring class"""
from math import pi

from me_toolbox.fatigue import FailureCriteria
from me_toolbox.springs import HelicalCompressionSpring
from me_toolbox.tools import percent_to_decimal


class ExtensionSpring(HelicalCompressionSpring):
    """An extension spring object"""

    def __repr__(self):
        return f"ExtensionSpring(max_force={self.max_force}, " \
               f"initial_tension={self.initial_tension}, wire_diameter={self.wire_diameter}, " \
               f"spring_diameter={self.diameter}, hook_r1={self.hook_r1}, " \
               f"hook_r2={self.hook_r2}, " \
               f"ultimate_tensile_strength={self.ultimate_tensile_strength}, " \
               f"shear_modulus={self.shear_modulus}, elastic_modulus={self.elastic_modulus}, " \
               f"body_shear_yield_percent={self.body_shear_yield_percent}, " \
               f"hook_normal_yield_percent={self.hook_normal_yield_percent}, " \
               f"hook_shear_yield_percent={self.hook_normal_yield_percent}, " \
               f"spring_rate={self.spring_rate}, shot_peened={self.shot_peened}, " \
               f"density={self.density}, working_frequency={self.working_frequency})"

    def __str__(self):
        return f"ExtensionSpring(d={self.wire_diameter}, D={self.diameter}, " \
               f"k={self.spring_rate}, L={self.free_length})"

    def __init__(self, max_force, initial_tension, wire_diameter, spring_diameter, hook_r1, hook_r2,
                 ultimate_tensile_strength, body_shear_yield_percent, hook_normal_yield_percent,
                 hook_shear_yield_percent, shear_modulus, elastic_modulus,
                 spring_rate, shot_peened=False, density=None, working_frequency=None):
        """Instantiate an extension spring object with the given parameters

        :param float max_force: The maximum load on the spring [N]
        :param float initial_tension: The initial tension in the spring [N]
        :param float wire_diameter: spring wire diameter [mm]
        :param float spring_diameter: spring diameter measured from
            the center point of the wire diameter [mm]
        :param float hook_r1: hook internal radius [mm]
        :param float hook_r2: hook bend radius [mm]
        :param float ultimate_tensile_strength: Ultimate tensile strength of the material [Mpa]
        :param float body_shear_yield_percent: Used to estimate the spring's body shear yield stress
        :param float hook_normal_yield_percent: Used to estimate the spring's hook yield stress
        :param float hook_shear_yield_percent: Used to estimate the spring's hook shear yield stress
        :param float shear_modulus: Spring's material shear modulus [MPa]
        :param float elastic_modulus: Spring's material elastic modulus [MPa]
        :param float spring_rate: K - spring constant [N/mm]
        :param bool shot_peened: if True adds to fatigue strength
        :param float or None density: Spring's material density [kg/m^3]
            (used for buckling and weight calculations)
        :param float or None working_frequency: the spring working frequency [Hz]
            (used for fatigue calculations)

        :returns: HelicalCompressionSpring
        """

        super().__init__(max_force, wire_diameter, spring_diameter, ultimate_tensile_strength,
                         body_shear_yield_percent, shear_modulus, elastic_modulus, end_type='plain',
                         spring_rate=spring_rate, set_removed=False, shot_peened=shot_peened,
                         density=density, working_frequency=working_frequency,
                         anchors=None, zeta=0.15)

        self.initial_tension = initial_tension
        self.hook_r1 = hook_r1
        self.hook_r2 = hook_r2
        self.body_shear_yield_percent = body_shear_yield_percent
        self.hook_normal_yield_percent = hook_normal_yield_percent
        self.hook_shear_yield_percent = hook_shear_yield_percent

        self.check_design()

    def check_design(self):
        """Check if the spring index,active coils and natural frequency
         are in the acceptable range for good design.

        :returns: True if pass all checks
        :rtype: bool
        """
        good_design = all([self.__check_spring_index(), self.__check_active_coils()])

        natural_frequency_check = self.__check_natural_frequency()
        if natural_frequency_check is not None:
            good_design = natural_frequency_check

        return good_design

    def __check_spring_index(self) -> bool:
        in_range = True
        C = self.spring_index  # pylint: disable=invalid-name
        if isinstance(C, float) and not 3 <= C <= 16 and self.set_removed:
            print("Note: C - spring index should be in range of [3,16],"
                  "lower C causes surface cracks,\n"
                  "higher C causes the spring to tangle and requires separate packing")
            in_range = False
        return in_range

    @property
    def free_length(self) -> float:
        """The free length of the spring"""
        return 2 * (self.diameter - self.wire_diameter) + (self.body_coils + 1) * self.wire_diameter

    @property
    def solid_length(self):
        raise NotImplementedError("solid_length is inherited from HelicalCompressionSpring "
                                  "but has no use in ExtensionSpring")

    @property
    def Fsolid(self):
        raise NotImplementedError("Fsolid is inherited from HelicalCompressionSpring "
                                  "but has no use in ExtensionSpring")

    @property
    def body_coils(self) -> float:
        """Number of spring's coils"""
        return self.active_coils - (self.shear_modulus / self.elastic_modulus)

    @property
    def total_coils(self):
        raise NotImplementedError("total_coils is inherited from HelicalCompressionSpring "
                                  "but has no use in ExtensionSpring")

    @property
    def hook_normal_yield_strength(self) -> float:  # pylint: disable=invalid-name
        """Hook's yield strength (Sy = % * Sut)"""
        try:
            return (percent_to_decimal(self.hook_normal_yield_percent) *
                    self.ultimate_tensile_strength)
        except TypeError:
            return self.hook_normal_yield_percent * self.ultimate_tensile_strength

    @property
    def hook_shear_yield_strength(self) -> float:
        """Hook's yield strength (Ssy = % * Sut)"""
        try:
            return (percent_to_decimal(self.hook_shear_yield_percent) *
                    self.ultimate_tensile_strength)
        except TypeError:
            return self.hook_shear_yield_percent * self.ultimate_tensile_strength

    @property
    def hook_KA(self) -> float:  # pylint: disable=invalid-name
        """Hook's bending stress correction factor"""
        C1 = 2 * self.hook_r1 / self.wire_diameter  # pylint: disable=invalid-name
        return ((4 * C1 ** 2) - C1 - 1) / (4 * C1 * (C1 - 1))

    @property
    def hook_KB(self) -> float:
        """Hook's torsional stress correction factor"""
        C2 = 2 * self.hook_r2 / self.wire_diameter  # pylint: disable=invalid-name
        return (4 * C2 - 1) / (4 * C2 - 4)

    @property
    def max_hook_normal_stress(self) -> float:
        """Maximum normal stress due to bending and axial loads"""
        return self.calc_normal_stress(self.max_force)

    def calc_normal_stress(self, force):
        """Calculates the normal stress based on the force given.

        :param float force: Working max_force of the spring

        :returns: normal stress
        :rtype: float
        """
        return force * (self.hook_KA * (
                (16 * self.diameter) / (pi * self.wire_diameter ** 3)) + (
                                4 / (pi * self.wire_diameter ** 2)))

    @property
    def max_hook_shear_stress(self) -> float:
        """The spring's hook torsion stress"""
        return self.calc_shear_stress(self.max_force, self.hook_KB)

    @property
    def max_body_shear_stress(self) -> float:
        """The spring's body torsion stress"""
        # return self.calc_max_shear_stress(self.max_force, hook=False)
        return self.calc_shear_stress(self.max_force, self.factor_Kw)

    def calc_deflection(self, force):
        """Calculate the spring's deflection (change in length) due to the specified force.

        :param float force: Spring working force in [N]

        :returns: Spring deflection
        :rtype: float
        """
        return (force - self.initial_tension) / self.spring_rate

    def static_safety_factor(self, verbose=False):
        """ Returns the static safety factors for the hook (torsion and
        bending), and for the spring's body (torsion)

        :param bool verbose: More information

        :returns: Spring's body (torsion) safety factor, Spring's hook bending safety factor,
            Spring's hook torsion safety factor
        :type: dict{str: float}
        """
        if verbose:
            print(f"max body shear stress = {self.max_body_shear_stress:.2f}\n"
                  f"body Ssy = {self.shear_yield_strength:.2f}\n\n"
                  f"max hook normal stress = {self.max_hook_normal_stress:.2f}\n"
                  f"hook Sy = {self.hook_normal_yield_strength:.2f}\n\n"
                  f"max hook shear stress = {self.max_hook_shear_stress:.2f}\n"
                  f"hook Ssy = {self.hook_shear_yield_strength:.2f}\n")

        n_body = self.shear_yield_strength / self.max_body_shear_stress
        n_hook_normal = self.hook_normal_yield_strength / self.max_hook_normal_stress
        n_hook_shear = self.hook_shear_yield_strength / self.max_hook_shear_stress

        return {'n_body': n_body, 'n_hook_normal': n_hook_normal, 'n_hook_shear': n_hook_shear}

    def fatigue_analysis(self, max_force, min_force, reliability,
                         criterion='gerber', verbose=False, metric=True):
        """Fatigue analysis of the hook section, for normal and shear stress,and for the
        body section for shear and static yield.

        :param float max_force: Maximal max_force acting on the spring
        :param float min_force: Minimal max_force acting on the spring
        :param float reliability: in percentage
        :param str criterion: fatigue criterion ('modified goodman', 'soderberg', 'gerber',
                                                 'asme-elliptic')
        :param bool verbose: print more details
        :param bool metric: Metric or imperial

        :returns: Normal and shear safety factors for the hook section and
            static and dynamic safety factors for body section
        :rtype: dict[str, float]
        """
        # calculating mean and alternating forces
        alt_force = abs(max_force - min_force) / 2
        mean_force = (max_force + min_force) / 2

        # calculating mean and alternating stresses for the hook section
        # shear stresses:
        hook_alt_shear_stress = self.calc_shear_stress(alt_force, self.hook_KB)
        hook_mean_shear_stress = (mean_force / alt_force) * hook_alt_shear_stress
        # normal stresses due to bending:
        hook_alt_normal_stress = self.calc_normal_stress(alt_force)
        hook_mean_normal_stress = (mean_force / alt_force) * hook_alt_normal_stress

        Sse = self.shear_endurance_limit(reliability, metric)  # pylint: disable=invalid-name
        Ssu = self.shear_ultimate_strength
        Ssy_body = self.shear_yield_strength
        Ssy_hook = self.hook_shear_yield_strength
        Sy_hook = self.hook_normal_yield_strength
        Se = Sse / 0.577  # estimation using distortion-energy theory
        Sut = self.ultimate_tensile_strength

        try:
            nf_hook_normal, ns_hook_normal = \
                FailureCriteria.get_safety_factors(Sy_hook, Sut, Se, hook_alt_normal_stress,
                                                   hook_mean_normal_stress, criterion)

            nf_hook_shear, ns_hook_shear = \
                FailureCriteria.get_safety_factors(Ssy_hook, Ssu, Sse, hook_alt_shear_stress,
                                                   hook_mean_shear_stress, criterion)
        except TypeError as typ_err:
            raise ValueError(f"Fatigue analysis can't handle symbolic vars") from typ_err

        # calculating mean and alternating stresses for the body section
        # shear stresses:
        alt_body_shear_stress = self.calc_shear_stress(alt_force, self.hook_KB)
        mean_body_shear_stress = (mean_force / alt_force) * hook_alt_shear_stress

        nf_body, ns_body = FailureCriteria.get_safety_factors(Ssy_body, Ssu, Sse,
                                                              alt_body_shear_stress,
                                                              mean_body_shear_stress, criterion)

        if verbose:
            print(f"Alternating force = {alt_force:.2f}, "
                  f"Mean force = {mean_force:.2f}\n\n"
                  f"Body's alternating body shear stress = {alt_body_shear_stress:.2f}, "
                  f"Body's mean body shear stress = {mean_body_shear_stress:.2f}\n\n"
                  f"Hook's alternating shear stress = {hook_alt_shear_stress:.2f}, "
                  f"Hook's mean shear stress = {hook_mean_shear_stress:.2f}\n\n"
                  f"Hook's alternating normal stress = {hook_alt_normal_stress:.2f}, "
                  f"Hook's mean normal stress = {hook_mean_normal_stress:.2f}\n\n"
                  f"Sut = {Sut:.2f}, Sse = {Sse:.2f}, Se = {Se:.2f}, Ssu = {Ssu:.2f},\n"
                  f"Ssy_body = {Ssy_body:.2f}, Ssy_hook = {Ssy_hook:.2f}, "
                  f"Sy_hook = {Sy_hook:.2f}\n")

        return {'nf_body': nf_body, 'ns_body': ns_body, 'nf_hook_normal': nf_hook_normal,
                'ns_hook_normal': ns_hook_normal, 'nf_hook_shear': nf_hook_shear,
                'ns_hook_shear': ns_hook_shear}

    def buckling(self, anchors, verbose=True):
        raise NotImplementedError("Inherited from HelicalCompressionSpring but useless here")

    @staticmethod
    def calc_spring_rate(wire_diameter, spring_diameter, shear_modulus, active_coils):
        raise NotImplementedError("Didn't get to it yet")
