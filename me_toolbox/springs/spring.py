# third party
from math import pi, sqrt
import numpy as np


# internal package
from me_toolbox.tools import print_atributes
from me_toolbox.tools import percent_to_decimal


# TODO: add optimization based on cost and other needs
class Spring:
    def __init__(self, force, Ap, m, torsion_yield_percent, wire_diameter, spring_diameter,
                 shear_modulus, shot_peened):
        self.force = force
        self.Ap = Ap
        self.m = m
        self.torsion_yield_percent = torsion_yield_percent
        self.wire_diameter = wire_diameter
        self.spring_diameter = spring_diameter
        self.shear_modulus = shear_modulus
        self.shot_peened = shot_peened

    def get_info(self):
        """print all of the spring properties"""
        print_atributes(self)

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
    def ultimate_tensile_strength(self):
        """ Sut - ultimate tensile strength """
        return self.Ap / (self.wire_diameter ** self.m)

    @property
    def shear_ultimate_strength(self):
        """ Ssu - ultimate tensile strength for shear """
        return 0.67 * self.ultimate_tensile_strength

    @property
    def shear_yield_strength(self):
        """ Ssy - yield strength for shear
        (shear_yield_stress = % * ultimate_tensile_strength))
        """
        return percent_to_decimal(self.torsion_yield_percent) * self.ultimate_tensile_strength

    def shear_endurance_limit(self, reliability):
        """Sse - Shear endurance limit according to Zimmerli

        :param float reliability: reliability in percentage

        :returns: Sse - Shear endurance limit
        :rtype: float
        """
        # data from table
        percentage = np.array([50, 90, 95, 99, 99.9, 99.99, 99.999, 99.9999])
        reliability_factors = np.array([1, 0.897, 0.868, 0.814, 0.753, 0.702, 0.659, 0.620])
        # interpolating from data
        Ke = np.interp(reliability, percentage, reliability_factors)  # pylint: disable=invalid-name

        if self.shot_peened:
            Ssa, Ssm = 398, 534  # pylint: disable=invalid-name
        else:
            Ssa, Ssm = 241, 379  # pylint: disable=invalid-name

        return Ke * (Ssa / (1 - (Ssm / self.shear_ultimate_strength) ** 2))

    def calc_max_shear_stress(self, force, k_factor):
        """Calculates the max shear stress based on the force applied

        :param float of Symbol force: Working force of the spring
        :param float k_factor: the appropriate k factor for the calculation

        :returns: Shear stress
        :rtype: float or Symbol
        """
        return (k_factor * 8 * force * self.spring_diameter) / (pi * self.wire_diameter ** 3)

    def natural_frequency(self, density):
        """Figures out what is the natural frequency of the spring

        :param float density: spring material density

        :returns: Natural frequency
        :rtype: float
        """
        return (self.wire_diameter / (2 * self.spring_diameter ** 2 * self.active_coils * pi)) \
            * sqrt(self.shear_modulus / (2 * density))

    def weight(self, density):
        """Return's the spring *active coils* weight according to the specified density

        :param float density: The material density

        :returns: Spring weight
        :type: float or Symbol
        """
        area = 0.25 * pi * self.wire_diameter ** 2  # cross section area
        length = pi * self.spring_diameter  # the circumference of the spring
        volume = area * length
        return volume * self.active_coils * density

    def calc_spring_constant(self):
        """Calculate spring constant (using Castigliano's theorem)

        :returns: The spring constant
        :rtype: float
        """
        return ((self.shear_modulus * self.wire_diameter) /
                (8 * self.spring_index ** 3 * self.active_coils)) * (
                       (2 * self.spring_index ** 2) / (1 + 2 * self.spring_index ** 2))

    def calc_active_coils(self):
        """Calculate active_coils which is the number of active coils (using Castigliano's theorem)

        :returns: number of active coils
        :rtype: float
        """
        return ((self.shear_modulus * self.wire_diameter) /
                (8 * self.spring_index ** 3 * self.spring_constant)) * (
                       (2 * self.spring_index ** 2) / (1 + 2 * self.spring_index ** 2))
