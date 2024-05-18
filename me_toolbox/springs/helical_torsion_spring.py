"""A module containing the helical torsion spring class"""
from math import pi

from me_toolbox.fatigue import FailureCriteria, FatigueAnalysis
from me_toolbox.springs import Spring
from me_toolbox.tools import percent_to_decimal


class HelicalTorsionSpring(Spring):
    """A Helical torsion spring object"""

    def __repr__(self):
        return f"HelicalTorsionSpring(max_moment={self.max_moment}, " \
               f"wire_diameter{self.wire_diameter}, spring_diameter={self.diameter}, " \
               f"leg1={self.leg1}, leg2={self.leg2}, " \
               f"ultimate_tensile_strength={self.ultimate_tensile_strength}, " \
               f"yield_percent={self.yield_percent}, shear_modulus={self.shear_modulus}, " \
               f"elastic_modulus={self.elastic_modulus}, spring_rate={self.spring_rate}, " \
               f"arbor_diameter={self.arbor_diameter}, shot_peened={self.shot_peened}, " \
               f"density={self.density})"

    def __str__(self):
        return f"HelicalTorsionSpring(d={self.wire_diameter}, D={self.diameter}, " \
               f"k={self.spring_rate})"

    def __init__(self, max_moment, wire_diameter, spring_diameter, leg1, leg2,
                 ultimate_tensile_strength, yield_percent, shear_modulus, elastic_modulus,
                 spring_rate, arbor_diameter=None, shot_peened=False, density=None):
        """Instantiate helical torsion spring object with the given parameters

        :param float  max_moment: The maximum load on the spring [Nmm]
        :param float  wire_diameter: spring wire diameter [mm]
        :param float  spring_diameter: spring diameter measured from [mm]
            the center point of the wire diameter
        :param float leg1: Effective length of the first spring's leg [mm] (where the force is applied)
        :param float leg2: Effective length of the second spring's leg [mm] (where the force is applied)
        :param float ultimate_tensile_strength: Ultimate tensile strength of the material [MPa]
        :param float yield_percent: Used to estimate the spring's yield stress
        :param float shear_modulus: Spring's material shear modulus [MPa]
        :param float elastic_modulus: Spring's material elastic modulus [MPa]
        :param float spring_rate: K - spring rate [Nmm/rad]
        :param float arbor_diameter: the diameter of the pin going through the spring [mm]
        :param bool shot_peened: if True adds to fatigue strength
        :param float or None density: Spring's material density [kg/m^3]
            (used for buckling and weight calculations)

        :returns: HelicalTorsionSpring
        """
        force1 = max_moment / leg1
        force2 = max_moment / leg2
        max_force = max(force1, force2)

        super().__init__(max_force, wire_diameter, spring_diameter, spring_rate,
                         ultimate_tensile_strength, shear_modulus, elastic_modulus,
                         shot_peened, density)

        self.max_moment = max_moment
        self.yield_percent = yield_percent
        self.leg1 = leg1
        self.leg2 = leg2
        self.arbor_diameter = arbor_diameter

        self.check_design()

    def check_design(self):
        if self.arbor_diameter is None:
            return None
        if self.clearance < 0:
            print(f"The clearance between the spring and arbor "
                  f"after tension is applied is negative ({self.clearance})")
            return False
        elif self.clearance == 0:
            print(f"The clearance between the spring and arbor "
                  f"after tension is applied is zero")
        else:
            return True

    @property
    def loaded_diameter(self) -> float:
        """Diameter after load is applied"""
        Nb = self.body_coils
        return (Nb * self.diameter) / (Nb + self.calc_angular_deflection(self.max_moment, False))

    @property
    def clearance(self) -> float:
        """Diametrical Clearance between the spring after deflection and the arbor"""
        if self.arbor_diameter is None:
            raise KeyError("Arbor diameter attribute is None")

        ID = self.loaded_diameter - self.wire_diameter
        return ID - self.arbor_diameter

    @property
    def free_length(self) -> float:
        """Free length of the spring (L) """
        return self.wire_diameter * self.body_coils

    @property
    def loaded_length(self) -> float:
        """Length after load is applied"""
        return self.wire_diameter * (self.body_coils + 1 + (self.partial_turn / 360))

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
    def body_coils(self) -> float:
        """Total number of coils"""
        return self.active_coils - ((self.leg1 + self.leg2) / (3 * pi * self.diameter))

    @property
    def partial_turn(self) -> float:
        """Partial number of coils (β) in degrees, i.e. The angle between the legs of the spring"""
        return (self.body_coils - int(self.body_coils))*360

    @property
    def yield_strength(self) -> float:
        """Yield strength (Sy)
        (shear_yield_stress = % * ultimate_tensile_strength)
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
    def max_stress(self) -> float:
        """The normal stress due to bending and axial loads"""
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
    def weight(self) -> float:
        """Return's the spring weight"""
        area = 0.25 * pi * (self.wire_diameter * 1e-3) ** 2  # cross-section area
        length = pi * self.diameter * 1e-3  # the circumference of the spring
        coil_volume = area * length
        if self.density is not None:
            return (coil_volume * self.body_coils + (self.leg1 + self.leg2) * area) * self.density
        else:
            raise ValueError(f"Can't calculate weight, no density is specified")

    def static_safety_factor(self, verbose=False):
        """ Returns the static safety factor

        :param bool verbose: Print additional information

        :returns: Spring's safety factor
        :type: float
        """
        if verbose:
            print(f"Sy={self.yield_strength}, Maximal stress={self.max_stress}")
        return self.yield_strength / self.max_stress

    def fatigue_analysis(self, max_moment, min_moment, fatigue_percent, reliability,
                         criterion='gerber', z=-3, verbose=False):
        """ Returns safety factors for fatigue and
        for first cycle according to Langer failure criteria.

        :param float max_moment: Maximal max_force acting on the spring
        :param float min_moment: Minimal max_force acting on the spring
        :param float fatigue_percent: Percent of Tensile Strength
        :param float reliability: in percentage
        :param str criterion: fatigue criterion ('modified goodman', 'soderberg', 'gerber', 'asme-elliptic')
        :param float z: -3 for steel where N=1e6, -5 for metal where N=1e8, -5.69 for metal where N=5e8
        :param bool verbose: print more details

        :returns: static and dynamic safety factor
        :rtype: tuple[float, float]
        """
        if max_moment == min_moment:
            raise ValueError("max_moment can't equal the min_moment")
        # calculating mean and alternating forces
        alt_moment = abs(max_moment - min_moment) / 2
        mean_moment = (max_moment + min_moment) / 2

        # calculating mean and alternating stresses
        alt_stress = self.calc_max_stress(alt_moment)
        mean_stress = self.calc_max_stress(mean_moment)

        Se = self.endurance_limit(fatigue_percent, reliability)
        Sut = self.ultimate_tensile_strength
        Sy = self.yield_strength
        nf, nl = FailureCriteria.get_safety_factors(Sy, Sut, Se, alt_stress, mean_stress, criterion)
        N, Sf = FatigueAnalysis.calc_num_of_cycles(mean_stress, alt_stress, Se, Sut, Sy, z)
        if verbose:
            print(f"Alternating moment = {alt_moment}, Mean moment = {mean_moment}\n\n"
                  f"Alternating stress = {alt_stress}, Mean stress = {mean_stress}\n\n"
                  f"Se= {Se}")
        return nf, nl, N, Sf

    def natural_frequency(self):
        # return sqrt(self.spring_rate / self.weight)
        raise NotImplementedError("natural_frequency is not implemented yet for HelicalTorsionSpring")

    @staticmethod
    def calc_spring_rate(wire_diameter, spring_diameter, active_coils, elastic_modulus):
        """Estimate spring constant from geometric and material properties

        :returns: The spring constant [Nm/rad]
        :rtype: float
        """
        d = wire_diameter
        D = spring_diameter
        return (d ** 4 * elastic_modulus) / (67.8584 * D * active_coils)
