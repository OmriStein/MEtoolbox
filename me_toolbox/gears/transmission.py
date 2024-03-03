"""Module containing the Transmission Class"""
# I want the variables names to be the same as in AGMA pylint: disable=invalid-name
from math import cos, sin, log, sqrt, radians, pi

from me_toolbox.gears import Gear
from me_toolbox.tools import print_atributes


class GearTypeError(ValueError):
    """Error class, inherits from ValueError"""
    pass


class Transmission:
    """ Transmission object containing the transmission design parameters
        and methods to perform strength analysis on its gears. (AGMA 2001-D04)
    """

    # TODO: add advices to improve strength
    # TODO: add function to find minimum volume for contact and bending
    # TODO: add gear train calculation, including multiple stages

    def __init__(self, driving_machine, driven_machine, oil_temp, reliability,
                 power, SF, gear1, gear2=None, gear_ratio=0, SH=1):
        """
        :param Gear gear1: gear object (the driving gear by convention)
        :param Gear or None gear2: gear object (the driven gear by convention)
        :param str driving_machine: ('uniform' - Electric Motor/Turbine,
            'light shock' - multi-cylinder engine, 'medium shock' - single-cylinder engine)
        :param str driven_machine: (uniform / moderate shock / heavy shock)
        :param int oil_temp: oil temperature of the transmission in [deg spring_index]
        :param float reliability: reliability of the transmission
        :str float power: transmission power in [W]
        :param float SF: bending safety factor
        :keyword float SH: contact safety factor
        :keyword float gear_ratio: transmission gear ratio

        :returns: Transmission object
        :rtype: Transmission
        """
        if (type(gear1) is not type(gear2)) and (gear2 is not None):
            raise GearTypeError("gears entered to Transmission are not of the same type")

        self.gear1 = gear1
        self.gear2 = self._gear2_checkup(gear1, gear2, gear_ratio)

        # check if the pressure angle and modulus match between gear1 and gear2
        gear1.check_compatibility(self.gear2)

        self.driving_machine = driving_machine
        self.driven_machine = driven_machine
        self.oil_temp = oil_temp
        self.reliability = reliability
        self.power = power
        self.SF = SF
        self.SH = SH
        self.gear_ratio = gear_ratio
        self._contact_ratio()
        self.gear1.Y_j(self.gear1, self.gear2)
        self.gear1.Zw = 1  # the pinion's Zw is 1 by the AGMA standard
        self.gear2.Zw = self._Zw()
        self.ZI = gear1.ZI(self.gear1, self.gear2)

    def get_info(self):
        """print all the class fields with values"""
        print_atributes(self)

    def get_factors(self, verbose=True):
        """ retrieve transmission analysis factors

        :param bool verbose: print factors
        :type verbose: bool
        :rtype: dict
        """
        if verbose:
            print(f"Ko={self.Ko}, Yθ={self.Ytheta}, Yz=, {self.Yz}, ZE={self.ZE}, ZI={self.ZI}")

        return {"Ko=": self.Ko, "Yθ=": self.Ytheta, "Yz=": self.Yz, "ZE=": self.ZE, "ZI=": self.ZI}

    @property
    def Ytheta(self):
        """Returns temperature factor"""

        if self.oil_temp > 71:
            y_theta = (273 + self.oil_temp) / 344
        else:
            y_theta = 1
        return y_theta

    @property
    def Ko(self):
        """ Returns overload factor
        Ko is dependent on the type of driving motor type
        (Electric Motor/Turbine - uniform, multi-cylinder engine - light shock,
        single-cylinder engine - medium shock) and on the driven machine type
        (uniform, moderate shock, heavy shock)
        """
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
        """Returns reliability factor"""
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
        """returns the elastic coefficient"""
        elastic_modulus_list = {'steel': 2e5, 'malleable iron': 1.7e5,
                                'nodular iron': 1.7e5, 'cast iron': 1.5e5,
                                'aluminum bronze': 1.2e5, 'tin bronze': 1.1e5}

        material1 = self.gear1.material
        material2 = self.gear2.material

        E1 = elastic_modulus_list.get(material1, material1)
        E2 = elastic_modulus_list.get(material2, material2)

        poissons_ratio = 1 / 3
        try:
            return sqrt(
                (1 / pi) / (((1 - poissons_ratio ** 2) / E1) + ((1 - poissons_ratio ** 2) / E2)))
        except TypeError:
            print(f"error: at ZE: invalid gear material ({material1} or {material2})")

    @property
    def centers_distance(self):
        """Returns the distance between the gear's centers"""
        return self.gear1.calc_centers_distance(self.gear_ratio)

    # bending stress related methods
    def bending_stress(self, gear):
        """Calculating bending stress

        :param Gear gear: gear object

        :returns: Bending stress
        :rtype: float
        """
        N = gear.teeth_num
        b = gear.width
        d = gear.pitch_diameter
        Yj = gear.Yj
        Wt = gear.calc_forces(gear, self.power)[0]
        sigma = (Wt * N * self.Ko * gear.Kv * gear.Ks * gear.KH * gear.KB) / (
                    Yj * b * d)
        return sigma

    def allowed_bending_stress(self, gear):
        """Calculating allowed bending stress

        :para Gear gear: gear object

        :returns: Allowed bending stress
        :rtype: float
        """
        allowed_bending_stress = (gear.St * gear.YN) / (self.Ytheta * self.Yz * self.SF)
        return allowed_bending_stress

    def minimum_width_for_bending(self, gear):
        """Calculating minimum gear width to withstand bending stress

        :keyword Gear gear: gear object

        :returns: Minimum gear width
        :rtype: float
        """
        Yj = gear.Yj
        N = gear.teeth_num
        d = gear.pitch_diameter

        allowed_bending = self.allowed_bending_stress(gear)
        Wt = gear.calc_forces(gear, self.power)[0]
        minimum_gear_width = ((Wt * N * self.Ko * gear.Kv * gear.Ks * gear.KH *
                               gear.KB) / (Yj * allowed_bending * d))
        return minimum_gear_width

    # contact stress related methods
    def contact_stress(self, gear):
        """Calculating contact stress

        :param Gear gear: gear object

        :returns: Contact stress
        :rtype: float
        """
        b = gear.width
        d = gear.pitch_diameter
        Wt = gear.calc_forces(gear, self.power)[0]

        sigma = sqrt((Wt * (self.ZE ** 2) * self.Ko * gear.Kv * gear.Ks * gear.KH * gear.ZR)
                     / (b * d * self.ZI))
        return sigma

    def allowed_contact_stress(self, gear):
        """Calculating allowed contact stress

        :param Gear gear: gear object

        :returns: Allowed contact stress
        :rtype: float
        """
        allowed_contact_stress = (gear.Sc * gear.ZN * gear.Zw) / (self.Ytheta * self.Yz * self.SH)
        return allowed_contact_stress

    def minimum_width_for_contact(self, gear):
        """Calculating minimum gear width to withstand contact stress

        :param Gear gear: gear object

        :returns: Minimum gear width
        :rtype: float
        """
        Wt = gear.calc_forces(gear, self.power)[0]
        d = gear.pitch_diameter
        allowed_contact = self.allowed_contact_stress(gear)
        Kv = gear.Kv
        Ks = gear.Ks
        KH = gear.KH
        ZR = gear.ZR

        minimum_gear_width = ((Wt * self.ZE ** 2 * self.Ko * Kv * Ks * KH * ZR) /
                              (d * self.ZI * allowed_contact ** 2))
        return minimum_gear_width

    # for both bending and contact stresses
    def life_expectency(self, gear, in_hours=False):
        """Calculates expected life span of the gear,
         if not possible return  stress cycle factors (YN/ZN)

        :example: helical = HelicalGear(gear_properties)
                  gearbox = Transmission(transmission_properties)
                  gearbox.LifeExpectency(helical, in_hours=True)

        :param Gear gear: gear object
        :param bool in_hours: return gears life expectency in hours

        :returns: Number of cycles or work hours
        :rtype: float
        """

        bending_stress = self.bending_stress(gear)
        contact_stress = self.contact_stress(gear)
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

    def minimal_hardness(self, gear):
        """Returns the minimal hardness of the gear to avoid failure

        :param Gear gear: Gear object

        :returns: Minimal hardness
        :rtype: float
        """
        # for bending
        St = (self.Ytheta * self.Yz * self.SF * self.bending_stress(gear)) / gear.YN
        if gear.grade == 1:
            # for grade 1
            HBt = (St - 88.3) / 0.533
        else:
            # for grade 2
            HBt = (St - 113) / 0.703

        # for contact
        Sc = (self.Ytheta * self.Yz * self.SH * self.bending_stress(gear)) / (gear.ZN * gear.Zw)
        if gear.grade == 1:
            # for grade 1
            HBc = (Sc - 200) / 2.22
        else:
            # for grade 2
            HBc = (Sc - 237) / 2.41

        return max(HBt, HBc)

    def optimize(self, gear, optimize_feature='all', verbose=False):
        """ perform gear optimization

        example: result, results_list = gearbox.Optimize(pinion, optimize_feature='width')

        note: result of width in [mm], volume in [mm^3] and center distance in [mm]

        :param Gear gear: gear object
        :param str optimize_feature: property to optimize for ('width'/'volume'/'center')
        :param bool verbose: print optimization stages

        :returns: An optimized result and list of other viable options
        :rtype: tuple
        """
        return gear.optimization(self, optimize_feature, verbose)

    def check_undercut(self):
        """Checks undercut state """

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
        """Surface strength factor"""
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

    def _contact_ratio(self):
        """Calculate contact ratio between the gears
        and assign it to the gear's attributes
        """
        rp = 0.5 * self.gear1.pitch_diameter
        # check if gear2 is specified
        if self.gear2 is not None:
            rG = 0.5 * self.gear2.pitch_diameter
        else:
            rG = rp * self.gear_ratio
        phi = radians(self.gear1.pressure_angle)
        m = self.gear1.modulus
        p = self.gear1.pitch
        contact_length = (sqrt((rG + m) ** 2 - (rG * cos(phi)) ** 2) +
                          sqrt((rp + m) ** 2 - (rp * cos(phi)) ** 2) - (rp + rG) * sin(phi))
        contact_ratio = contact_length / (p * cos(phi))
        if contact_ratio < 1.2:
            print("attention: ratio is should be higher than 1.2")

        self.gear1.contact_ratio = contact_ratio
        self.gear2.contact_ratio = contact_ratio

    @staticmethod
    def _gear2_checkup(gear1, gear2, gear_ratio):
        """Instantiate gear2 object if it wasn't given

        :param Gear gear1: gear object
        :param Gear or None gear2: gear object
        :param float gear_ratio: gear ratio

        :returns: Gear2 object
        :rtype: Gear
        """

        if gear2 is None and gear_ratio != 0:
            # create gear2 from gear1 properties and the gear ratio

            # copy gear1 properties
            gear2_prop = gear1.__dict__.copy()
            # change the name, teeth number and rpm according to the gear ratio
            gear2_prop.update(
                {'teeth_num': round(gear1.teeth_num * gear_ratio), 'rpm': gear1.rpm / gear_ratio})

            return gear1.create_new_gear(gear1.format_properties(gear2_prop))

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

    @staticmethod
    def train_value(*gear_pairs):
        """Returns transmission train value
        (which is the inverse of the transmission value)
        the input should be an iterable of two gears
        each of them can be either int or Gear obj

        Note: A negative sign indicates direction change of rotation

        Example:
            >> N1, N2, N3, N4 = 10, 20, 50, 10
            >> e = gearbox.train_value((N1, N2), (N3, N4)))

        :param gear_pairs: iterable of two gears
        """
        t_val = 1
        for gears in gear_pairs:
            if hasattr(gears, '__iter__'):
                N1 = gears[0].teeth_num if isinstance(gears[0], Gear) else gears[0]
                N2 = gears[1].teeth_num if isinstance(gears[1], Gear) else gears[1]
                t_val *= -(N1 / N2)
            else:
                raise TypeError("Gear pair can only be iterables")
        return t_val
