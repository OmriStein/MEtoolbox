"""A module containing the extension spring class"""
from math import pi
from sympy import Symbol  # pylint: disable=unused-import

from me_toolbox.fatigue import FailureCriteria
from me_toolbox.springs import Spring, HelicalPushSpring
from me_toolbox.tools import percent_to_decimal


class ExtensionSpring(Spring):
    """An extension spring object"""

    def __init__(self, max_force, initial_tension, wire_diameter, spring_diameter, Ap, m,
                 hook_r1, hook_r2, shear_modulus, elastic_modulus, body_shear_yield_percent,
                 end_normal_yield_percent, end_shear_yield_percent, spring_constant=None,
                 active_coils=None, shot_peened=False, body_coils=None, free_length=None,
                 density=None, working_frequency=None):
        """Instantiate an extension spring object with the given parameters

        :param float or Symbol max_force: The maximum load on the spring
        :param float or Symbol initial_tension: The initial tension in the spring
        :param float or Symbol wire_diameter: spring wire diameter
        :param float or Symbol spring_diameter: spring diameter measured from
            the center point of the wire diameter
        :param float Ap: A constant for Estimating Minimum Tensile Strength of Common Spring Wires
        :param float m: A Constants Estimating Minimum Tensile Strength of Common Spring Wires
        :param float hook_r1: hook internal radius
        :param float hook_r2: hook bend radius
        :param float shear_modulus: Spring's material shear modulus
        :param float elastic_modulus: Spring's material elastic modulus
        :param float body_shear_yield_percent: Used to estimate the spring's body shear yield stress
        :param float end_normal_yield_percent: Used to estimate the spring's hook yield stress
        :param float end_shear_yield_percent: Used to estimate the spring's hook shear yield stress
        :param float or None spring_constant: K - spring constant
        :param float or None active_coils: active_coils - number of active coils
        :param bool shot_peened: if True adds to fatigue strength
        :param float or None body_coils: Spring's number of body coils
        :param float or None free_length: the spring length when no force is applied
        :param float or None density: Spring's material density
            (used for buckling and weight calculations)
        :param float or None working_frequency: the spring working frequency
            (used for fatigue calculations)

        :returns: HelicalPushSpring

        """
        self.constructing = True
        super().__init__(max_force, Ap, m, body_shear_yield_percent, wire_diameter, spring_diameter,
                         shear_modulus, elastic_modulus, shot_peened, density, working_frequency)

        self.initial_tension = initial_tension
        self.hook_r1 = hook_r1
        self.hook_r2 = hook_r2
        self.end_normal_yield_percent = end_normal_yield_percent
        self.end_shear_yield_percent = end_shear_yield_percent

        self.shot_peened = shot_peened
        self._na_k_sorter(active_coils, body_coils, spring_constant)
        self.free_length = free_length
        self.check_design()
        self.constructing = False

    def check_design(self, verbose=False):
        """Check if the spring index,active_coils,zeta and free_length
        are in acceptable range for a good design

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
            natural_freq = self.natural_frequency(self.density)
            if natural_freq <= 20 * self.working_frequency:
                print(
                    f"Note: the natural frequency={natural_freq} is less than 20*working"
                    f"frequency={20 * self.working_frequency}")
                good_design = False
        if verbose:
            print(f"good_design = {good_design}")

        return good_design

    @property
    def end_normal_yield_strength(self):  # pylint: disable=invalid-name
        """getter for the yield strength attribute (Sy = % * Sut)

        :returns: end bending yield strength
        :rtype: float
        """
        return percent_to_decimal(self.end_normal_yield_percent) * self.ultimate_tensile_strength

    @property
    def end_shear_yield_strength(self):  # pylint: disable=invalid-name
        """getter for the yield strength attribute (Sy = % * Sut)

        :returns: end bending yield strength
        :rtype: float
        """
        return percent_to_decimal(self.end_shear_yield_percent) * self.ultimate_tensile_strength

    @property
    def wire_diameter(self):
        """Getter for the wire diameter attribute

        :returns: The spring's wire diameter
        :rtype: float or Symbol
        """
        return self._wire_diameter

    @wire_diameter.setter
    def wire_diameter(self, wire_diameter):
        """Sets the wire diameter and updates relevant attributes

        :param float wire_diameter: Spring's wire diameter
        """
        self._wire_diameter = wire_diameter
        if not self.constructing:
            # updating active_coils and free length with the new diameter
            self.active_coils = None
            self.spring_constant = None
            self.free_length = None

    @property
    def spring_diameter(self):
        """Getter for the spring diameter attribute

        :returns: The spring diameter
        :rtype: float or Symbol
        """
        return self._spring_diameter

    @spring_diameter.setter
    def spring_diameter(self, wire_diameter):
        """Sets the spring diameter and updates relevant attributes

        :param float wire_diameter: Spring's diameter
        """
        self._spring_diameter = wire_diameter
        if not self.constructing:
            # updating active_coils and free length with the new diameter
            self.active_coils = None
            self.spring_constant = None
            self.free_length = None

    @property
    def active_coils(self):
        """getter for the :attr:`active_coils` attribute

        :returns: The spring active coils
        :rtype: float
        """
        return self._active_coils

    @active_coils.setter
    def active_coils(self, active_coils):
        """getter for the :attr:`active_coils` attribute
        the method checks if active_coils was given and if not it
        calculates it form the other known parameters
        and then update the :attr:`spring_constant` attribute to match

        :param float or None active_coils: Spring active coils
        """
        if active_coils is not None:
            # active_coils was given
            self._active_coils = active_coils
            # recalculate spring constant and free_length according to the new active_coils
            self.spring_constant = None
            self.body_coils = None
            self.free_length = None
        else:
            # active_coils was not given so calculate it
            self._active_coils = self.calc_active_coils()

    def calc_active_coils(self):
        """Calculate Na which is the number of active coils
        (using Castigliano's theorem)

        :returns: number of active coils
        :rtype: float
        """
        if self.body_coils is None:
            active_coils = ((self.shear_modulus * self.wire_diameter) /
                            (8 * self.spring_index ** 3 * self.spring_constant)) * (
                                   (2 * self.spring_index ** 2) / (1 + 2 * self.spring_index ** 2))
        else:
            active_coils = self.body_coils + (self.shear_modulus / self.elastic_modulus)
        return active_coils

    @property
    def body_coils(self):
        """getter for the :attr:`body_coils` attribute

        :returns: The spring body coils
        :rtype: float
        """
        try:
            return self._body_coils
        except AttributeError:
            # if called before attribute was creates
            return None

    @body_coils.setter
    def body_coils(self, body_coils):
        """getter for the :attr:`body_coils` attribute
        the method checks if body_coils was given and if
        not it calculates it form the other known parameters

        :param float or None body_coils: Spring body coils
        """
        if body_coils is not None:
            # active_coils was given
            self._body_coils = body_coils
            # recalculate spring constant and free_length according to the new active_coils
            self.active_coils = None
            self.spring_constant = None
            self.free_length = None
        else:
            # active_coils was not given so calculate it
            self._body_coils = self.calc_body_coils()

    def calc_body_coils(self):
        """Calculate active_coils which is the number of active coils (using Castigliano's theorem)

        :returns: number of active coils
        :rtype: float
        """
        return self.active_coils - (self.shear_modulus / self.elastic_modulus)

    @body_coils.deleter
    def body_coils(self):
        print("deleter of body_coils called")
        del self._body_coils

    @property
    def spring_constant(self):
        """getter for the :attr:`spring_constant` attribute

        :returns: The spring constant
        :rtype: float
        """
        return self._spring_constant

    @spring_constant.setter
    def spring_constant(self, spring_constant):
        """getter for the :attr:`spring_constant` attribute
        the method checks if the spring constant was given and
        if not it calculates it form the other known parameters
        and then update the :attr:`active_coils` attribute to match

        :param float or None spring_constant: K - The spring constant
        """
        if spring_constant is not None:
            # spring_constant was given
            self._spring_constant = spring_constant
            # makes sure active_coils is calculated based on the new
            # spring constant and not on the last body_coils value
            del self.body_coils
            self.active_coils = None
            self.body_coils = None
            self.free_length = None
        else:
            # spring_constant was not given so calculate it
            self._spring_constant = self.calc_spring_constant()

    @property
    def hook_KA(self):  # pylint: disable=invalid-name
        """Returns The spring's bending stress correction factor

        :returns: Bending stress correction factor
        :rtype: float
        """
        C1 = 2 * self.hook_r1 / self.wire_diameter  # pylint: disable=invalid-name
        return ((4 * C1 ** 2) - C1 - 1) / (4 * C1 * (C1 - 1))

    @property
    def hook_KB(self):  # pylint: disable=invalid-name
        """Returns The spring's torsional stress correction factor

        :returns: Torsional stress correction factor
        :rtype: float or Symbol
        """

        C2 = 2 * self.hook_r2 / self.wire_diameter  # pylint: disable=invalid-name
        return (4 * C2 - 1) / (4 * C2 - 4)

    @property
    def max_hook_normal_stress(self):
        """The normal stress due to bending and axial loads

        :returns: Normal stress
        :rtype: float or Symbol
        """
        return self.calc_max_normal_stress(self.force)

    def calc_max_normal_stress(self, force):
        """Calculates the normal stress based on the force given

        :param float of Symbol force: Working force of the spring

        :returns: normal stress
        :rtype: float or Symbol
        """
        return force * (self.hook_KA * (
                (16 * self.spring_diameter) / (pi * self.wire_diameter ** 3)) + (
                                4 / (pi * self.wire_diameter ** 2)))

    @property
    def max_hook_shear_stress(self):
        """The spring's hook torsion stress

        :returns: Hook torsion stress
        :rtype: float
        """
        # return self.calc_max_shear_stress(self.force)
        return HelicalPushSpring.calc_max_shear_stress(self, self.force, self.hook_KB)

    @property
    def max_body_shear_stress(self):
        """The spring's body torsion stress

        :returns: Body torsion stress
        :rtype: float
        """
        # return self.calc_max_shear_stress(self.force, hook=False)
        return self.calc_max_shear_stress(self.force, self.factor_Kw)

    @property
    def free_length(self):
        """ getter for the :attr:`free_length` attribute

        :returns: free length of the springs
        :rtype: float
        """
        return self._free_length

    @free_length.setter
    def free_length(self, free_length):
        """free_length setter methods
        if free_length is specified assignee it and set the
        free_length_input_flag for the :attr:`Fsolid` method
        if free_length is not specified calculate it using :meth:`CalcL0`

        :param float or None free_length: The free length of the spring
        """
        # self.free_length_input_flag = False if free_length is None else True
        self._free_length = self.calc_free_length() if free_length is None else free_length

    def calc_free_length(self):
        """Calculates the free length of the spring

        :returns: free_length - The free length
        :rtype: float of Symbol
        """
        return 2 * (self.spring_diameter - self.wire_diameter) + (
                self.body_coils + 1) * self.wire_diameter

    def static_safety_factor(self):  # pylint: disable=unused-argument
        """ Returns the static safety factors for the hook (torsion and
        bending), and for the spring's body (torsion)

        :returns: Spring's body (torsion) safety factor, Spring's hook bending safety factor,
            Spring's hook torsion safety factor
        :type: tuple[float, float, float] or tuple[Symbol, Symbol, Symbol]
        """

        n_body = self.shear_yield_strength / self.max_body_shear_stress
        n_hook_normal = self.end_normal_yield_strength / self.max_hook_normal_stress
        n_hook_shear = self.end_shear_yield_strength / self.max_hook_shear_stress

        return n_body, n_hook_normal, n_hook_shear

    @property
    def deflection(self):
        """Returns the spring deflection, It's change in length

        :returns: Spring deflection
        :rtype: float or Symbol
        """
        return self.calc_deflection(self.force)

    def calc_deflection(self, force):
        """Calculate the spring deflection (change in length) due to a specific force

        :param float or Symbol force: Spring working force

        :returns: Spring deflection
        :rtype: float or Symbol
        """
        return (force - self.initial_tension) / self.spring_constant

    @property
    def factor_Kw(self):  # pylint: disable=invalid-name
        """K_W - Wahl shear stress concentration factor

        :returns: Wahl shear stress concentration factor
        :rtype: float
        """
        return (4 * self.spring_index - 1) / (4 * self.spring_index - 4) + \
               (0.615 / self.spring_index)

    def fatigue_analysis(self, max_force, min_force, reliability,
                         criterion='gerber', verbose=False):
        """Fatigue analysis of the hook section
        for normal and shear stress,and for the
        body section for shear and static yield.

        :param float max_force: Maximal force acting on the spring
        :param float min_force: Minimal force acting on the spring
        :param float reliability: in percentage
        :param str criterion: fatigue criterion
        :param bool verbose: print more details

        :returns: Normal and shear safety factors for the hook section and
            static and dynamic safety factors for body section
        :rtype: tuple[float, float, float, float]
        """
        # calculating mean and alternating forces
        alt_force = abs(max_force - min_force) / 2
        mean_force = (max_force + min_force) / 2

        # calculating mean and alternating stresses for the hook section
        # shear stresses:
        alt_shear_stress = self.calc_max_shear_stress(alt_force, self.hook_KB)
        mean_shear_stress = (mean_force / alt_force) * alt_shear_stress
        # normal stresses due to bending:
        alt_normal_stress = self.calc_max_normal_stress(alt_force)
        mean_normal_stress = (mean_force / alt_force) * alt_normal_stress

        Sse = self.shear_endurance_limit(reliability)  # pylint: disable=invalid-name
        Ssu = self.shear_ultimate_strength
        Ssy_body = self.shear_yield_strength
        Ssy_end = self.end_shear_yield_strength
        Sy_end = self.end_normal_yield_strength
        Se = Sse / 0.577  # estimation using distortion-energy theory
        Sut = self.ultimate_tensile_strength

        nf_hook_normal, _ = FailureCriteria.get_safety_factor(Sy_end, Sut, Se, alt_normal_stress,
                                                              mean_normal_stress, criterion)

        nf_hook_shear, _ = FailureCriteria.get_safety_factor(Ssy_end, Ssu, Sse, alt_shear_stress,
                                                             mean_shear_stress, criterion)

        # calculating mean and alternating stresses for the body section
        # shear stresses:
        alt_body_shear_stress = self.calc_max_shear_stress(alt_force, self.hook_KB)
        mean_body_shear_stress = (mean_force / alt_force) * alt_shear_stress

        nf_body, ns_body = FailureCriteria.get_safety_factor(Ssy_body, Ssu, Sse,
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

        return nf_body, ns_body, nf_hook_normal, nf_hook_shear

    def min_wire_diameter(self, static_safety_factor):
        """The minimal wire diameters (for shear and normal stresses)
        for a given safety factor in order to avoid failure,

        NOTE: Because KA and KB contains d no simple solution is available as in the
            HelicalPushSpring, so we assume an initial K and iterate until convergence,
            be aware that for some static_safety_factor a convergence my not occur.

        NOTE: for static use only

        :param float static_safety_factor: factor of safety

        :returns: The minimal wire diameter for shear and normal stresses
        :rtype: float or Symbol
        """
        factor_k, temp_k = 1.1, 0
        min_diam_shear = 0
        while abs(factor_k - temp_k) > 1e-3:
            diam = ((8 * factor_k * self.force * self.spring_index * static_safety_factor)
                    / (self.end_shear_yield_percent * self.Ap * pi)) ** (1 / (2 - self.m))
            if isinstance(diam, float):
                min_diam_shear = diam
            else:
                break
            temp_k = factor_k
            factor_k = (8 * self.hook_r2 - min_diam_shear) / (8 * self.hook_r2 - 4 * min_diam_shear)

        factor_k, temp_k = 1.1, 0
        min_diam_normal = 0
        while abs(factor_k - temp_k) > 1e-3:
            diam = ((factor_k * self.force * (
                    16 * self.spring_index + 4) * static_safety_factor) / (
                            self.end_normal_yield_percent * self.Ap * pi)) ** (
                           1 / (2 - self.m))
            if isinstance(diam, float):
                min_diam_normal = diam
            else:
                break
            temp_k = factor_k

            factor_k = (16 * self.hook_r1 ** 2 - 2 * self.hook_r1 * diam - diam ** 2) / (
                    16 * self.hook_r1 ** 2 - 8 * self.hook_r1 * diam)

            if isinstance(min_diam_shear, float) and isinstance(min_diam_normal, float):
                return max(min_diam_shear, min_diam_normal)
            else:
                return min_diam_shear, min_diam_normal

    def min_spring_diameter(self, static_safety_factor):
        """return the minimum spring diameter to avoid static failure
        according to the given safety factor.

        :param float static_safety_factor: factor of safety

        :returns: The minimal spring diameter
        :rtype: float or Symbol
        """
        # extracted from shear stress
        diameter_shear = (self.end_shear_yield_strength * pi * self.wire_diameter ** 3) / (
                self.hook_KB * 8 * self.force * static_safety_factor)
        # extracted from normal stress
        diameter_normal = (1 / (4 * self.hook_KA)) * \
                          (((self.end_normal_yield_strength * pi * self.wire_diameter ** 3) /
                            (4 * self.force * static_safety_factor)) - self.wire_diameter)
        return max(diameter_shear, diameter_normal)

    def _na_k_sorter(self, *args):
        """The active coils, body coils and the spring
        constant are linked this method is meant to
        determine the order of assignment and calculation
        based on the class input
        """
        active_coils = args[0]
        body_coils = args[1]
        spring_constant = args[2]

        if (active_coils is None) and (spring_constant is None) and (body_coils is None):
            # if None were given
            raise ValueError(
                "active_coils, body_coils and the spring_constant can't all be None,"
                "Tip: Find the spring constant")
        elif active_coils is None and spring_constant is not None and body_coils is None:
            # calculating active_coils based on the spring constant and
            # than body_coils based on active_coils
            # K -> active_coils -> body_coils
            self.spring_constant = spring_constant
            self.active_coils = active_coils
            self.body_coils = body_coils
        elif spring_constant is None and active_coils is not None and body_coils is None:
            # calculating the spring constant and body_coils based on active_coils
            # active_coils -> k, active_coils->body_coils
            self.active_coils = active_coils
            self.body_coils = body_coils
            self.spring_constant = spring_constant
        elif spring_constant is None and active_coils is None and body_coils is not None:
            # calculating active_coils based on body_coils and
            # than the spring constant based on active_coils
            # body_coils -> active_coils -> k
            self.body_coils = body_coils
            self.active_coils = active_coils
            self.spring_constant = spring_constant
        else:
            # if two or more are given raise error to prevent mistakes
            raise ValueError("active_coils, body_coils and/or the spring constant were"
                             "given but only one is expected")
