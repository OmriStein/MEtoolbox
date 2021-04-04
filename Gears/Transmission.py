from math import cos, sin, log, sqrt, radians, pi
from tools import PrintAtributes

class GearTypeError(ValueError):
    pass


class Transmission:
    """ Transmission object containing the transmission design parameters
        and methods to perform strength analysis on its gears. (AGMA 2001-D04)"""
    # TODO: add advices to improve strength
    # TODO: add function to find minimum volume for contact and bending

    def __init__(self, driving_machine, driven_machine, oil_temp, reliability,
                 power, SF, gear1, gear2=None, gear_ratio=0, SH=1):
        """
        :keyword gear1: gear object (the driving gear by convention)
        :type gear1: SpurGear
        :keyword gear2: gear object (the driven gear by convention)
        :type gear2: SpurGear
        :keyword driving_machine: ('uniform' - Electric Motor/Turbine, 'light shock' - multi-cylinder engine,
                                   'medium shock' - single-cylinder engine)
        :type driving_machine: string
        :keyword driven_machine: (uniform / moderate shock / heavy shock)
        :type driven_machine: string
        :keyword oil_temp: oil temperature of the transmission in [deg spring_index]
        :type oil_temp: int
        :keyword reliability: reliability of the transmission
        :type reliability: float
        :keyword power: transmission power in [W]
        :type power: float
        :keyword SF: bending safety factor
        :type SF: float
        :keyword SH: contact safety factor
        :type SH: float
        :keyword gear_ratio: transmission gear ratio
        :type gear_ratio: float
        :rtype: Transmission
        """

        # check if both gears are the same type (spur or helical)
        if (type(gear1) is not type(gear2)) and (gear2 is not None):
            raise GearTypeError("gears entered to Transmission are not of the same type")

        self.gear1 = gear1
        self.gear2 = self._Gear2Checkup(gear1, gear2, gear_ratio)

        # check if the pressure angle match between gear1 and gear2
        gear1.CheckCompatibility(self.gear2)

        self.driving_machine = driving_machine
        self.driven_machine = driven_machine
        self.oil_temp = oil_temp
        self.reliability = reliability
        self.power = power
        self.SF = SF
        self.SH = SH
        self.gear_ratio = gear_ratio
        self._ContactRatio()
        self.gear1.Y_j(self.gear1, self.gear2)
        self.gear1.Zw = 1  # the pinion's Zw is 1 by the AGMA standard
        self.gear2.Zw = self._Zw()
        self.ZI = gear1.ZI(self.gear1, self.gear2)

    def getInfo(self):
        """ print all the class fields with values """
        for key in self.__dict__:
            print(key, ":", self.__dict__[key])

    def getFactors(self, verbose=True):
        """ retrieve transmission analysis factors

            :keyword verbose: print factors
            :type verbose: bool
            :rtype: dict """

        if verbose:
            print("Ko=", self.Ko, "Yθ=", self.Ytheta, "Yz=", self.Yz, "ZE=", self.ZE, "ZI=", self.ZI)
        return {"Ko=": self.Ko, "Yθ=": self.Ytheta, "Yz=": self.Yz, "ZE=": self.ZE, "ZI=": self.ZI}

    @property
    def Ytheta(self):
        # calculating Temperature factor
        # input: Temp - oil_temp in degree celsius
        # output: y_theta - temperature factor

        if self.oil_temp > 71:
            y_theta = (273 + self.oil_temp) / 344
        else:
            y_theta = 1
        return y_theta

    @property
    def Ko(self):
        """ overload factor
            Ko is dependent on the type of driving motor type (Electric Motor/Turbine - uniform,
            multi-cylinder engine - light shock, single-cylinder engine - medium shock)
            and on the driven machine type (uniform, moderate shock, heavy shock) """

        table = {'uniform': {'uniform': 1, 'moderate shock': 1.25, 'heavy shock': 1.75},
                 'light shock': {'uniform': 1.25, 'moderate shock': 1.5, 'heavy shock': 2},
                 'medium shock': {'uniform': 15, 'moderate shock': 1.75, 'heavy shock': 2.25}}

        if self.driving_machine not in table:
            raise ValueError("error at Ko factor: invalid driving machine")

        if self.driven_machine not in table[self.driving_machine]:
            raise ValueError("error at Ko factor: invalid driven machine")

        return table[self.driving_machine][self.driven_machine]

    @property
    def Yz(self):
        """ calculating Reliability factor
            input: reliability_num - reliability percentage
            output: Y_z - Reliability factor """

        R = self.reliability
        if 0.9 <= R <= 0.99:
            Y_z = 0.658 - 0.0759 * log(1 - R)
        elif 0.99 < R <= 0.9999:
            Y_z = 0.5 - 0.109 * log(1 - R)
        else:
            raise ValueError("Reliability not in range (0.9<=R<=0.9999)")

        return Y_z

    @property
    def ZE(self):
        """ Elastic coefficient
            ZE is dependent on the gears material """

        elastic_modulus_list = {'steel': 2e5, 'malleable iron': 1.7e5, 'nodular iron': 1.7e5, 'cast iron': 1.5e5,
                                'aluminum bronze': 1.2e5, 'tin bronze': 1.1e5}

        material1 = self.gear1.material
        material2 = self.gear2.material

        E1 = elastic_modulus_list.get(material1, material1)
        E2 = elastic_modulus_list.get(material2, material2)

        Poissons_ratio = 1 / 3
        try:
            return sqrt((1/pi) / (((1 - Poissons_ratio ** 2) / E1) + ((1 - Poissons_ratio ** 2) / E2)))
        except TypeError:
            print(f"error: at ZE: invalid gear material ({material1} or {material2})")

    @property
    def CentersDistance(self):
        """ calculate the distance between the centers of the gears

            :return: the distance between the transmissions gears centers in [mm]
            :rtype: float """
        return self.gear1.CalculateCentersDistance(self.gear_ratio)

    # bending stress related methods
    def BendingStress(self, gear):
        """ calculating bending stress

            :keyword gear: gear object
            :type gear: Union[SpurGear, HelicalGear]
            :rtype: float """

        N = gear.teeth_num
        b = gear.width
        d = gear.pitch_diameter
        Yj = gear.Yj
        Wt = gear.CalculateForces(gear, self.power)[0]
        sigma = (Wt * N * self.Ko * gear.Kv * gear.Ks * gear.KH * gear.KB) / (Yj * b * d)
        return sigma

    def AllowedBendingStress(self, gear):
        """ calculating allowed bending stress

            :keyword gear: gear object
            :type gear: Union[SpurGear, HelicalGear]
            :rtype: float """

        allowed_bending_stress = (gear.St * gear.YN) / (self.Ytheta * self.Yz * self.SF)
        return allowed_bending_stress

    def MinimumWidthForBending(self, gear):
        """ calculating minimum gear width to withstand bending stress

            :keyword gear: gear object
            :type gear: Union[SpurGear, HelicalGear]
            :rtype: float """

        Yj = gear.Yj
        N = gear.teeth_num
        d = gear.pitch_diameter

        allowed_bending = self.AllowedBendingStress(gear)
        Wt = gear.CalculateForces(gear, self.power)[0]
        minimum_gear_width = (Wt * N * self.Ko * gear.Kv * gear.Ks * gear.KH * gear.KB) / (Yj * allowed_bending * d)
        return minimum_gear_width

    # contact stress related methods
    def ContactStress(self, gear):
        """ calculating contact stress

            :keyword gear: gear object
            :type gear: Union[SpurGear, HelicalGear]
            :rtype: float """

        b = gear.width
        d = gear.pitch_diameter
        Wt = gear.CalculateForces(gear, self.power)[0]

        sigma = sqrt((Wt * (self.ZE ** 2) * self.Ko * gear.Kv * gear.Ks * gear.KH * gear.ZR) / (b * d * self.ZI))
        return sigma

    def AllowedContactStress(self, gear):
        """ calculating allowed contact stress

            :keyword gear: gear object
            :type gear: Union[SpurGear, HelicalGear]
            :rtype: float """

        allowed_contact_stress = (gear.Sc * gear.ZN * gear.Zw) / (self.Ytheta * self.Yz * self.SH)
        return allowed_contact_stress

    def MinimumWidthForContact(self, gear):
        """ calculating minimum gear width to withstand contact stress

            :keyword gear: gear object
            :type gear: Union[SpurGear, HelicalGear]
            :rtype: float """

        Wt = gear.CalculateForces(gear, self.power)[0]
        d = gear.pitch_diameter
        allowed_contact = self.AllowedContactStress(gear)
        Kv = gear.Kv
        Ks = gear.Ks
        KH = gear.KH
        ZR = gear.ZR

        minimum_gear_width = (Wt * self.ZE ** 2 * self.Ko * Kv * Ks * KH * ZR) / (d * self.ZI * allowed_contact ** 2)
        return minimum_gear_width

    # for both bending and contact stresses
    def LifeExpectency(self, gear, in_hours=False):
        """ try calculating expected life span of the gear if not possible return  stress cycle factors (YN/ZN)

            :example: helical = HelicalGear(gear_properties)
                      gearbox = Transmission(transmission_properties)
                      gearbox.LifeExpectency(helical, in_hours=True)

            :keyword gear: gear object
            :type gear: Gear
            :keyword in_hours: return gears life expectency in hours
            :type in_hours: bool
            :returns: Number of cycles / work hours
            :rtype: float """

        bending_stress = self.BendingStress(gear)
        contact_stress = self.ContactStress(gear)
        YN = (bending_stress * self.SF * self.Ytheta * self.Yz) / gear.St
        ZN = (contact_stress * self.SH * self.Ytheta * self.Yz) / (gear.Sc * gear.Zw)

        # for YN > 1
        YN_low_cycle = {160: (YN / 2.3194) ** (-1 / 0.0538),
                        250: (YN / 4.9404) ** (-1 / 0.1045),
                        400: (YN / 9.4518) ** (-1 / 0.148)}
        # for YN <= 1
        YN_high_cycle = {True: (YN / 1.6831) ** (-1 / 0.0323),
                         False: (YN / 1.3558) ** (-1 / 0.0178)}

        # for ZN > 1
        ZN_low_cycle = {True: (ZN / 1.249) ** (-1 / 0.0138),
                        False: (ZN / 2.466) ** (-1 / 0.056)}
        # for ZN < 1
        ZN_high_cycle = {True: (ZN / 2.466) ** (-1 / 0.056),
                         False: (ZN / 1.4488) ** (-1 / 0.023)}
        # print(f"YN = {YN}, ZN = {ZN}")
        try:
            # number of cycles until bending failure
            Ny = YN_low_cycle[gear.hardness] if YN > 1 else YN_high_cycle[gear.sensitive_use]

            # number of cycles until contact failure
            Nz = ZN_low_cycle[gear.nitriding] if ZN > 1 else ZN_high_cycle[gear.sensitive_use]

            N = min(Ny, Nz)
            # print(f"Ny={Ny:e}, Nz={Nz:e}")
        except KeyError:
            print(f"error: YN > 1 but hardness {gear.hardness} has no graph associated with it")
            # return YN, ZN
        else:
            # if in_hours True convert number of cycles to house
            # and shorten float length to only 2 decimal places
            return float(f"{N / (gear.rpm * 60):.2f}") if in_hours else N

    def MinimalHardness(self,gear):
        """ return the minimum hardness of the gear to avoid failure """
        # for bending
        St = (self.Ytheta * self.Yz * self.SF * self.BendingStress(gear)) / gear.YN
        if gear.grade == 1:
            # for grade 1
            HBt = (St-88.3)/0.533
        else:
            # for grade 2
            HBt = (St-113)/0.703

        # for contact
        Sc = (self.Ytheta * self.Yz * self.SH * self.BendingStress(gear)) / (gear.ZN * gear.Zw)
        if gear.grade == 1:
            # for grade 1
            HBc = (Sc-200)/2.22
        else:
            # for grade 2
            HBc = (Sc-237)/2.41

        return max(HBt, HBc)

    def Optimize(self, gear, optimize_feature='all', verbose=False):
        """ perform gear optimization

            example: result, results_list = gearbox.Optimize(pinion, optimize_feature='volume', verbose=True)

            note: result of width in [mm], volume in [mm^3] and center distance in [mm]

            :keyword gear: gear object
            :type gear: SpurGear, HelicalGear
            :keyword optimize_feature: property to optimize for ('width'/'volume'/'center')
            :type optimize_feature: str
            :keyword verbose: print optimization stages
            :type verbose: bool
            :return: optimized result and list of other viable options
            :rtype: tuple """

        return gear.Optimization(self, optimize_feature, verbose)

    def CheckUndercut(self):
        """ Checks undercut state """

        phi = radians(self.gear1.pressure_angle)
        invert_mG = 1 / self.gear_ratio
        minimum_teeth_num = 2 * (1 + sqrt(1 + invert_mG * (2 + invert_mG) * sin(phi) ** 2)) / (
                (2 + invert_mG) * sin(phi) ** 2)
        if self.gear1.teeth_num > minimum_teeth_num:
            print("No Undercut")
        else:
            print("Undercut Occurs")

    # for internal use
    def _Zw(self):
        """ Surface strength factor
            Zw dependent on gear1 and gear2 hardness"""
        if self.gear1 is not None:
            HBp = self.gear1.hardness
        else:
            HBp = self.gear2.hardness
        if self.gear2 is not None:
            HBg = self.gear2.hardness
        else:
            HBg = self.gear1.hardness

        ratio = HBp / HBg

        if 1.2 <= ratio < 1.7:
            A = 0.00898 * ratio - 0.00829
        elif ratio >= 1.7:
            A = 0.00698
        else:
            # if ratio < 1.2:
            A = 0

        return 1 + A * (self.gear_ratio - 1)

    def _ContactRatio(self):
        """ calculate contact ratio between the gears and pass it to the each of the gears """

        rp = 0.5 * self.gear1.pitch_diameter
        # check if gear2 is specified
        if self.gear2 is not None:
            rG = 0.5 * self.gear2.pitch_diameter
        else:
            rG = rp * self.gear_ratio
        phi = radians(self.gear1.pressure_angle)
        m = self.gear1.modulus
        p = self.gear1.pitch
        contact_length = sqrt((rG + m) ** 2 - (rG * cos(phi)) ** 2) + sqrt((rp + m) ** 2 - (rp * cos(phi)) ** 2) - (
                rp + rG) * sin(phi)
        contact_ratio = contact_length / (p * cos(phi))
        if contact_ratio < 1.2:
            print("attention: ratio is should be higher than 1.2")

        self.gear1.contact_ratio = contact_ratio
        self.gear2.contact_ratio = contact_ratio

    @staticmethod
    def _Gear2Checkup(gear1, gear2, gear_ratio):
        """ if gear2 object was entered in the class call pass it on if not instantiate it

            :keyword gear1: gear object
            :type gear1: Union[SpurGear, HelicalGear]
            :keyword gear2: gear object
            :type gear2: Union[SpurGear, HelicalGear]
            :keyword gear_ratio: gear ratio
            :type gear_ratio: float """

        if gear2 is None and gear_ratio != 0:
            # create gear2 from gear1 properties and the gear ratio

            # copy gear1 properties
            gear2_prop = gear1.__dict__.copy()
            # change the name, teeth number and rpm according to the gear ratio
            gear2_prop.update(
                {'teeth_num': round(gear1.teeth_num * gear_ratio), 'rpm': gear1.rpm / gear_ratio})

            return gear1.CreateNewGear(gear1.FormatProperties(gear2_prop))

        elif gear2 is not None and gear_ratio == 0:
            # gear2 had been specified
            return gear2
        elif gear2 is not None and gear_ratio != 0:
            # both gear2 and gear ratio entered check if they match
            if gear2.teeth_num / gear1.teeth_num == gear_ratio:
                return gear2
            else:
                # mismatch gear ratio
                raise GearTypeError(f"calculated gear ratio:{gear2.teeth_num / gear1.teeth_num}"
                                    f" not matching specified gear ratio:{gear_ratio}")
        else:
            # gear2 cant be None at the same time gear_ratio is zero
            raise GearTypeError('gear2 and gear_ratio not specified, one of them is needed')
