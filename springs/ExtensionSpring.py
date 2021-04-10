from math import pi
from springs import HelicalPushSpring
from tools import print_atributes
from sympy import Symbol


class ExtensionSpring(HelicalPushSpring):
    def __init__(self, max_force, initial_tension, wire_diameter, spring_diameter, Ap, m, hook_r1, hook_r2,
                 shear_modulus, elastic_modulus, yield_percent, bending_yield_percent,
                 spring_constant=None, active_coils=None, body_coils=None, free_length=None, density=None,
                 working_frequency=None):
        """Instantiate an extension spring object with the given parameters
        :param float hook_r1: hook internal radius
        :param float hook_r2: hook bend radius
        """
        self.initial_tension = initial_tension
        self.constructing = True
        super().__init__(max_force, Ap, m, yield_percent, wire_diameter, spring_diameter, shear_modulus, )
        self.r1 = hook_r1
        self.r2 = hook_r2
        self.elastic_modulus = elastic_modulus
        self.bending_yield_percent = bending_yield_percent
        self.density = density
        self.working_frequency = working_frequency

        self._na_k_sorter(active_coils, body_coils, spring_constant)

        self.free_length = free_length
        self.constructing = False

    def get_info(self):
        """print all of the spring properties"""
        print_atributes(self)

    @property
    def Sy(self):
        """ yield strength (Sy = % * ultimate_tensile_strength)) """
        if 1 <= self.bending_yield_percent <= 100:
            # if the yield_percent is in percentage form divide by 100
            return (self.bending_yield_percent / 100) * self.ultimate_tensile_strength
        elif 0 < self.bending_yield_percent < 1:
            # if the yield_percent is in decimal form no correction needed
            return self.bending_yield_percent * self.ultimate_tensile_strength
        else:
            raise ValueError("something is wrong with the bending yield percentage")

    @HelicalPushSpring.wire_diameter.setter
    def wire_diameter(self, d):
        """Sets the wire diameter and updates relevant attributes

        :param float d: Spring's wire diameter
        """
        self._wire_diameter = d
        if not self.constructing:
            # updating active_coils and free length with the new diameter
            self.active_coils = None
            self.spring_constant = None
            self.free_length = None

    @HelicalPushSpring.spring_diameter.setter
    def spring_diameter(self, d):
        """Sets the spring diameter and updates relevant attributes

        :param float d: Spring's diameter
        """
        self._spring_diameter = d
        if not self.constructing:
            # updating active_coils and free length with the new diameter
            self.active_coils = None
            self.spring_constant = None
            self.free_length = None

    @HelicalPushSpring.active_coils.setter
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
            self.body_coils = None
            self.free_length = None
        else:
            # active_coils was not given so calculate it
            self._Na = self.calc_Na()

    def calc_Na(self):
        """Calculate Na which is the number of active coils
        (using Castigliano's theorem)

        :returns: number of active coils
        :rtype: float
        """
        if self.body_coils is None:
            return ((self.shear_modulus * self.wire_diameter) / (8 * self.spring_index ** 3 * self.spring_constant)) * (
                    (2 * self.spring_index ** 2) / (1 + 2 * self.spring_index ** 2))
        else:
            return self.body_coils + (self.shear_modulus / self.elastic_modulus)

    @property
    def body_coils(self):
        """getter for the :attr:`body_coils` attribute

        :returns: The spring body coils
        :rtype: float
        """
        try:
            return self._Nb
        except AttributeError:
            # if called before attribute was creates
            return None

    @body_coils.setter
    def body_coils(self, body_coils):
        """getter for the :attr:`body_coils` attribute
        the method checks if body_coils was given and if not it calculates it form the other known parameters

        :param float or None body_coils: Spring body coils
        """
        if body_coils is not None:
            # active_coils was given
            self._Nb = body_coils
            # recalculate spring constant and free_length according to the new active_coils
            self.active_coils = None
            self.spring_constant = None
            self.free_length = None
        else:
            # active_coils was not given so calculate it
            self._Nb = self.calc_Nb()

    def calc_Nb(self):
        """Calculate active_coils which is the number of active coils (using Castigliano's theorem)

        :returns: number of active coils
        :rtype: float
        """
        return self.active_coils - (self.shear_modulus / self.elastic_modulus)

    @body_coils.deleter
    def body_coils(self):
        print("deleter of body_coils called")
        del self._Nb

    @HelicalPushSpring.spring_constant.setter
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
            del self.body_coils  # makes sure active_coils is calculated based on the new spring constant and not on the last body_coils value
            self.active_coils = None
            self.body_coils = None
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
    def KA(self):
        """Returns The spring's bending stress correction factor

        :returns: Bending stress correction factor
        :rtype: float
        """
        C1 = 2 * self.r1 / self.wire_diameter
        return ((4 * C1 ** 2) - C1 - 1) / (4 * C1 * (C1 - 1))

    @property
    def KB(self):
        """Returns The spring's torsional stress correction factor

        :returns: Torsional stress correction factor
        :rtype: float or Symbol
        """

        C2 = 2 * self.r2 / self.wire_diameter
        return (4 * C2 - 1) / (4 * C2 - 4)

    @property
    def normal_stress(self):
        """The normal stress due to bending and axial loads

        :returns: Normal stress
        :rtype: float or Symbol
        """
        return self.calc_normal_stress(self.force)

    def calc_normal_stress(self, force):
        """Calculates the normal stress based on the force given

        :param float of Symbol force: Working force of the spring

        :returns: normal stress
        :rtype: float or Symbol
        """
        return force * (self.KA * ((16 * self.spring_diameter) / (pi * self.wire_diameter ** 3)) + (
                4 / (pi * self.wire_diameter ** 2)))

    @property
    def shear_stress(self):
        """The spring's torsion stress

        :returns: Torsion stress
        :rtype: float
        """
        return self.calc_shear_stress(self.force)

    def calc_shear_stress(self, force):
        """Calculates the torsion stress based on the force given

        :param float of Symbol force: Working force of the spring

        :returns: Torsion stress
        :rtype: float or Symbol
        """
        return (self.KB * 8 * force * self.spring_diameter) / (pi * self.wire_diameter ** 3)

    @HelicalPushSpring.free_length.setter
    def free_length(self, L0):
        """free_length setter methods
        if L0 is specified assignee it and set the L0_input_flag for the :attr:`Fsolid` method
        if L0 is not specified calculate it using :meth:`CalcL0`

        :param float or None L0: The free length of the spring
        """
        # self.L0_input_flag = False if L0 is None else True
        self._free_length = self.calc_L0() if L0 is None else L0

    def calc_L0(self):
        """Calculates the free length of the spring

        :returns: L0 - The free length
        :rtype: float of Symbol
        """
        return 2 * (self.spring_diameter - self.wire_diameter) + (self.body_coils + 1) * self.wire_diameter

    def static_safety_factor(self, solid=False):
        """ Returns the static safety factors for torsion and for bending, according to the object attributes

        :returns: static factor of safety
        :type: tuple[float, float] or tuple[Symbol, Symbol]
        """
        return self.shear_yield_strength / self.shear_stress, self.Sy / self.normal_stress

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

    def fatigue_analysis(self, Fmax, Fmin, reliability, verbose=False):
        pass

    def shear_endurance_limit(self, reliability):
        pass

    def min_wire_diameter(self, static_safety_factor, solid=False):
        pass

    def min_spring_diameter(self, static_safety_factor, solid=False):
        pass

    def Fsolid(self):
        raise NotImplementedError

    def buckling(self, end, E):
        raise NotImplementedError

    def end_coils(self):
        raise NotImplementedError

    def solid_length(self):
        raise NotImplementedError

    def total_coils(self):
        raise NotImplementedError(f"For ExtensionSprings the body coils are the total coils")

    def _na_k_sorter(self, *args):
        """The active coils, body coils and the spring constant are linked this method is meant to
        determine the order of assignment and calculation based on the class input
        """
        active_coils = args[0]
        body_coils = args[1]
        spring_constant = args[2]
        # active_coils and the spring constant are linked this if statement is meant to determine which one to calculate
        # based on the class input
        if (active_coils is None) and (spring_constant is None) and (body_coils is None):
            # if None were given
            raise ValueError(
                "active_coils, body_coils and the spring_constant can't all be None, Tip: Find the spring constant")
        elif active_coils is None and spring_constant is not None and body_coils is None:
            # calculating active_coils based on the spring constant and than body_coils based on active_coils
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
            # calculating active_coils based on body_coils and than the spring constant based on active_coils
            # body_coils -> active_coils -> k
            self.body_coils = body_coils
            self.active_coils = active_coils
            self.spring_constant = spring_constant
        else:
            # if two or more are given raise error to prevent mistakes
            raise ValueError("active_coils, body_coils and/or the spring constant were given but only one is expected")

