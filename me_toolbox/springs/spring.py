# third party
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
