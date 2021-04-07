class Spring:
    def __init__(self, force, Ap, m, yield_percent, wire_diameter, spring_diameter, shear_modulus):
        self.force = force
        self.Ap = Ap
        self.m = m
        self.shear_modulus = shear_modulus
        self.spring_diameter = spring_diameter
        self.wire_diameter = wire_diameter
        self.yield_percent = yield_percent

    @property
    def Sut(self):
        """ ultimate tensile strength """
        return self.Ap / (self.wire_diameter ** self.m)

    @property
    def Ssu(self):
        """ ultimate tensile strength for shear """
        return 0.67 * self.Sut

    @property
    def Ssy(self):
        """ yield strength for shear (Ssy = % * Ssu)) """
        if 1 <= self.yield_percent <= 100:
            # if the yield_percent is in percentage form divide by 100
            return (self.yield_percent/100) * self.Sut
        elif 0 < self.yield_percent < 1:
            # if the yield_percent is in decimal form no correction needed
            return self.yield_percent * self.Sut
        else:
            raise ValueError("something is wrong with the yield percentage")
