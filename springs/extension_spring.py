"""A module containing the extension spring class"""
from math import pi
from sympy import Symbol  # pylint: disable=unused-import
from tools import print_atributes
import springs


class ExtensionSpring(springs.Spring):
    """An extension spring object"""

    def __init__(self, max_force, initial_tension, wire_diameter, spring_diameter,
                 Ap, m, hook_r1, hook_r2, shear_modulus, elastic_modulus, yield_percent,
                 bending_yield_percent, spring_constant=None, active_coils=None, shot_peened=False,
                 body_coils=None, free_length=None, density=None, working_frequency=None):
        """Instantiate an extension spring object with the given parameters
        :param float hook_r1: hook internal radius
        :param float hook_r2: hook bend radius
        """
        self.constructing = True
        super().__init__(max_force, Ap, m, yield_percent, wire_diameter, spring_diameter,
                         shear_modulus, shot_peened)

        self.initial_tension = initial_tension
        self.hook_r1 = hook_r1
        self.hook_r2 = hook_r2
        self.bending_yield_percent = bending_yield_percent
        self.elastic_modulus = elastic_modulus
        self.density = density
        self.working_frequency = working_frequency
        self.shot_peened = shot_peened
        self._na_k_sorter(active_coils, body_coils, spring_constant)
        self.free_length = free_length

        self.constructing = False

    def get_info(self):
        """print all of the spring properties"""
        print_atributes(self)

    @property
    def Sy(self):  # pylint: disable=invalid-name
        """ yield strength (Sy = % * ultimate_tensile_strength)) """
        if 1 <= self.bending_yield_percent <= 100:
            # if the yield_percent is in percentage form divide by 100
            yield_strength = (self.bending_yield_percent / 100) * self.ultimate_tensile_strength
        elif 0 < self.bending_yield_percent < 1:
            # if the yield_percent is in decimal form no correction needed
            yield_strength = self.bending_yield_percent * self.ultimate_tensile_strength
        else:
            raise ValueError("something is wrong with the bending yield percentage")
        return yield_strength

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

    def calc_spring_constant(self):
        """Calculate spring constant (using Castigliano's theorem)

        :returns: The spring constant
        :rtype: float
        """
        return ((self.shear_modulus * self.wire_diameter) /
                (8 * self.spring_index ** 3 * self.active_coils)) * (
                       (2 * self.spring_index ** 2) / (1 + 2 * self.spring_index ** 2))

    @property
    def KA(self):  # pylint: disable=invalid-name
        """Returns The spring's bending stress correction factor

        :returns: Bending stress correction factor
        :rtype: float
        """
        C1 = 2 * self.hook_r1 / self.wire_diameter  # pylint: disable=invalid-name
        return ((4 * C1 ** 2) - C1 - 1) / (4 * C1 * (C1 - 1))

    @property
    def KB(self):  # pylint: disable=invalid-name
        """Returns The spring's torsional stress correction factor

        :returns: Torsional stress correction factor
        :rtype: float or Symbol
        """

        C2 = 2 * self.hook_r2 / self.wire_diameter  # pylint: disable=invalid-name
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
        """ Returns the static safety factors for torsion and
        for bending, according to the object attributes

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

    def fatigue_analysis(self, max_force, min_force, reliability, verbose=False):
        """place holder"""
        raise NotImplementedError("Not implemented yet")  # TODO: implement

    def min_wire_diameter(self, static_safety_factor):
        """The minimal wire diameters (for shear and normal stresses)
        for a given safety factor in order to avoid failure,
        according to the spring parameters

        Note: for static use only

        :param float static_safety_factor: factor of safety

        :returns: The minimal wire diameter for shear and normal stresses
        :rtype: float or Symbol
        """
        factor_k, temp_k = 1.1, 0
        while abs(factor_k - temp_k) > 1e-3:
            diam = ((8 * factor_k * self.force * self.spring_index * static_safety_factor)
                    / (self.yield_percent * self.Ap * pi)) ** (1 / (2 - self.m))
            if isinstance(diam, float):
                min_diam_shear = diam
            else:
                break
            temp_k = factor_k
            factor_k = (8 * self.hook_r2 - min_diam_shear) / (8 * self.hook_r2 - 4 * min_diam_shear)

        factor_k, temp_k = 1.1, 0
        while abs(factor_k - temp_k) > 1e-3:
            diam = ((factor_k * self.force * (
                    16 * self.spring_index + 4) * static_safety_factor) / (
                                       self.bending_yield_percent * self.Ap * pi)) ** (
                                      1 / (2 - self.m))
            if isinstance(diam, float):
                min_diam_normal = diam
            else:
                break
            temp_k = factor_k
            try:
                c1 = self.hook_r1 / min_diam_normal
            except ZeroDivisionError:  # fixme: find another way to solve
                print("Failed to calculate minimum diameter for normal forces")
                min_diam_normal = None
            factor_k = (4 * c1 ** 2 - c1 - 1) / 4 * c1 * (c1 - 1)

        return min_diam_shear, min_diam_normal

    def min_spring_diameter(self, static_safety_factor):
        """return the minimum spring diameter to avoid static failure
        according to the specified safety factor, if the solid flag is True :attr:'Fsolid'
        is used instead of :attr:`force`

        :param float static_safety_factor: factor of safety

        :returns: The minimal spring diameter
        :rtype: float or Symbol
        """
        raise NotImplementedError("Not implemented yet")  # TODO: implement

    def check_design(self):
        """place holder"""
        raise NotImplementedError("Not implemented yet")  # TODO: implement

    def natural_frequency(self, density):
        """Figures out what is the natural frequency of the spring

        :param float density: spring material density

        :returns: Natural frequency
        :rtype: float
        """
        raise NotImplementedError("Not implemented yet")  # TODO: implement

    def weight(self, density):
        """Return's the spring *active coils* weight according to the specified density

        :param float density: The material density

        :returns: Spring weight
        :type: float or Symbol
        """
        springs.HelicalPushSpring.weight(self, density)

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
