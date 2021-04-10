from tools import print_atributes


class Spring:
    def __init__(self, max_force, Ap, m, yield_percent, wire_diameter, spring_diameter, shear_modulus):
        self.force = max_force
        self.Ap = Ap
        self.m = m
        self.yield_percent = yield_percent
        self.wire_diameter = wire_diameter
        self.spring_diameter = spring_diameter
        self.shear_modulus = shear_modulus

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
        if 1 <= self.yield_percent <= 100:
            # if the yield_percent is in percentage form divide by 100
            return (self.yield_percent / 100) * self.ultimate_tensile_strength
        elif 0 < self.yield_percent < 1:
            # if the yield_percent is in decimal form no correction needed
            return self.yield_percent * self.ultimate_tensile_strength
        else:
            raise ValueError("something is wrong with the yield percentage")

    def get_info(self):
        """print all of the spring properties"""
        print_atributes(self)
