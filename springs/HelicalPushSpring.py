from springs import Spring
from math import pi, sqrt
from tools import print_atributes
from tools import parse_input
from sympy import Symbol


class HelicalPushSpring(Spring):
    def __init__(self, max_force, Ap, m, yield_percent, wire_diameter, spring_diameter, shear_modulus,
                 end_type, spring_constant=None, active_coils=None, zeta=0.15, set_removed=False,
                 shot_peened=False, anchor=None, free_length=None, elastic_modulus=None, density=None,
                 working_frequency=None):
        """Instantiate a helical push spring object with the given parameters

        :param float or Symbol max_force: The maximum load on the spring
        :param float or Symbol wire_diameter: spring wire diameter
        :param float or Symbol spring_diameter: spring diameter measured from
            the center point of the wire diameter
        :param float Ap: Constants Ap of ultimate_tensile_strength = Ap/d**m for Estimating Minimum
            Tensile Strength of Common Spring Wires
        :param float m: Constants m of ultimate_tensile_strength = Ap/d**m for Estimating Minimum
            Tensile Strength of Common Spring Wires
        :param float shear_modulus: Shear modulus
        :param str end_type: what kind of ending the spring has
        :param float yield_percent: yield percent used to estimate shear_yield_stress
        :param float or None spring_constant: K - spring constant
        :param float or None active_coils: active_coils - number of active coils
        :param float zeta: overrun safety factor
        :param bool set_removed: if True adds to STATIC strength
            (must NOT use for fatigue application)
        :param bool shot_peened: if True adds to fatigue strength
        :param float or None free_length: the spring length when no force is applied
        :param str or None anchor: How the spring is anchored
            (used for buckling calculations)
        :param float or None elastic_modulus: elastic modulus
            (used for buckling calculations)
        :param float or None density: Spring's material density
            (used for buckling and weight calculations)
        :param float or None working_frequency: the spring working frequency
            (used for fatigue calculations)

        :returns: HelicalPushSpring
        """
        self.constructing = True  # a flag to tall methods that they are being called from within __init__
        super().__init__(max_force, Ap, m, yield_percent, wire_diameter, spring_diameter, shear_modulus)
        if set_removed:
            print(f"Note: set should ONLY be removed for static loading and NOT for periodical loading")

        self.set_removed = set_removed
        self.shot_peened = shot_peened
        self.yield_percent = yield_percent
        self.zeta = zeta  # overrun safety factor
        self.end_type = end_type.lower()

        self._na_k_sorter(active_coils, spring_constant)

        self.free_length = free_length

        end_types = ('plain', 'plain and ground', 'squared or closed', 'squared and ground')
        if self.end_type not in end_types:
            raise ValueError(f"{end_type} not one of this: {end_types}")

        self.anchor = anchor
        self.elastic_modulus = elastic_modulus
        self.density = density
        self.working_frequency = working_frequency

        self.check_design()  # check C and active_coils
        self.constructing = False

    def get_info(self):
        """print all of the spring properties"""
        print_atributes(self)
        self.check_design()  # check C and active_coils

    # TODO break CheckDesign to smaller pieces
    def check_design(self):
        """Check if the spring index,active_coils,zeta and L0 are in acceptable range for a good design

        :returns: True if all the checks are good
        :rtype: bool
        """
        good_design = True
        C = self.spring_index
        if isinstance(C, float) and not 4 <= C <= 12 and self.set_removed:
            print(f"Note: C - spring index should be in range of [4,12], lower C causes surface cracks,\n"
                  f"higher C causes the spring to tangle and requires separate packing")
            good_design = False
        elif isinstance(C, float) and not 3 <= C <= 12:
            print(f"Note: C - spring index should be in range of [3,12], lower C causes surface cracks,\n"
                  f"higher C causes the spring to tangle and requires separate packing")
            good_design = False

        Na = self.active_coils
        if isinstance(Na, float) and not 3 <= Na <= 15:
            print(f"Note: active_coils={Na:.2f} is not in range [3,15], this can cause non linear behavior")
            good_design = False

        if not self.L0_input_flag:
            print(f"Note: the free length was not given so Fsolid was estimated using zeta={self.zeta}")

        zeta = self.zeta
        if zeta < 0.15:
            print(f"Note: zeta={zeta:.2f} is smaller then 0.15, the spring could reach its solid length")
            good_design = False

        L0 = self.free_length
        if isinstance(L0, float) and (self.anchor is not None) and (self.elastic_modulus is not None):
            buckling = self.buckling(self.anchor, self.elastic_modulus)
            if buckling[0]:
                print(f"Note: buckling is accruing , max free length (L0) = {buckling[1]} , L0= {L0}")
                good_design = False

        if (self.density is not None) and (self.working_frequency is not None):
            Wn = self.natural_frequency(self.density)
            if Wn <= 20 * self.working_frequency:
                print(
                    f"Note: the natural frequency={Wn} is less than 20*working frequency={20 * self.working_frequency}")
                good_design = False

        return True if good_design else False

    @property
    def wire_diameter(self):
        """Getter for the wire diameter attribute

        :returns: The spring's wire diameter
        :rtype: float or Symbol
        """
        return self._wire_diameter

    @wire_diameter.setter
    def wire_diameter(self, d):
        """Sets the wire diameter and updates relevant attributes

        :param float d: Spring's wire diameter
        """
        self._wire_diameter = d
        if not self.constructing:
            # updating active_coils and free length with the new diameter
            self.active_coils = None
            self.free_length = None

    @property
    def spring_diameter(self):
        """Getter for the spring diameter attribute

        :returns: The spring diameter
        :rtype: float or Symbol
        """
        return self._spring_diameter

    @spring_diameter.setter
    def spring_diameter(self, d):
        """Sets the spring diameter and updates relevant attributes

        :param float d: Spring's diameter
        """
        self._spring_diameter = d
        if not self.constructing:
            # updating active_coils and free length with the new diameter
            self.active_coils = None
            self.free_length = None

    @property
    def spring_index(self):
        """C - spring index

        Note: C should be in range of [4,12], lower C causes surface cracks,
            higher C causes the spring to tangle and require separate packing

        :returns: The spring index
        :type: float or Symbol
        """
        return self.spring_diameter / self.wire_diameter

    @property
    def active_coils(self):
        """getter for the :attr:`active_coils` attribute

        :returns: The spring active coils
        :rtype: float
        """
        return self._Na

    @active_coils.setter
    def active_coils(self, active_coils):
        """getter for the :attr:`active_coils` attribute
        the method checks if active_coils was given and if not it calculates it form the other known parameters
        and then update the :attr:`spring_constant` attribute to match

        :param float or None active_coils: Spring active coils
        """
        if active_coils is not None:
            # active_coils was given
            self._Na = active_coils
            # recalculate spring constant and free_length according to the new active_coils
            self.spring_constant = None
            self.free_length = None
        else:
            # active_coils was not given so calculate it
            self._Na = self.calc_Na()

    def calc_Na(self):
        """Calculate active_coils which is the number of active coils (using Castigliano's theorem)

        :returns: number of active coils
        :rtype: float
        """
        return ((self.shear_modulus * self.wire_diameter) / (8 * self.spring_index ** 3 * self.spring_constant)) * (
                (2 * self.spring_index ** 2) / (1 + 2 * self.spring_index ** 2))

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
        the method checks if the spring constant was given and if not it calculates it form the other known parameters
        and then update the :attr:`active_coils` attribute to match

        :param float or None spring_constant: K - The spring constant
        """
        if spring_constant is not None:
            # spring_constant was given
            self._spring_constant = spring_constant
            # recalculate active_coils and the free length according to the new spring_constant
            self.active_coils = None
            self.free_length = None
        else:
            # spring_constant was not given so calculate it
            self._spring_constant = self.calc_spring_constant()

    def calc_spring_constant(self):
        """Calculate spring constant (using Castigliano's theorem)

        :returns: The spring constant
        :rtype: float
        """
        return ((self.shear_modulus * self.wire_diameter) / (8 * self.spring_index ** 3 * self.active_coils)) * (
                (2 * self.spring_index ** 2) / (1 + 2 * self.spring_index ** 2))

    @property
    def factor_Ks(self):
        """factor_Ks - Static shear stress concentration factor

        :returns: Static shear stress concentration factor
        :rtype: float
        """
        return (2 * self.spring_index + 1) / (2 * self.spring_index)

    @property
    def factor_Kw(self):
        """K_W - Wahl shear stress concentration factor

        :returns: Wahl shear stress concentration factor
        :rtype: float
        """
        return (4 * self.spring_index - 1) / (4 * self.spring_index - 4) + (0.615 / self.spring_index)

    @property
    def factor_KB(self):  # NOT IMPLEMENTED!!! TODO: check when to use and implement
        """K_B - Bergstrasser shear stress concentration factor (very close to factor_Kw)

        :returns: Bergstrasser shear stress concentration factor
        :rtype: float
        """
        return (4 * self.spring_index + 2) / (4 * self.spring_index - 3)

    @property
    def shear_stress(self):
        """ Return's the shear stress

        :returns: Shear stress
        :rtype: float
        """
        return self.calc_shear_stress(self.force)

    def calc_shear_stress(self, force):
        """Calculates the shear stress based on the force given

        :param float of Symbol force: Working force of the spring

        :returns: Shear stress
        :rtype: float or Symbol
        """
        K = self.factor_Ks if self.set_removed else self.factor_Kw
        return (K * 8 * force * self.spring_diameter) / (pi * self.wire_diameter ** 3)

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
        return ((8 * force * self.spring_index ** 3 * self.active_coils) / (
                self.shear_modulus * self.wire_diameter)) * (
                       (1 + 2 * self.spring_index ** 2) / (2 * self.spring_index ** 2))

    @property
    def end_coils(self):
        """Ne - the end coils of the spring

        :returns: Number of the spring end coils
        :rtype: float or Symbol
        """
        options = {'plain': 0, 'plain and ground': 1, 'squared or closed': 2, 'squared and ground': 2}
        return options.get(self.end_type)

    @property
    def total_coils(self):
        """Nt - the total coils of the spring

        :returns: Number of the spring total coils
        :rtype: float or Symbol
        """
        return self.end_coils + self.active_coils

    @property
    def solid_length(self):
        """Ls - the solid length of the spring
        (if the spring is fully compressed so the coils are touching each other)

        :returns: Spring solid length (when all the coils are touching)
        :rtype: float or Symbol
        """
        d = self.wire_diameter
        Nt = self.total_coils
        options = {'plain': d * (Nt + 1), 'plain and ground': d * Nt, 'squared or closed': d * (Nt + 1),
                   'squared and ground': d * Nt}
        return options.get(self.end_type)

    @property
    def Fsolid(self):
        """calculate the force necessary to bring the spring to solid length
        it is a good practice for the force that compresses the spring to solid state to be greater than the
        maximum force anticipated so we use this calculation: Fs=(1+zeta)Fmax in case the free length is unknown

        Note: zeta is the overrun safety factor, it's customary that zeta=0.15 so Fs=1.15Fmax

        :returns: The force it takes to get the spring to solid length
        :rtype: float
        """
        if self.L0_input_flag:
            # if L0 is given
            return self.spring_constant * (self.free_length - self.solid_length)
        else:
            # if L0 is unknown make an estimation
            return (1 + self.zeta) * self.force

    @property
    def free_length(self):
        """ getter for the :attr:`free_length` attribute

        :returns: free length of the springs
        :rtype: float
        """
        return self._free_length

    @free_length.setter
    def free_length(self, L0):
        """free_length setter methods
        if L0 is specified assignee it and set the L0_input_flag for the :attr:`Fsolid` method
        if L0 is not specified calculate it using :meth:`CalcL0`

        :param float or None L0: The free length of the spring
        """
        self.L0_input_flag = False if L0 is None else True
        self._free_length = self.calc_L0() if L0 is None else L0

    def calc_L0(self):
        """Calculates the free length of the spring"""
        return (self.Fsolid / self.spring_constant) + self.solid_length

    def static_safety_factor(self, solid=False):
        """ Returns the static safety factor according to the object attributes

        :returns: static factor of safety
        :type: float or Symbol
        """
        shear_stress = self.calc_shear_stress(self.Fsolid) if solid else self.shear_stress
        return self.shear_yield_strength / shear_stress

    def weight(self, density):
        """Return's the spring *active coils* weight according to the specified density

        :param float density: The material density

        :returns: Spring weight
        :type: float or Symbol
        """
        area = 0.25 * pi * self.wire_diameter ** 2  # cross section area
        length = pi * self.spring_diameter  # the circumference of the spring
        volume = area*length
        return volume*self.active_coils*self.density

    def min_wire_diameter(self, static_safety_factor, solid=False):
        """The minimal wire diameter for a given safety factor in order to avoid failure,
        according to the spring parameters, if solid is True the calculation uses :attr:`Fsolid`
        instead of :attr:`force`

        Note: for static use only

        :param float static_safety_factor: factor of safety
        :param bool solid: If true calculate to according to the solid force

        :returns: The minimal wire diameter
        :rtype: float or Symbol
        """
        K = self.factor_Ks if self.set_removed else self.factor_Kw
        force = self.Fsolid if solid else self.force
        return ((8 * K * force * self.spring_index * static_safety_factor) / (
                self.yield_percent * self.Ap * pi)) ** (1 / (2 - self.m))

    def min_spring_diameter(self, static_safety_factor, solid=False):
        """return the minimum spring diameter to avoid static failure
        according to the specified safety factor, if the solid flag is True :attr:'Fsolid'
        is used instead of :attr:`force`

        :param float static_safety_factor: factor of safety
        :param bool solid: If true calculate to according to the solid force

        :returns: The minimal spring diameter
        :rtype: float or Symbol
        """
        force = self.Fsolid if solid else self.force
        if self.set_removed:
            return 0.5 * ((self.shear_yield_strength / static_safety_factor) * (
                    (pi * self.wire_diameter ** 3) / (4 * force)) - self.wire_diameter)
        else:
            # TODO: add a solution for factor_Kw (before set removed)
            print("MinSpringDiameter Not valid if set not removed")

    def buckling(self, ends, E):
        """ Checks if the spring will buckle and find the maximum free length to avoid buckling

        :param float E: elastic modulus
        :param str ends: the spring end condition (from Table 10-2)

        :returns: True if spring is in danger of collapse and False if not,
            and the maximum free length(L0) to avoid collapsing
        :rtype: tuple[bool, float]
        """
        alpha = {'fixed-fixed': 0.5, 'fixed-hinged': 0.707, 'hinged-hinged': 1, 'clamped-free': 2}  # from table 10-2

        L0 = self.free_length
        try:
            collapse_test = (pi * self.spring_diameter / alpha[ends.lower()]) * sqrt(
                (2 * (E - self.shear_modulus)) / (2 * self.shear_modulus + E))
        except ValueError as e:
            print(f"{e}, make sure E and G have the same units (Mpa)")
        except KeyError as key:
            print(f"Ends: {key} is unknown ")
        else:
            return L0 >= collapse_test, collapse_test

    def shear_endurance_limit(self, reliability):
        """Sse - Shear endurance limit according to Zimmerli

        :param float reliability: reliability in percentage

        :returns: Sse - Shear endurance limit
        :rtype: float
        """
        import numpy as np
        # data from table
        percentage = np.array([50, 90, 95, 99, 99.9, 99.99, 99.999, 99.9999])
        reliability_factors = np.array([1, 0.897, 0.868, 0.814, 0.753, 0.702, 0.659, 0.620])
        # interpolating from data
        Ke = np.interp(reliability, percentage, reliability_factors)

        if self.shot_peened:
            Ssa, Ssm = 398, 534
        else:
            Ssa, Ssm = 241, 379

        return Ke * (Ssa / (1 - (Ssm / self.shear_ultimate_strength) ** 2))

    def fatigue_analysis(self, Fmax, Fmin, reliability, verbose=False):
        """ Returns safety factors for fatigue according to Goodman and for first circle according to Langer

        :param float Fmax: Maximal force acting on the spring
        :param float Fmin: Minimal force acting on the spring
        :param float reliability: in percentage
        :param bool verbose: print more details

        :returns: static and dynamic safety factor
        :rtype: tuple[float, float]
        """
        # calculating mean and alternating forces
        alternating_force = abs(Fmax - Fmin) / 2
        mean_force = (Fmax + Fmin) / 2

        # calculating mean and alternating stresses
        alternating_shear_stress = self.calc_shear_stress(alternating_force)
        mean_shear_stress = self.calc_shear_stress(mean_force)

        # nf - goodman fatigue safety factor
        Sse = self.shear_endurance_limit(reliability)
        nf = 1 / ((alternating_shear_stress / Sse) + (mean_shear_stress / self.shear_ultimate_strength))
        # ns - langer safety factor for first cycle
        ns = self.shear_yield_strength / (mean_shear_stress + alternating_shear_stress)
        if verbose:
            print(f"Alternating force = {alternating_force}, Mean force = {mean_force}\n"
                  f"Alternating shear stress = {alternating_shear_stress}, Mean shear stress = {mean_shear_stress}\n"
                  f"Sse = {Sse}")
        return nf, ns

    def natural_frequency(self, density):
        """Figures out what is the natural frequency of the spring

        :param float density: spring material density

        :returns: Natural frequency
        :rtype: float
        """
        return (self.wire_diameter / (2 * self.spring_diameter ** 2 * self.active_coils * pi)) * sqrt(
            self.shear_modulus / (2 * density))

    def calc_spring_index(self, solid_safety_factor):
        """Calculate Spring index for a certain safety factor if only wire diameter was given
        but the spring diameter was not (from Shigley's)

        :param float solid_safety_factor: Spring's safety factor for solid length

        :returns: Spring's index number
        """
        alpha = self.shear_yield_strength / solid_safety_factor
        beta = (8 * self.Fsolid) / (pi * self.wire_diameter ** 2)
        if self.set_removed:
            # for factor_Ks
            return (alpha / beta) + 0.5
        else:
            # for factor_Kw
            try:
                return (alpha - 0.365 * beta) / (2 * beta) + (
                    (0.966 * sqrt(0.268 * alpha ** 2 - alpha * beta + 0.53 * beta ** 2))) / beta
            except TypeError:
                print("In this method d can't be symbolic")
            # for Kb TODO: find a way to implement Kb (Bergstrasser factor)
            # return ((2 * alpha - beta) / (4 * beta)) + sympy.sqrt(
            #     ((2 * alpha - beta) / (4 * beta)) ** 2 - ((3 * alpha) / (4 * beta)))

    def _na_k_sorter(self, *args):
        """The active coils and the spring constant are linked this method is meant to
        determine the order of assignment and calculate based on the class input
        """
        active_coils = args[0]
        spring_constant = args[1]
        if (active_coils is None) and (spring_constant is None):
            # if None were given
            raise ValueError("active_coils and the spring_constant can't both be None, Tip: Find the spring constant")
        elif active_coils is None:
            # calculating active_coils based on the spring constant
            self.spring_constant = spring_constant
            self.active_coils = active_coils
        elif spring_constant is None:
            # calculating the spring constant based on active_coils
            self.active_coils = active_coils
            self.spring_constant = spring_constant
        else:
            # if both are given
            raise ValueError("Both active_coils and the spring constant were given but only one is expected")
