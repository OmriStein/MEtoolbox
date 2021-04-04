from math import sqrt

from tools import PrintAtributes


class EnduranceLimit:
    """ calculates Marin modification factors and return modified endurance limit """

    def __init__(self, Sut, surface_finish, rotating, max_normal_stress, max_bending_stress, stress_type, temp,
                 reliability, material=None, unmodified_endurance=None, A95=None, diameter=None, height=None,
                 width=None):
        """
        :keyword Sut: ultimate tensile strength
        :type Sut: float
        :keyword surface_finish: 'ground' / 'machined' / 'cold-drawn' / 'hot-rolled' / 'as forged'
        :type surface_finish: str
        :keyword rotating: rotating mode (True/False)
        :type rotating: bool
        :keyword max_normal_stress: (for axial loading check)
        :type max_normal_stress: float
        :keyword max_bending_stress: (for axial loading check)
        :type max_bending_stress: float
        :keyword stress_type: 'bending' / 'axial' / 'torsion' / 'shear' / 'multiple'
        :type stress_type: str
        :keyword temp: temperature
        :type: float
        :keyword reliability: reliability
        :type: float
        :keyword material:
        :type material: str
        :keyword unmodified_endurance:
        :keyword A95: Area containing over 95% of maximum periodic stress in the cross section
        :keyword diameter:
        :keyword height:
        :keyword width:
        """

        self.Sut = Sut
        self.surface_finish = surface_finish
        self.rotating = rotating
        self.max_normal_stress = max_normal_stress
        self.max_bending_stress = max_bending_stress
        self.diameter = diameter
        self.width = width
        self.height = height
        self.stress_type = stress_type
        self.temp = temp
        self.reliability = reliability
        self.material = material
        self.unmodified_endurance = unmodified_endurance
        self.A95 = self.CalcA95(A95)

    def CalcA95(self, A95):
        if A95 is not None:
            return A95
        elif self.diameter is not None:
            return 0.01046 * self.diameter ** 2
        elif (self.width and self.height) is not None:
            return 0.05 * self.width * self.height
        else:
            raise ValueError('A95 is None and no parameters (diameter/width/height)'
                             'were given in order to calculate it')

    @property
    def Ka(self):
        """ Surface condition modification factor

            :returns: Ka - surface finish factor
            :rtype: float"""

        data = {'ground': (1.58, -0.085),
                'machined': (4.51, -0.265),
                'cold-drawn': (4.51, -0.265),
                'hot-rolled': (57.7, -0.718),
                'as forged': (272, -0.995)}
        a, b = data[self.surface_finish]
        return a * (self.Sut ** b)

    @property
    def Kb(self):
        """ Size modification factor

        :returns: Kb - size factor
        :rtype: float """

        if self.max_normal_stress > 0.85 * self.max_bending_stress:
            # if axial loading accrue
            return 1
        elif self.rotating and self.diameter is not None:
            # rotating and round
            de = self.diameter
        else:
            # not rotating or not round
            de = sqrt(self.A95/0.07658)

        if 2.79 <= de <= 51:
            return 1.24 * (de ** -0.107)
        elif 51 < de <= 254:
            return 1.51 * (de ** -0.157)

    @property
    def Kc(self):
        """ Load modification factor

            :returns Kc - stress type factor
            :rtype: float """

        types = {'bending': 1, 'axial': 0.85, 'torsion': 0.59, 'shear': 0.59, 'multiple': 1}
        return types[self.stress_type]

    @property
    def Kd(self):
        """ Temperature modification factor

            :returns: Ks - temperature factor
            :rtype: float """

        import numpy as np
        percentage = np.array([20, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600])
        reliability_factors = np.array([1, 1.01, 1.02, 1.025, 1.02, 1, 0.975, 0.943, 0.9, 0.843, 0.768, 0.672, 0.549])
        return np.interp(self.temp, percentage, reliability_factors)

    @property
    def Ke(self):
        """ Reliability factor

            :returns: Ke - reliability factor
            :rtype: float """

        import numpy as np
        percentage = np.array([50, 90, 95, 99, 99.9, 99.99, 99.999, 99.9999])
        reliability_factors = np.array([1, 0.897, 0.868, 0.814, 0.753, 0.702, 0.659, 0.620])
        return np.interp(self.reliability, percentage, reliability_factors)

    @property
    def Kf(self):
        """ Miscellaneous effects factor """
        return 1

    @property
    def unmodified(self):
        print()
        if self.material is None and self.unmodified_endurance is None:
            raise ValueError("material and unmodified endurance can't both be None")

        data = {'steel': {'divider': 1400, 'lesser': 0.5 * self.Sut, 'grater': 700},
                'iron': {'divider': 400, 'lesser': 0.4 * self.Sut, 'grater': 160},
                'aluminium': {'divider': 330, 'lesser': 0.4 * self.Sut, 'grater': 130},
                'copper alloy': {'divider': 280, 'lesser': 0.4 * self.Sut, 'grater': 100}}

        if self.unmodified_endurance is None:
            if self.Sut < data[self.material]['divider']:
                return data[self.material]['lesser']
            else:
                return data[self.material]['grater']
        else:
            return self.unmodified_endurance

    @property
    def modified(self):
        """ returns the modified endurance limit """
        return self.Ka * self.Kb * self.Kc * self.Kd * self.Ke * self.Kf * self.unmodified

    def getFactors(self):
        """ print Marine factors """
        print(f"Ka={self.Ka:.3f}, Kb={self.Kb:.3f}, Kc={self.Kc:.3f}, Ks={self.Kd:.3f}, Ke={self.Ke:.3f}, Kf={self.Kf:.3f}")