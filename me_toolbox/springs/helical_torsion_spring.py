"""A module containing the helical torsion spring class"""
from math import pi, sqrt
from sympy import Symbol  # pylint: disable=unused-import

from me_toolbox.fatigue import FailureCriteria
from me_toolbox.springs import Spring
from me_toolbox.tools import percent_to_decimal


class HelicalTorsionSpring(Spring):
    """A Helical torsion spring object"""

    def __init__(self, max_moment, wire_diameter, spring_diameter, leg1, leg2,
                 ultimate_tensile_strength, yield_percent, shear_modulus, elastic_modulus,
                 spring_rate, radius=None, arbor_diameter=None, shot_peened=False, density=None,
                 working_frequency=None):
        """Instantiate helical torsion spring object with the given parameters

        :param float  max_moment: The maximum load on the spring
        :param float  wire_diameter: spring wire diameter
        :param float  spring_diameter: spring diameter measured from
            the center point of the wire diameter
        :param float ultimate_tensile_strength: Ultimate tensile strength of the material
        :param float leg1: spring leg
        :param float leg2: spring leg
        :param float shear_modulus: Spring's material shear modulus
        :param float elastic_modulus: Spring's material elastic modulus
        :param float yield_percent: Used to estimate the spring's yield stress
        :param float spring_rate: K - spring rate
        :param float arbor_diameter: the diameter of the pin going through the spring
        :param float radius: The distance of applied force from the center
        :param bool shot_peened: if True adds to fatigue strength
        :param float or None density: Spring's material density
            (used for buckling and weight calculations)
        :param float or None working_frequency: the spring working frequency
            (used for fatigue calculations)

        :returns: HelicalTorsionSpring
        """
        max_force = max_moment / radius if radius is not None else None

        super().__init__(max_force, wire_diameter, spring_diameter, spring_rate,
                         ultimate_tensile_strength, shear_modulus, elastic_modulus,
                         shot_peened, density, working_frequency)

        self.max_moment = max_moment
        self.yield_percent = yield_percent
        self.leg1 = leg1
        self.leg2 = leg2
        self.arbor_diameter = arbor_diameter

    def check_design(self):
        raise NotImplementedError("check_design is not implemented yet for HelicalTorsionSpring")

    @property
    def diameter_after_deflection(self):
        """ After deflection The spring diameter is shrinking it is important to know the new
        diameter to check if it conflicts with the arbor size

        :return: The spring diameter after deflection
        :rtype: float
        """
        Nb = self.body_coils
        return (Nb * self.diameter) / (Nb + self.calc_angular_deflection(self.max_moment, False))

    @property
    def clearance(self):
        """Diametrical Clearance between the spring after deflection and the arbor"""
        if self.arbor_diameter is not None:
            ID = self.diameter_after_deflection - self.wire_diameter
            return ID - self.arbor_diameter
        else:
            return "The pin diameter was not given"

    @property
    def length(self):
        """ The length of the spring - L """
        return self.wire_diameter * self.body_coils

    @property
    def active_coils(self):
        """Number of active coils - Na

        Note: according to the analytical calculation the 67.8584 should be 64 (from the second
        moment of inertia of a round wire) but 67.8584 fits better to the experimental results,
        probably due to friction between the coils and arbor.

        :returns: number of active coils
        :rtype: float
        """
        D = self.diameter
        d = self.wire_diameter
        active_coils = (d ** 4 * self.elastic_modulus) / (67.8584 * D * self.spring_rate)
        return active_coils

    @property
    def body_coils(self):
        """Total number of coils

        :returns: number of body coils
        :rtype: float
        """
        return self.active_coils - ((self.leg1 + self.leg2) / (3 * pi * self.diameter))

    @property
    def partial_turn(self):
        """Partial number of coils (β/360)

        :returns: Partial number of coils
        :rtype: float
        """
        return self.body_coils - int(self.body_coils)

    @property
    def yield_strength(self):
        """ Sy - yield strength
        (shear_yield_stress = % * ultimate_tensile_strength))
        """
        try:
            return percent_to_decimal(self.yield_percent) * self.ultimate_tensile_strength
        except TypeError:
            return self.yield_percent * self.ultimate_tensile_strength

    @property
    def factor_Ki(self):
        """Inner fibers stress correction factor

        :returns:stress concentration factor ki
        :rtype: float
        """
        index = self.spring_index
        return (4 * index ** 2 - index - 1) / (4 * index * (index - 1))

    @property
    def factor_Ko(self):
        """Outer fiber stress correction factor. in light that factor_Ko is always less than
        factor_ki we don't use it in the stress estimation, but it is brought here
        for the sake of completion

        :returns:stress concentration factor Ko
        :rtype: float
        """
        index = self.spring_index
        return (4 * index ** 2 - index - 1) / (4 * index * (index - 1))

    @property
    def max_stress(self):
        """The normal stress due to bending and axial loads

        :returns: Normal stress
        :rtype: float 
        """
        return self.calc_max_stress(self.max_moment)

    def calc_max_stress(self, moment):
        """Calculates the normal stress based on the moment given
        NOTE: The calculation is for round wire torsion spring.

        :param float moment: Working force of the spring

        :returns: normal stress
        :rtype: float 
        """
        return self.factor_Ki * ((32 * moment) / (pi * self.wire_diameter ** 3))

    @property
    def natural_frequency(self):
        raise NotImplementedError("natural_frequency has not been implemented yet "
                                  "for HelicalTorsionSpring")

    @property
    def max_angular_deflection(self):
        """The total angular deflection due to the max moment
        this deflection consists of the angular deflection
        of the coil body and from the end deflection of cantilever
        for *each* leg.

        :returns: Max angular deflection
        :rtype: float 
        """
        return self.calc_angular_deflection(self.max_moment)

    def calc_angular_deflection(self, moment, total_deflection=True):
        """Calculates the total angular deflection based on the moment given,
        If the total flag is True than the total angular deflection is calculated,
        if False only the deflection of the coil body is calculated (without the legs)

        Note: according to the analytical calculation the 67.8584 should be 64 (from the second
        moment of inertia of a round wire) but 67.8584 fits better to the experimental results,
        probably due to friction between the coils and arbor.

        :param float  moment: Working moment of the spring
        :param bool total_deflection: total or partial deflection

        :returns: Total angular deflection in radians
        :rtype: float 
        """
        d = self.wire_diameter
        D = self.diameter
        E = self.elastic_modulus
        l1 = self.leg1
        l2 = self.leg2
        Nb = self.body_coils
        legs_deflection_part = (l1 + l2)/(3*pi*D) if total_deflection else 0
        return ((67.8584 * moment * D) / (d ** 4 * E)) * (Nb + legs_deflection_part)

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
            return (coil_volume * self.body_coils + (self.leg1 + self.leg2) * area) * self.density
        else:
            raise ValueError(f"Can't calculate weight, no density is specified")

    @property
    def static_safety_factor(self):  # pylint: disable=unused-argument
        """ Returns the static safety factor

        :returns: Spring's safety factor
        :type: float
        """
        return self.yield_strength / self.max_stress

    def fatigue_analysis(self, max_moment, min_moment, reliability,
                         criterion='gerber', verbose=False, metric=True):
        """ Returns safety factors for fatigue and
        for first cycle according to Langer failure criteria.

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
        nf, nl = FailureCriteria.get_safety_factors(Sy, Sut, Se, alt_stress, mean_stress, criterion)
        if verbose:
            print(f"Alternating moment = {alt_moment}, Mean moment = {mean_moment}\n"
                  f"Alternating stress = {alt_stress}, Mean stress = {mean_stress}\n"
                  f"Sse = {Sse}, Se= {Se}")
        return nf, nl

    def min_wire_diameter(self, safety_factor, spring_diameter=None, spring_index=None):
        """The minimal wire diameter for given safety factor
        in order to avoid failure, according to the spring parameters

        Note: In order for the calculation to succeed the
            spring diameter or the spring index should be known.

        :param float safety_factor: static safety factor
        :param float spring_diameter: The spring diameter
        :param float spring_index: The spring index

        :returns: The minimal wire diameter
        :rtype: float
        """
        factor_k, temp_k = 1.1, 0
        diam = 0
        while abs(factor_k - temp_k) > 1e-4:
            # waiting for k to converge
            diam = ((32 * self.max_moment * factor_k * safety_factor) / (
                    self.yield_percent * self.Ap * pi)) ** (
                           1 / (3 - self.m))
            temp_k = factor_k
            if spring_diameter is not None:
                D = spring_diameter
                factor_k = (4 * D ** 2 - D * diam - diam ** 2) / (4 * D * (D - diam))
            elif spring_index is not None:
                c = spring_index
                factor_k = (4 * c ** 2 - c - 1) / (4 * c * (c - 1))
            else:
                print("Need to know spring index or spring diameter to calculate wire diameter")
        return diam

    def min_spring_diameter(self, safety_factor, wire_diameter):
        """return the minimum spring diameter to avoid static failure
        according to the specified safety factor.

        :param float safety_factor: static safety factor
        :param float wire_diameter: Spring's wire diameter

        :returns: The minimal spring diameter
        :rtype: float
        """
        d = wire_diameter
        Sy = self.yield_strength
        M = self.max_moment
        alpha = 4 * (Sy * pi * d ** 3 - 32 * M * safety_factor)
        beta = -d * (4 * Sy * pi * d ** 3 + 32 * M * safety_factor)
        gamma = 32 * M * safety_factor * d ** 2
        return (-beta + sqrt(beta ** 2 - 4 * alpha * gamma)) / (2 * alpha)

    @staticmethod
    def calc_spring_rate(wire_diameter, spring_diameter, active_coils, elastic_modulus):
        """Estimate spring constant from geometric and material properties

        :returns: The spring constant [Nm/rad]
        :rtype: float
        """
        d = wire_diameter
        D = spring_diameter
        return (d ** 4 * elastic_modulus) / (67.8584 * D * active_coils)
