from Springs import Spring
from math import pi
from tools import PrintAtributes


class HelicalPushSpring(Spring):
    def __init__(self, force, wire_diameter, spring_diameter, Ap, m, shear_modulus, end_type, yield_percent,
                 spring_constant=None, set_removed=False, shot_peened=False):
        """
        :keyword shear_modulus: Shear modulus
        :keyword end_type: what kind of ending the spring has
        :keyword set_removed: if True adds to STATIC strength (must NOT use for fatigue application)
        :keyword shot_peened: if True adds to fatigue strength """
        super().__init__(Ap, m, yield_percent, wire_diameter, spring_diameter)

        if set_removed:
            print(f"Note: set should ONLY be removed for static loading and NOT for periodical loading")

        self.force = force
        self.set_removed = set_removed
        self.shot_peened = shot_peened
        self.shear_modulus = shear_modulus
        self.yield_percent = yield_percent
        self.spring_constant = spring_constant
        self.end_type = end_type.lower()

        end_types = ('plain', 'plain and ground', 'squared or closed', 'squared and ground')
        if self.end_type not in end_types:
            raise ValueError(f"{end_type} not one of this: {end_types}")

    def getInfo(self):
        """ print all of the spring properties """
        PrintAtributes(self)

    @property
    def spring_index(self):
        """ C - spring index

            Note: C should be in range of [4,12], lower C causes surface cracks,
                higher C causes the spring to tangle and require separate packing """
        C = self.spring_diameter / self.wire_diameter

        if isinstance(C, float) and not 4 <= C <= 12 and self.set_removed:
            print(f"Note: C - spring index should be in range of [4,12], lower C causes surface cracks,\n"
                  f"higher C causes the spring to tangle and requires separate packing")
        elif isinstance(C, float) and not 3 <= C <= 12:
            print(f"Note: C - spring index should be in range of [3,12], lower C causes surface cracks,\n"
                  f"higher C causes the spring to tangle and requires separate packing")

        return C

    @property
    def Na(self):
        """ Calculate Na which is the number of active coils (using Castigliano's theorem) """
        Na = ((self.shear_modulus * self.wire_diameter) / (8 * self.spring_index ** 3 * self.spring_constant)) * (
                (2 * self.spring_index ** 2) / (1 + 2 * self.spring_index ** 2))

        if isinstance(Na, float) and not 3 <= Na <= 15:
            print("Note: Na is not in range [3,15], this can cause non linear behavior")
        return Na

    @property
    def Ks(self):
        """ Ks - Static Shear stress concentration factor """
        return (2 * self.spring_index + 1) / (2 * self.spring_index)

    @property
    def Kw(self):
        """ K_W - Wahl shear stress concentration factor """
        return (4 * self.spring_index - 1) / (4 * self.spring_index - 4) + (0.615 / self.spring_index)

    @property
    def KB(self):  # NOT IMPLEMENTED!!! TODO: check when to use and implement
        """ K_B - Bergstrasser shear stress concentration factor (very close to Kw)"""
        return (4 * self.spring_index + 2) / (4 * self.spring_index - 3)

    @property
    def max_shear_stress(self):
        """ maximum shear stress """
        K = self.Ks if self.set_removed else self.Kw
        return (K * 8 * self.force * self.spring_diameter) / (pi * self.wire_diameter ** 3)

    @property
    def deflection(self):
        """ spring deflection (change in length) """
        return ((8 * self.force * self.spring_index ** 3 * self.Na) / (self.shear_modulus * self.wire_diameter)) * (
                (1 + 2 * self.spring_index ** 2) / (2 * self.spring_index ** 2))

    @property
    def end_coils(self):
        """ Ne - the end coils of the spring"""
        options = {'plain': 0, 'plain and ground': 1, 'squared or closed': 2, 'squared and ground': 2}
        return options.get(self.end_type)

    @property
    def total_coils(self):
        """ Nt - the total coils of the spring"""
        return self.end_coils + self.Na

    @property
    def solid_length(self):
        """ Ls - the solid length of the spring
            (if the spring is fully compressed so the coils are touching each other) """

        d = self.wire_diameter
        Nt = self.total_coils
        options = {'plain': d * (Nt + 1), 'plain and ground': d * Nt, 'squared or closed': d * (Nt + 1),
                   'squared and ground': d * Nt}
        return options.get(self.end_type)

    @property
    def static_safety_factor(self):
        return self.Ssy / self.max_shear_stress

    def weight(self, density):
        """ return the spring weight according to the specified density """
        return 0.25 * density * (pi ** 2) * (self.wire_diameter ** 2) * self.spring_diameter * self.Na

    def CalcSpringConstant(self, Na):
        """ Calculate the spring constant if Na is Known (using Castigliano's theorem) """
        return ((self.shear_modulus * self.wire_diameter) / (8 * self.spring_index ** 3 * Na)) * (
                (2 * self.spring_index ** 2) / (1 + 2 * self.spring_index ** 2))

    def MinimalWireDiameter(self, safety_factor):
        """ The minimal wire diameter for a given safety factor in order to avoid failure,
            according to the spring parameters """
        return ((8 * self.Kw * self.force * self.spring_index * safety_factor) / (
                self.yield_percent * self.Ap * pi)) ** (1 / (2 - self.m))
