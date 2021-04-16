"""A module containing the helical torsion spring class"""
from math import pi
from sympy import Symbol  # pylint: disable=unused-import

from fatigue import FailureCriteria
from me_toolbox.springs import Spring
from tools import percent_to_decimal


class HelicalTorsionSpring(Spring):
    """A Helical torsion spring object"""

    def __init__(self, max_moment, wire_diameter, spring_diameter, leg1, leg2,
                 shear_modulus, elastic_modulus, yield_percent, material=None, Ap=None, m=None,
                 spring_constant=None, active_coils=None, body_coils=None, shot_peened=False,
                 density=None, working_frequency=None, radius=None, pin_diameter=None):
        """Instantiate a helical torsion spring object with the given parameters

        :param float or Symbol max_moment: The maximum load on the spring
        :param float or Symbol wire_diameter: spring wire diameter
        :param float or Symbol spring_diameter: spring diameter measured from
            the center point of the wire diameter
        :param float leg1: spring leg
        :param float leg2: spring leg
        :param float shear_modulus: Spring's material shear modulus
        :param float elastic_modulus: Spring's material elastic modulus
        :param float yield_percent: Used to estimate the spring's yield stress
        :param str material: Spring's material (instead of Ap and m)
        :param float Ap: A constant for Estimating Minimum Tensile Strength of Common Spring Wires
        :param float m: A Constants Estimating Minimum Tensile Strength of Common Spring Wires
        :param float or None spring_constant: K - spring constant
        :param float or None active_coils: active_coils - number of active coils
        :param float or None body_coils: Spring's number of body coils
        :param bool shot_peened: if True adds to fatigue strength
        :param float or None density: Spring's material density
            (used for buckling and weight calculations)
        :param float or None working_frequency: the spring working frequency
            (used for fatigue calculations)
        :param float radius: The distance of applied force from the center
        :param float pin_diameter: the diameter of the pin going through the spring

        :returns: HelicalTorsionSpring
        """
        self.constructing = True
        max_force = max_moment / radius if radius is not None else None

        super().__init__(max_force, wire_diameter, spring_diameter, shear_modulus, elastic_modulus,
                         shot_peened, density, working_frequency, material, Ap, m)

        self.max_moment = max_moment
        self.yield_percent = yield_percent
        self.leg1, self.leg2 = leg1, leg2
        self.pin_diameter = pin_diameter
        self._na_k_sorter(active_coils, body_coils, spring_constant)

        self.constructing = False

    def _na_k_sorter(self, active_coils, body_coils, spring_constant):
        """The active coils, body coils and the spring
        constant are linked this method is meant to
        determine the order of assignment and calculation
        based on the class input

        :param float or None active_coils: The spring's number of active coils
        :param float or None body_coils: The spring's number of body coils
        :param float or None spring_constant: The spring's constant (rate)

        """
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

    @property
    def yield_strength(self):
        """ Sy - yield strength
        (shear_yield_stress = % * ultimate_tensile_strength))
        """
        return percent_to_decimal(self.yield_percent) * self.ultimate_tensile_strength

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

        else:
            # active_coils was not given so calculate it
            self._active_coils = self.calc_active_coils()

    def calc_active_coils(self):
        """Calculate Na which is the number of active coils
        (using Castigliano's theorem)

        :returns: number of active coils
        :rtype: float
        """
        D = self.spring_diameter

        if self.body_coils is None:
            d = self.wire_diameter
            active_coils = (d ** 4 * self.elastic_modulus) / (10.8 * D * self.spring_constant)
        else:
            active_coils = self.body_coils + (self.leg1 + self.leg2) / (3 * pi * D)
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

        else:
            # active_coils was not given so calculate it
            self._body_coils = self.calc_body_coils()

    def calc_body_coils(self):
        """Calculate active_coils which is the number of active coils (using Castigliano's theorem)

        :returns: number of active coils
        :rtype: float
        """
        return self.active_coils - (self.leg1 + self.leg2) / (3 * pi * self.spring_diameter)

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

        else:
            # spring_constant was not given so calculate it
            self._spring_constant = self.calc_spring_constant()

    def calc_spring_constant(self):
        """Calculate spring constant (using Castigliano's theorem)

        :returns: The spring constant
        :rtype: float
        """
        d = self.wire_diameter
        D = self.spring_diameter
        return (d ** 4 * self.elastic_modulus) / (10.8 * D * self.active_coils)

    @property
    def factor_ki(self):
        """Internal stress correction factor

        :returns:stress concentration factor
        :rtype: float
        """
        index = self.spring_index
        return (4 * index ** 2 - index - 1) / (4 * index * (index - 1))

    @property
    def max_stress(self):
        """The normal stress due to bending and axial loads

        :returns: Normal stress
        :rtype: float or Symbol
        """
        return self.calc_max_stress(self.max_moment)

    def calc_max_stress(self, moment):
        """Calculates the normal stress based on the moment given
        NOTE: The calculation is for round wire torsion spring

        :param float of Symbol moment: Working force of the spring

        :returns: normal stress
        :rtype: float or Symbol
        """
        return (self.factor_ki * 32 * moment) / (pi * self.wire_diameter ** 3)

    @property
    def max_total_angular_deflection(self):
        """The total angular deflection due to the max moment
        this deflection is comprise out of the angular deflection
        of the coil body and from the end deflection of a cantilever
        for *each* leg.

        :returns: Max angular deflection
        :rtype: float or Symbol
        """
        return self.calc_angular_deflection(self.max_moment)

    @property
    def max_angular_deflection(self):
        """The angular deflection due to the max moment
        of *only* the coil body

        :returns: Max angular deflection
        :rtype: float or Symbol
        """
        return self.calc_angular_deflection(self.max_moment, total=False)

    def calc_angular_deflection(self, moment, total=True):
        """Calculates the total angular deflection based on the moment given
        if the total flag is True than the total angular deflection is calculated,
        if False only the deflection of the coil body is calculated

        :param float of Symbol moment: Working moment of the spring
        :param bool total: total or partial deflection

        :returns: Total angular deflection
        :rtype: float or Symbol
        """
        d = self.wire_diameter
        D = self.spring_diameter
        E = self.elastic_modulus

        N = self.active_coils if total else self.body_coils
        return ((10.8 * moment * D) / (d ** 4 * E)) * N

    @property
    def helix_diameter(self):
        """The helix diameter"""
        Nb = self.body_coils
        return (Nb * self.spring_diameter) / (Nb + self.max_angular_deflection)

    @property
    def clearance(self):
        if self.pin_diameter is not None:
            return self.helix_diameter - self.wire_diameter - self.pin_diameter
        else:
            return "The pin diameter was not given"

    @property
    def static_safety_factor(self):  # pylint: disable=unused-argument
        """ Returns the static safety factor

        :returns: Spring's safety factor
        :type: float or Symbol
        """
        return self.yield_strength / self.max_stress

    def fatigue_analysis(self, max_moment, min_moment, reliability,
                         criterion='gerber', verbose=False, metric=True):
        """ Returns safety factors for fatigue and
        for first cycle according to Langer

        :param float max_moment: Maximal max_force acting on the spring
        :param float min_moment: Minimal max_force acting on the spring
        :param float reliability: in percentage
        :param str criterion: fatigue criterion
        :param bool verbose: print more details
        :param bool metric: Metric or imperial

        :returns: static and dynamic safety factor
        :rtype: tuple[float, float]
        """
        # calculating mean and alternating forces
        alt_moment = abs(max_moment - min_moment) / 2
        mean_moment = (max_moment + min_moment) / 2

        # calculating mean and alternating stresses
        alt_stress = self.calc_max_stress(alt_moment)
        mean_stress = self.calc_max_stress(mean_moment)

        Sse = self.shear_endurance_limit(reliability, metric)
        Se = Sse / 0.577  # based on the distortion energy method
        Sut = self.ultimate_tensile_strength
        Sy = self.yield_strength
        nf, nl = FailureCriteria.get_safety_factor(Sy, Sut, Se, alt_stress, mean_stress, criterion)
        if verbose:
            print(f"Alternating moment = {alt_moment}, Mean moment = {mean_moment}\n"
                  f"Alternating stress = {alt_stress}, Mean stress = {mean_stress}\n"
                  f"Sse = {Sse}, Se= {Se}")
        return nf, nl
