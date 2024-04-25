"""A module containing the extension spring class"""
from math import pi

from me_toolbox.fatigue import FailureCriteria
from me_toolbox.springs import HelicalCompressionSpring
from me_toolbox.tools import percent_to_decimal


class ExtensionSpring(HelicalCompressionSpring):
    """An extension spring object"""

    def __init__(self, max_force, initial_tension, wire_diameter, spring_diameter, hook_r1, hook_r2,
                 ultimate_tensile_strength, shear_modulus, elastic_modulus,
                 body_shear_yield_percent, hook_normal_yield_percent, hook_shear_yield_percent,
                 spring_rate, shot_peened=False, density=None, working_frequency=None,
                 anchors=None):
        """Instantiate an extension spring object with the given parameters

        :param float max_force: The maximum load on the spring
        :param float initial_tension: The initial tension in the spring
        :param float wire_diameter: spring wire diameter
        :param float spring_diameter: spring diameter measured from
            the center point of the wire diameter
        # :param float Ap: A constant for Estimating Minimum Tensile Strength of Common Spring Wires
        # :param float m: A Constants Estimating Minimum Tensile Strength of Common Spring Wires
        :param float ultimate_tensile_strength: Ultimate tensile strength of the material
        :param float hook_r1: hook internal radius
        :param float hook_r2: hook bend radius
        :param float shear_modulus: Spring's material shear modulus
        :param float elastic_modulus: Spring's material elastic modulus
        :param float body_shear_yield_percent: Used to estimate the spring's body shear yield stress
        :param float hook_normal_yield_percent: Used to estimate the spring's hook yield stress
        :param float hook_shear_yield_percent: Used to estimate the spring's hook shear yield stress
        :param float or None spring_rate: K - spring constant
        :param bool shot_peened: if True adds to fatigue strength
        :param float or None density: Spring's material density
            (used for buckling and weight calculations)
        :param float or None working_frequency: the spring working frequency
            (used for fatigue calculations)

        :returns: HelicalCompressionSpring
        """

        super().__init__(max_force, wire_diameter, spring_diameter, ultimate_tensile_strength,
                         body_shear_yield_percent, shear_modulus, elastic_modulus, end_type='plain',
                         spring_rate=spring_rate, set_removed=False, shot_peened=shot_peened,
                         density=density, working_frequency=working_frequency,
                         anchors=anchors, zeta=0.15)

        self.initial_tension = initial_tension
        self.hook_r1 = hook_r1
        self.hook_r2 = hook_r2
        self.body_shear_yield_percent = body_shear_yield_percent
        self.hook_normal_yield_percent = hook_normal_yield_percent
        self.hook_shear_yield_percent = hook_shear_yield_percent

        # self.check_design()

    def check_design(self, verbose=False):
        """Check if the spring index,active_coils,zeta and free_length
        are in acceptable range for good design

        :returns: True if all the checks are good
        :rtype: bool
        """
        good_design = True
        C = self.spring_index  # pylint: disable=invalid-name
        if isinstance(C, float) and not 3 <= C <= 16:
            print("Note: C - spring index should be in range of [3,16],"
                  "lower C causes surface cracks,\n"
                  "higher C causes the spring to tangle and requires separate packing")
            good_design = False

        active_coils = self.active_coils
        if isinstance(active_coils, float) and not 3 <= active_coils <= 15:
            print(f"Note: active_coils={active_coils:.2f} is not in range [3,15],"
                  f"this can cause non linear behavior")
            good_design = False

        if (self.density is not None) and (self.working_frequency is not None):
            natural_freq = self.natural_frequency
            if natural_freq <= 20 * self.working_frequency:
                print(
                    f"Note: the natural frequency={natural_freq} is less than 20*working"
                    f"frequency={20 * self.working_frequency}")
                good_design = False
        if verbose:
            print(f"good_design = {good_design}")

        return good_design

    @property
    def free_length(self):
        """Calculates the free length of the spring

        :returns: free_length - The free length
        :rtype: float
        """
        return 2 * (self.diameter - self.wire_diameter) + (
                self.body_coils + 1) * self.wire_diameter

    @property
    def solid_length(self):
        raise NotImplementedError("solid_length is inherited from HelicalCompressionSpring "
                                  "but has no use in ExtensionSpring")

    @property
    def Fsolid(self):
        raise NotImplementedError("Fsolid is inherited from HelicalCompressionSpring "
                                  "but has no use in ExtensionSpring")

    @property
    def body_coils(self):
        """Calculate active_coils which is the number of active coils (using Castigliano's theorem)

        :returns: number of active coils
        :rtype: float
        """
        return self.active_coils - (self.shear_modulus / self.elastic_modulus)

    @property
    def hook_normal_yield_strength(self):  # pylint: disable=invalid-name
        """getter for the yield strength attribute (Sy = % * Sut)

        :returns: hook bending yield strength
        :rtype: float
        """
        try:
            return (percent_to_decimal(self.hook_normal_yield_percent) *
                    self.ultimate_tensile_strength)
        except TypeError:
            return self.hook_normal_yield_percent * self.ultimate_tensile_strength

    @property
    def hook_shear_yield_strength(self):
        """getter for the yield strength attribute (Sy = % * Sut)

        :returns: hook bending yield strength
        :rtype: float
        """
        try:
            return (percent_to_decimal(self.hook_shear_yield_percent) *
                    self.ultimate_tensile_strength)
        except TypeError:
            return self.hook_shear_yield_percent * self.ultimate_tensile_strength

    @property
    def hook_KA(self):  # pylint: disable=invalid-name
        """Returns The spring's bending stress correction factor

        :returns: Bending stress correction factor
        :rtype: float
        """
        C1 = 2 * self.hook_r1 / self.wire_diameter  # pylint: disable=invalid-name
        return ((4 * C1 ** 2) - C1 - 1) / (4 * C1 * (C1 - 1))

    @property
    def hook_KB(self):
        """Returns The spring's torsional stress correction factor

        :returns: Torsional stress correction factor
        :rtype: float
        """

        C2 = 2 * self.hook_r2 / self.wire_diameter  # pylint: disable=invalid-name
        return (4 * C2 - 1) / (4 * C2 - 4)

    @property
    def max_hook_normal_stress(self):
        """The normal stress due to bending and axial loads

        :returns: Normal stress
        :rtype: float
        """
        return self.calc_normal_stress(self.max_force)

    def calc_normal_stress(self, force):
        """Calculates the normal stress based on the max_force given

        :param float force: Working max_force of the spring

        :returns: normal stress
        :rtype: float
        """
        return force * (self.hook_KA * (
                (16 * self.diameter) / (pi * self.wire_diameter ** 3)) + (
                                4 / (pi * self.wire_diameter ** 2)))

    @property
    def max_hook_shear_stress(self):
        """The spring's hook torsion stress

        :returns: Hook torsion stress
        :rtype: float
        """
        return self.calc_shear_stress(self.max_force, self.hook_KB)

    @property
    def max_body_shear_stress(self):
        """The spring's body torsion stress

        :returns: Body torsion stress
        :rtype: float
        """
        # return self.calc_max_shear_stress(self.max_force, hook=False)
        return self.calc_shear_stress(self.max_force, self.factor_Kw)

    @property
    def natural_frequency(self):
        raise NotImplementedError("Need to adapt the formula to extension spring")

    def calc_deflection(self, force):
        """Calculate the spring max_deflection (change in length) due to specific max_force
        :param float force: Spring working max_force

        :returns: Spring max_deflection
        :rtype: float
        """
        return (force - self.initial_tension) / self.spring_rate

    def static_safety_factor(self):
        """ Returns the static safety factors for the hook (torsion and
        bending), and for the spring's body (torsion)

        :returns: Spring's body (torsion) safety factor, Spring's hook bending safety factor,
            Spring's hook torsion safety factor
        :type: dict{str: float}
        """

        n_body = self.shear_yield_strength / self.max_body_shear_stress
        n_hook_normal = self.hook_normal_yield_strength / self.max_hook_normal_stress
        n_hook_shear = self.hook_shear_yield_strength / self.max_hook_shear_stress

        return {'n_body': n_body, 'n_hook_normal': n_hook_normal, 'n_hook_shear': n_hook_shear}

    def fatigue_analysis(self, max_force, min_force, reliability,
                         criterion='gerber', verbose=False, metric=True):
        """Fatigue analysis of the hook section
        for normal and shear stress,and for the
        body section for shear and static yield.
        :param float max_force: Maximal max_force acting on the spring
        :param float min_force: Minimal max_force acting on the spring
        :param float reliability: in percentage
        :param str criterion: fatigue criterion
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
        alt_shear_stress = self.calc_shear_stress(alt_force, self.hook_KB)
        mean_shear_stress = (mean_force / alt_force) * alt_shear_stress
        # normal stresses due to bending:
        alt_normal_stress = self.calc_normal_stress(alt_force)
        mean_normal_stress = (mean_force / alt_force) * alt_normal_stress

        Sse = self.shear_endurance_limit(reliability, metric)  # pylint: disable=invalid-name
        Ssu = self.shear_ultimate_strength
        Ssy_body = self.shear_yield_strength
        Ssy_hook = self.hook_shear_yield_strength
        Sy_hook = self.hook_normal_yield_strength
        Se = Sse / 0.577  # estimation using distortion-energy theory
        Sut = self.ultimate_tensile_strength

        try:
            nf_hook_normal, _ = FailureCriteria.get_safety_factors(Sy_hook, Sut, Se,
                                                                   alt_normal_stress,
                                                                   mean_normal_stress, criterion)

            nf_hook_shear, _ = FailureCriteria.get_safety_factors(Ssy_hook, Ssu, Sse,
                                                                  alt_shear_stress,
                                                                  mean_shear_stress, criterion)
        except TypeError as typ_err:
            raise ValueError(f"Fatigue analysis can't handle symbolic vars") from typ_err

        # calculating mean and alternating stresses for the body section
        # shear stresses:
        alt_body_shear_stress = self.calc_shear_stress(alt_force, self.hook_KB)
        mean_body_shear_stress = (mean_force / alt_force) * alt_shear_stress

        nf_body, ns_body = FailureCriteria.get_safety_factors(Ssy_body, Ssu, Sse,
                                                              alt_body_shear_stress,
                                                              mean_body_shear_stress, criterion)

        if verbose:
            print(f"Alternating force = {alt_force}, Mean force = {mean_force}\n"
                  f"Alternating shear stress = {alt_shear_stress},"
                  f"Mean shear stress = {mean_shear_stress}\n"
                  f"Alternating normal stress = {alt_normal_stress},"
                  f"Mean normal stress = {mean_normal_stress}\n"
                  f"Alternating body shear stress = {alt_body_shear_stress},"
                  f"Mean body shear stress = {mean_body_shear_stress}\n"
                  f"Sse = {Sse}, Se = {Se}")

        return {'nf_body':nf_body, 'ns_body':ns_body, 'nf_hook_normal':nf_hook_normal,
                'nf_hook_shear':nf_hook_shear}

    def min_wire_diameter(self, Ap, m, safety_factor, spring_index=None):
        """The minimal wire diameters (for shear and normal stresses)
        for given safety factor in order to avoid failure,

        Because KA and KB contains d no simple solution is available as in the
        HelicalCompressionSpring, so we assume an initial K and iterate until convergence,
        be aware that for some static_safety_factor convergence my not occur.

        NOTE: for static use only
        :param float safety_factor: Static safety factor
        :param float spring_index: Spring index

        :returns: The minimal wire diameter
        :rtype: tuple(float, float)
        """
        F = self.max_force
        C = spring_index

        factor_k, temp_k = 1.1, 0
        normal_diam = 0
        while abs(factor_k - temp_k) > 1e-4:
            # waiting for k to converge
            percent = self.hook_normal_yield_percent
            normal_diam = (safety_factor * F * (16 * factor_k * C - 4) / (percent * Ap * pi)) ** (
                    1 / (2 - m))
            temp_k = factor_k
            factor_k = ((16 * self.hook_r1 ** 2 - 2 * self.hook_r1 * normal_diam - normal_diam ** 2)
                        / (16 * self.hook_r1 ** 2 - 8 * self.hook_r1 * normal_diam))

        factor_k, temp_k = 1.1, 0
        shear_diam = 0
        while abs(factor_k - temp_k) > 1e-4:
            # waiting for k to converge
            percent = self.hook_shear_yield_percent
            shear_diam = ((8 * factor_k * F * C * safety_factor) / (percent * Ap * pi)) ** (
                    1 / (2 - m))
            temp_k = factor_k
            factor_k = (8 * self.hook_r2 - shear_diam) / (8 * self.hook_r2 - 4 * shear_diam)

        try:
            return max(normal_diam, shear_diam)
        except TypeError:
            return normal_diam, shear_diam

    def min_spring_diameter(self, static_safety_factor):
        """return the minimum spring diameter to avoid static failure
        according to the given safety factor.
        :param float static_safety_factor: factor of safety

        :returns: The minimal spring diameter
        :rtype: float
        """
        # extracted from shear stress
        diameter_shear = (self.hook_shear_yield_strength * pi * self.wire_diameter ** 3) / (
                self.hook_KB * 8 * self.max_force * static_safety_factor)
        # extracted from normal stress
        diameter_normal = (1 / (4 * self.hook_KA)) * \
                          (((self.hook_normal_yield_strength * pi * self.wire_diameter ** 3) /
                            (4 * self.max_force * static_safety_factor)) - self.wire_diameter)
        try:
            return max(diameter_shear, diameter_normal)
        except TypeError:
            return diameter_shear, diameter_normal

    def buckling(self, anchors, verbose=True):
        raise NotImplementedError("Inherited from HelicalCompressionSpring but useless here")

    @staticmethod
    def calc_spring_rate(wire_diameter, spring_diameter, shear_modulus, active_coils):
        raise NotImplementedError("Didn't get to it yet")
