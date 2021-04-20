# third party
import csv
import os
from math import pi
import numpy as np
from sympy import Symbol, symbols, sqrt

# internal package
from me_toolbox.tools import print_atributes


# TODO: add optimization based on cost and other needs
class Spring:

    def __repr__(self):
        try:
            return f"{self.__class__.__name__}(K={self.spring_constant}, d={self.wire_diameter}, " \
                   f"D={self.spring_diameter})"
        except AttributeError:
            return f"{self.__class__.__name__}(d={self.wire_diameter}, D={self.spring_diameter})"

    def __init__(self, max_force, wire_diameter, spring_diameter,
                 shear_modulus, elastic_modulus, shot_peened, density, working_frequency, Ap, m):
        self.max_force = max_force
        self.Ap, self.m = Ap, m
        self._wire_diameter = wire_diameter
        self._spring_diameter = spring_diameter
        self.shear_modulus = shear_modulus
        self.elastic_modulus = elastic_modulus
        self.shot_peened = shot_peened
        self.density = density
        self.working_frequency = working_frequency

        self._active_coils = None
        self._body_coils = None
        self._spring_constant = None

    @classmethod
    def symbolic_spring(cls, shot_peened=False):
        F, d, D, G, E, yield_percent, density, working_frequency, Ap, m = symbols(
            'F, d, D, G, E, yield_percent, rho, omega, Ap, m')
        return Spring(F, d, D, G, E, shot_peened, density, working_frequency, Ap, m)

    def get_info(self):
        """print all of the spring properties"""
        print_atributes(self)

    @property
    def wire_diameter(self):
        """Getter for the wire diameter attribute

        :returns: The spring's wire diameter
        :rtype: float or Symbol
        """
        return self._wire_diameter

    @property
    def spring_diameter(self):
        """Getter for the spring diameter attribute

        :returns: The spring diameter
        :rtype: float or Symbol
        """
        return self._spring_diameter

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

    def shear_endurance_limit(self, reliability, metric=True):
        """Sse - Shear endurance limit according to Zimmerli

        :param float reliability: reliability in percentage
        :param bool metric: metric or imperial

        :returns: Sse - Shear endurance limit
        :rtype: float
        """
        # data from table
        percentage = np.array([50, 90, 95, 99, 99.9, 99.99, 99.999, 99.9999])
        reliability_factors = np.array([1, 0.897, 0.868, 0.814, 0.753, 0.702, 0.659, 0.620])
        # interpolating from data
        Ke = np.interp(reliability, percentage, reliability_factors)

        if self.shot_peened:
            Ssa, Ssm = (398, 534) if metric else (57.5e3, 77.5e3)
        else:
            Ssa, Ssm = (241, 379) if metric else (35e3, 55e3)

        return Ke * (Ssa / (1 - (Ssm / self.shear_ultimate_strength) ** 2))

    def calc_max_shear_stress(self, force, k_factor):
        """Calculates the max shear stress based on the max_force applied

        :param float of Symbol force: Working max_force of the spring
        :param float k_factor: the appropriate k factor for the calculation

        :returns: Shear stress
        :rtype: float or Symbol
        """
        return (k_factor * 8 * force * self.spring_diameter) / (pi * self.wire_diameter ** 3)

    @property
    def natural_frequency(self,):
        """Figures out what is the natural frequency of the spring

        :param float density: spring material density

        :returns: Natural frequency
        :rtype: float
        """
        d = self.wire_diameter
        D = self.spring_diameter
        Na = self.active_coils
        G = self.shear_modulus
        try:
            return (d / (2 * D ** 2 * Na * pi)) * sqrt(G / (2 * self.density))
        except TypeError:
            return None

    @property
    def weight(self):
        """Return's the spring *active coils* weight according to the specified density

        :returns: Spring weight
        :type: float or Symbol
        """
        area = 0.25 * pi * self.wire_diameter ** 2  # cross section area
        length = pi * self.spring_diameter  # the circumference of the spring
        volume = area * length
        try:
            return volume * self.active_coils * self.density
        except TypeError:
            return None

    def calc_spring_constant(self):
        """Calculate spring constant (using Castigliano's theorem)

        :returns: The spring constant
        :rtype: float
        """
        G = self.shear_modulus
        d = self.wire_diameter
        C = self.spring_index
        Na = self.active_coils
        return ((G * d) / (8 * C ** 3 * Na)) * ((2 * C ** 2) / (1 + 2 * C ** 2))

    @staticmethod
    def material_prop(material, diameter, metric=True):
        """Reads table A_and_m.csv from file and returns the
        material properties Ap and m for Sut estimation

        :param str material: The spring's material
        :param float diameter: Wire diameter
        :param str metric: Metric or imperial

        :returns: Ap and m for Sut estimation
        :rtype: (float, float)
        """
        # TODO: Find a way to work with symbolic diameter
        if isinstance(diameter, Symbol):
            raise ValueError(f"the material keyword can't be used if the diameter is symbolic "
                             f"specify Ap and m manually")

        path = os.path.dirname(__file__) + "\\tables\\A_and_m.csv"
        with open(path, newline='') as file:
            reader = csv.DictReader(file)
            table = []
            available_types = []
            for line in reader:
                table.append(line)
                available_types.append(line['type'])

        for line in table:
            min_d = float(line['min_d_mm'] if metric else line['min_d_in'])
            max_d = float(line['max_d_mm'] if metric else line['max_d_in'])
            if line['type'] == material.lower() and min_d <= diameter <= max_d:
                return float(line['A_mm'] if metric else line['A_in']), float(line['m'])

        if material not in available_types:
            raise KeyError("The material is unknown")
        else:
            raise ValueError("The diameter don't match any of the values in the table")
