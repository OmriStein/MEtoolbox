class Spring:
    def __init__(self, Ap, m, yield_percent, wire_diameter, spring_diameter):
        self.Ap = Ap
        self.m = m
        self.wire_diameter = wire_diameter
        self.spring_diameter = spring_diameter
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
        return self.yield_percent * self.Sut
