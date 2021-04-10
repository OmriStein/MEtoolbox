from math import pi, log, sqrt, tan, radians, cos, sin
from tools import table_interpolation
import numpy as np
import os


class GearTypeError(ValueError):
    pass


class SpurGear:
    """A gear object that contains all of its design parameters (AGMA 2001-D04)"""

    # TODO: YN - add solution for low cycle of material not in the graph
    # TODO: Qv - add a way to calculate the Qv value as in AGMA 2001-D04

    def __init__(self, name, modulus, teeth_num, rpm, Qv, width, bearing_span, pinion_offset, enclosure, hardness,
                 pressure_angle, grade, work_hours=0, number_of_cycles=0, crowned=False, adjusted=False,
                 sensitive_use=False, nitriding=False, case_carb=False, material='steel'):
        """ Instantiating a Spurgear object

        :param str name: the name of the gear
        :param float modulus: modulus in [mm]
        :param float pressure_angle: pressure angle in [deg]
        :param int teeth_num: number of teeth
        :param float rpm: angular velocity in [RPM]
        :param int grade: material grade (1 or 2)
        :param int Qv: transmission quality [5<=Qv<=11]
        :param bool crowned: crowned teeth shape ( True / False )
        :param bool adjusted: Adjusted after assembly ( True / False )
        :param float width: gear width in [mm]
        :param float bearing_span: length between the middle of the bearings in [mm]
        :param float pinion_offset: gear offset from the middle of the bearing span in [mm]
        :param strenclosure: type of enclosure
                            (open gearing / commercial enclosed / precision enclosed / extra precision enclosed)
        :param float hardness: gear hardness in Brinell scale [HB]
        :param str material: gear material (steel, malleable iron, nodular iron, cast iron, aluminum bronze, tin bronze)
        :param float work_hours: number of hour of operation in [hr]
        :param float number_of_cycles: number of cycles of operation
        :param bool sensitive_use: if the gear is for sensitive use ( True / False )
        :param bool nitriding: heat treating process ( True / False )

        :returns: A SpurGear object
        :rtype: SpurGear
        """
        # gear properties
        self.name = name
        self.modulus = modulus
        self.teeth_num = teeth_num
        self.rpm = rpm
        self.Qv = Qv
        self.width = width
        self.bearing_span = bearing_span
        self.pinion_offset = pinion_offset
        self.enclosure = enclosure
        self.hardness = hardness
        self.pressure_angle = pressure_angle
        self.grade = grade
        self.crowned = crowned
        self.adjusted = adjusted
        self.sensitive_use = sensitive_use
        self.nitriding = nitriding
        self.case_carb = case_carb
        self.material = material
        self.contact_ratio = None
        self.maximum_velocity = None
        if work_hours != 0:
            self.work_hours = work_hours
        if number_of_cycles != 0:
            self.number_of_cycles = number_of_cycles
        if work_hours == 0 and number_of_cycles == 0:
            raise ValueError('work_hours or number_of_cycles not specified')

    @property
    def pitch_diameter(self):
        """Calculate pitch diameter

        :returns: Gear's pitch diameter
        :rtype: float
        """
        return self.teeth_num * self.modulus  # pitch diameter [mm]

    @property
    def pitch(self):
        """Calculate circular pitch

        :returns: Gear's circular pitch
        :rtype: float
        """
        return self.modulus * pi

    @property
    def tangent_velocity(self):
        """Convert tangent velocity to [m/s] from [rpm]

        :returns: Gear's tangent velocity
        :rtype: float
        """
        return (pi * self.pitch_diameter * self.rpm) / 60e3

    @property
    def KB(self):
        """Rim thickness factor, factor_KB is dependent on the number of teeth


        :returns: Gear's Rim thickness factor
        :rtype: float
        """
        mB = (0.5 * self.teeth_num - 1.25) / 2.25
        if mB < 1.2:
            K_B = 1.6 * log(2.242 / mB)
        else:
            K_B = 1
        return K_B

    @property
    def Kv(self):
        """Dynamic factor, Kv is dependent on the pitch diameter in [mm],
        the angular velocity in [rpm] and Qv (transmission accuracy grade number)

        note: the equations here are from "Shigley's Mechanical Engineering Design"
               in the AGMA standard the transmission accuracy grade number is Av instead of Qv
               and its value is inverted, high Qv is more accurate and high Av is less accurate

        :returns: Gear's Dynamic factor
        :rtype: float
        """
        B = 0.25 * (12 - self.Qv) ** (2 / 3)
        A = 50 + 56 * (1 - B)

        # maximum velocity
        self.maximum_velocity = ((A + (self.Qv - 3)) ** 2) / 200

        if 6 <= self.Qv <= 11:
            K_v = ((A + sqrt(200 * self.tangent_velocity)) / A) ** B
        elif self.Qv == 5:
            K_v = (50 + sqrt(200 * self.tangent_velocity)) / 50
        elif self.Qv == 12:
            K_v = 1
            self.maximum_velocity = "Qv=12 no maximum velocity"
        else:
            raise ValueError(f"at Kv factor: Qv={self.Qv} not in range (5<=Qv<=12)\n")
        return K_v

    @property
    def Ks(self):
        """Size factor, factor_Ks is dependent on the circular pitch (p=πm) which in turn depends on the modulus

        :returns: Gear's size factor
        :rtype: float
        """
        if self.pitch > 8:
            K_s = (1 / 1.189) * (self.pitch ** 0.097)
        else:
            K_s = 1
        return K_s

    @property
    def KH(self):
        """Load distribution factor, KH is dependent on: the shape of teeth (crowned), if teeth are adjusted after assembly (adjusted),
        the gear width in [mm], pitch diameter in [mm], bearing span (the distance between the bearings center lines)
        pinion offset (the distance from the bearing span center to the pinion mid-face)
        enclosure type (open gearing, commercial enclosed, precision enclosed, extra precision enclosed)

        :returns: Gear's load distribution factor
        :rtype: float
        """
        # K_Hmc - lead correction factor
        if self.crowned:
            K_Hmc = 0.8
        else:
            K_Hmc = 1

        # K_He - mesh alignment correction factor
        if self.adjusted:
            K_He = 0.8
        else:
            K_He = 1

        # K_Hpf - mesh alignment correction factor
        # gear width to diameter ratio
        ratio = self.width / (10 * self.pitch_diameter)
        if ratio < 0.05:
            ratio = 0.05

        # print("the width is", b)
        if self.width <= 25:
            K_Hpf = ratio - 0.025
        elif 25 < self.width <= 432:
            K_Hpf = ratio - 0.0375 + 0.000492 * self.width
        elif 432 < self.width <= 1020:
            K_Hpf = ratio - 0.1109 + 0.00815 * self.width - 0.000000353 * self.width ** 2
        else:
            raise ValueError(f"at KH factor: width={self.width} not in range, (width < 1020)\n")

        # K_Hpm - pinion proportion modifier
        s = self.bearing_span
        s1 = self.pinion_offset
        if (s1 / s) < 0.175:
            K_Hpm = 1
        else:
            K_Hpm = 1.1

        # K_Hma - mash alignment factor
        enclosure_type = {'open gearing': [2.47e-1, 0.657e-3, -1.186e-7],
                          'commercial enclosed': [1.27e-1, 0.622e-3, -1.69e-7],
                          'precision enclosed': [0.675e-1, 0.504e-3, -1.44e-7],
                          'extra precision enclosed': [0.380e-1, 0.402e-3, -1.27e-7]}
        K_Hma = enclosure_type[self.enclosure][0] + self.width * enclosure_type[self.enclosure][1] + \
                enclosure_type[self.enclosure][2] * self.width ** 2

        K_H = 1.0 + K_Hmc * (K_Hpf * K_Hpm + K_Hma * K_He)
        return K_H

    @property
    def St(self):
        """Bending safety factor, St is dependent on the gear hardness in [HBN] and the material grade
        (material grade of the gear 1 for regular use 2 for military and sensitive uses)

        :returns: Gear's bending safety factor
        :rtype: float
        """
        if self.grade == 1:
            S_t = 0.533 * self.hardness + 88.3
        elif self.grade == 2:
            S_t = 0.703 * self.hardness + 113
        else:
            raise ValueError(f"at St factor: grade={self.grade} but only 1 or 2 are valid")

        return S_t

    @property
    def Sc(self):
        """Contact safety factor, Sc is dependent on the gear hardness in [HBN] and on the material grade
        (material grade of the gear 1 for regular use 2 for military and sensitive uses)

        :returns: Gear's contact safety factor
        :rtype: float
        """
        if self.grade == 1:
            S_c = 200 + 2.22 * self.hardness
        elif self.grade == 2:
            S_c = 237 + 2.41 * self.hardness
        else:
            raise ValueError(f"at Sc factor: grade={self.grade} but only 1 or 2 are valid")

        return S_c

    @property
    def ZR(self):
        """For now ZR is 1 according to the AGMA standard
        :rtype: int
        """
        return 1

    @property
    def YN(self):
        """Bending strength stress cycle factor

        :returns: Gear's bending strength stress cycle factor
        :rtype: float
        """
        # get the number of cycles of the gear
        N = self.cycles_or_hours()

        if N is None:
            return None

        # 1e2 <= N < 2e6
        low_cycle = {160: 2.3194 * N ** (-0.0538),
                     'Nitrided': 3.517 * N ** (-0.0817),
                     250: 4.9404 * N ** (-0.1045),
                     'Case carb': 6.1514 * N ** (-0.1192),
                     400: 9.4518 * N ** (-0.148)}

        # N>=2e6
        high_cycle = {True: 1.6831 * N ** (-0.0323),
                      False: 1.3558 * N ** (-0.0178)}

        try:
            if 1e2 <= N < 2e6 and self.nitriding:
                curve = 'Nitrided'
            elif 1e2 <= N < 2e6 and self.case_carb:
                curve = 'Case carb'
            else:
                curve = self.hardness

            if 1e2 <= N < 2e6:
                Y_N = low_cycle[curve]
            elif N >= 2e6:
                Y_N = high_cycle[self.sensitive_use]
            else:
                raise ValueError(f" at YN: the number of cycles is {N} but the minimum number is {1e2} ")
            return Y_N
        except KeyError as bad_key:
            print(f"at YN: not a valid hardness {bad_key}")
            return "Error"

    @property
    def ZN(self):
        """Calculating contact strength stress cycle factor

        :returns: Gear's contact strength stress cycle
        :rtype: float
        """
        # get the number of cycles of the gear
        N = self.cycles_or_hours()
        if N is None:
            return None

        # N < 3e6
        low_cycle = {True: 1.249 * N ** (-0.0138),  # nitrided
                     False: 2.466 * N ** (-0.056)}
        # N >= 3e6
        high_cycle = {True: 2.466 * N ** (-0.056),  # for sensitive use
                      False: 1.4488 * N ** (-0.023)}

        return low_cycle[self.nitriding] if N < 3e6 else high_cycle[self.sensitive_use]

    @staticmethod
    def Y_j(gear1, gear2):
        """Return Geometry factors for spur gear and pinion

        :returns: Gear's geometry factor
        :rtype: float
        """
        N1 = gear1.teeth_num
        N2 = gear2.teeth_num
        pressure_angle = gear1.pressure_angle

        # load table according to pressure angle
        if pressure_angle == 20:
            path = os.path.dirname(__file__) + "\\tables\\20deg - spur gear geometry factors.csv"
        elif pressure_angle == 25:
            path = os.path.dirname(__file__) + "\\tables\\25deg - spur gear geometry factors.csv"
        else:
            raise ValueError("at spur gear Yj Factor: pressure angle is wrong")

        data = np.genfromtxt(path, delimiter=',')
        # try:
        gear1.Yj = table_interpolation(N1, N2, data)
        gear2.Yj = table_interpolation(N2, N1, data)
        # except NotInRangeError as not_in_range:
        # print(f"Error: Teeth number of one of the gears ({not_in_range.num}) not in range {not_in_range.range_}")

    def get_info(self):
        """Print all the class fields with values """
        for key in self.__dict__:
            print(f"{key} : {self.__dict__[key]}")

    def get_factors(self, verbose=True):
        """Print correction factors for gear strength analysis

        :param bool verbose: Print factors
        :rtype: dict
        """

        factors = {'factor_KB': self.KB, 'Kv': self.Kv, 'max_vel': self.maximum_velocity, 'factor_Ks': self.Ks, 'KH': self.KH,
                   'St': self.St, 'ZR': self.ZR, 'Sc': self.Sc, 'YN': self.YN, 'ZN': self.ZN,
                   'Yj': self.__dict__.get('Yj', None), 'Zw': self.__dict__.get('Zw', None)}

        if verbose:
            print("factor_KB= {KB}, Kv= {Kv}, maximum velocity= {max_vel}, \
                  \nfactor_Ks= {Ks}, KH= {KH}, St= {St}, ZR= {ZR}, Sc= {Sc}, \
                  \nYN= {YN}, ZN= {ZN}, Yj= {Yj}, Zw= {Zw}".format(**factors))

        if None in factors.values():
            print(f"None value caused by Transmission not been instantiated")

        return factors

    def cycles_or_hours(self):
        """Check if the gear number of cycles or work hours were input and return the number of cycle

        :returns: Gear's Dynamic factor
        :rtype: float or None

        :raise ValueError: number of cycles and work hours entered but they're not matching
            or no number of cycles or work hours entered
        """

        if self.contact_ratio is None:
            return None

        # if attribute don't exist assign zero
        cycles_number = self.__dict__.get("number_of_cycles", 0)
        working_hours = self.__dict__.get("work_hours", 0)

        if cycles_number == 0 and working_hours != 0:
            # calculate number of cycles
            return 60 * working_hours * self.rpm * self.contact_ratio
        elif cycles_number != 0 and working_hours == 0:
            # number of cycle is an input
            return cycles_number
        elif cycles_number != 0 and working_hours != 0:
            # if both were an input check if the match
            if cycles_number == 60 * working_hours * self.rpm * self.contact_ratio:
                return cycles_number
            else:
                raise ValueError("at YN factor: number of cycles and work hours entered but they're not matching")
        else:
            raise ValueError("at YN factor: no number of cycles or work hours entered")

    @staticmethod
    def calc_forces(gear, power):
        """Calculate forces on the gear

        :param SpurGear gear: gear object
        :param float power: power

        :returns: Wt - tangent force in [N], Wr - radial force in [N]
        :rtype: tuple[float, float]
        """

        Wt = (60e3 / pi) * (power / (gear.pitch_diameter * gear.rpm))
        Wr = Wt * tan(radians(gear.pressure_angle))
        return Wt, Wr

    @staticmethod
    def ZI(gear1, gear2):
        """Geometric factor for contact failure, ZI is dependent on the gear ratio and pressure angel

        :param SpurGear gear1: gear object
        :param SpurGear gear2: gear object

        :return: ZI - geometric factor
        :rtype: float
        """

        mG = gear2.teeth_num / gear1.teeth_num
        phi = radians(gear1.pressure_angle)
        Z_I = 0.5 * cos(phi) * sin(phi) * (mG / (mG + 1))
        return Z_I

    def optimization(self, transmission, optimize_feature='all', verbose=False):
        """Perform gear optimization

        :param gears.transmission.Transmission transmission: Transmission object associated with the gears
        :param str optimize_feature: property to optimize for ('width'/'volume'/'center')
        :param bool verbose: print optimization stages

        :return: optimized result (width in mm, volume in mm^3, center distance in mm)
        :rtype: dict
        """

        gear = self

        # saving original attribute values
        original_teeth_num = gear.teeth_num  # saving original attribute
        original_width = gear.width
        original_modulus = gear.modulus

        # choosing the minimum number of teeth to start with
        # (Note: this is the minimum number of teeth to avoid interference)
        if gear.pressure_angle == 20:
            initial_teeth_num = 18

        elif gear.pressure_angle == 25:
            initial_teeth_num = 13

        # elif gear.pressure_angle == 14.5:
        #     initial_teeth_num = 32
        else:
            raise ValueError(f"pressure_angle={gear.pressure_angle} degrees but it can only be 20/25 degrees")

        modulus_list = [0.3, 0.4, 0.5, 0.8, 1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 16, 20, 25]
        modulus_list.sort(reverse=True)

        results_list = []
        for modulus in modulus_list:
            # set gear modulus
            gear.modulus = modulus
            gear.teeth_num = initial_teeth_num  # updating attribute

            # because the width range is (3πm,5πm) the initial guess is 4πm
            initial_width = 4 * pi * transmission.gear_ratio
            gear.width = initial_width

            # print(modulus, initial_teeth_num, initial_width)
            while True:
                # update Yj factors after attribute changed
                transmission.gear1.Y_j(transmission.gear1, transmission.gear2)

                # KH is a function of the gear width, we assumed an initial width of 4πm to calculate KH,
                # we recalculate KH and the width until KH converges
                kh_not_converging = False
                while True:
                    # calculate minimum gear width for bending and contact stress
                    bending_minimum_width = transmission.minimum_width_for_bending(gear)
                    contact_minimum_width = transmission.minimum_width_for_contact(gear)

                    # the new width is the max value of the two minimum width
                    new_width = max(bending_minimum_width, contact_minimum_width)
                    if new_width > 1020:
                        print("error: KH is not converging for m=", modulus)
                        kh_not_converging = True
                        break

                    # save old KH for comparison later
                    oldKH = gear.KH

                    # save new gear width
                    gear.width = new_width

                    # update Yj factors after width changed
                    transmission.gear1.Y_j(transmission.gear1, transmission.gear2)

                    newKH = gear.KH
                    # checking convergence
                    if abs(newKH - oldKH) < 1e-6:
                        break

                # in case KH couldn't converge exit optimization for current modulus
                if kh_not_converging:
                    break

                alpha = contact_minimum_width / bending_minimum_width
                centers_distance = 0.5 * gear.modulus * gear.teeth_num * (transmission.gear_ratio + 1)
                volume = 0.25 * pi * (gear.pitch_diameter ** 2) * gear.width
                f_string = f"m={gear.modulus}, N={gear.teeth_num}, b={gear.width:.2f}," \
                           f"spring_index={centers_distance:.2f}, V={volume:.2f}, α={alpha:.4f}"

                if gear.width < 3 * pi * gear.modulus:
                    # gear width is less than 3πm (b<3πm), gear width should be increased
                    # because the initial teeth number is minimal decrease modulus

                    modulus_list = [0.3, 0.4, 0.5, 0.8, 1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 16, 20, 25]
                    # get previous modulus on the list
                    if gear.modulus > 0.3:
                        new_modulus = modulus_list[modulus_list.index(gear.modulus) - 1]
                    else:
                        raise ValueError(f"at Optimize: b<3πm but the modulus is the lowest possible")

                    if verbose:
                        # printing step result
                        msg = "b<3πm" if gear.tangent_velocity < gear.maximum_velocity else f"b<3πm, v>v_max"
                        print(f_string, ',', msg)

                    # setting changes
                    gear.modulus = new_modulus

                elif gear.width > 5 * pi * gear.modulus:
                    # gear width is more than 5πm (b>5πm), gear width should be decreased
                    # because initial modulus is maximal increase teeth number

                    if verbose:
                        # print step result
                        msg = "b>5πm" if gear.tangent_velocity < gear.maximum_velocity else f"b>5πm, v>v_max"
                        print(f_string, ',', msg)

                    # increasing teeth number by one
                    # (note: the gear teeth number can't exceed the biggest number specified in the Yj factor tables
                    # and for a pinion a number that will make its gear pass this number.
                    # this error is handled at the Yj function)
                    gear.teeth_num += 1
                else:
                    # gear width is within range (3πm<b<5πm)
                    if alpha > 1:
                        # if α>1 increase number of teeth
                        if verbose:
                            # print step result
                            print(f"{f_string}, 3πm<b<5πm, α>1"
                                  if gear.tangent_velocity < gear.maximum_velocity else f"3πm<b<5πm, α>1, v>v_max")

                        # add result to least of viable results
                        results_list.append({'m': gear.modulus, 'N': gear.teeth_num, 'b': gear.width,
                                             'spring_index': centers_distance, 'V': volume, 'alpha': alpha})
                        # increase teeth number
                        gear.teeth_num += 1
                    else:
                        # if α<=1 stop optimization and return the optimized value
                        # and a list of all viable options

                        # print optimization progress
                        if verbose:
                            # print step result
                            print(f"{f_string}, 3πm<b<5πm, α<=1"
                                  if gear.tangent_velocity < gear.maximum_velocity else f"3πm<b<5πm, α<=1, v>v_max")

                        # find optimize feature
                        # optimize by width
                        if optimize_feature == 'width':
                            # create list of widths
                            width_list = [(dic['b'], index) for index, dic in enumerate(results_list)]
                            # get minimum width index
                            result_index = min(width_list)[1]
                            optimized_result = results_list[result_index]

                        # optimize by volume
                        elif optimize_feature == 'volume':
                            # create list of volumes
                            volume_list = [(dic['V'], index) for index, dic in enumerate(results_list)]
                            # get minimum volume index
                            result_index = min(volume_list)[1]
                            optimized_result = results_list[result_index]

                        # optimize by center distance
                        elif optimize_feature == 'center':
                            # create list of center distances
                            center_list = [(dic['spring_index'], index) for index, dic in enumerate(results_list)]
                            # get minimum center distance index
                            result_index = min(center_list)[1]
                            optimized_result = results_list[result_index]

                        elif optimize_feature == 'all':
                            width_list = [(dic['b'], index) for index, dic in enumerate(results_list)]
                            volume_list = [(dic['V'], index) for index, dic in enumerate(results_list)]
                            center_list = [(dic['spring_index'], index) for index, dic in enumerate(results_list)]

                            optimized_result = {'optimized width': results_list[min(width_list)[1]],
                                                'optimized volume': results_list[min(volume_list)[1]],
                                                'optimized center': results_list[min(center_list)[1]]}
                        else:
                            raise Exception(f"optimize_feature={optimize_feature} is invalid")

                        # restore gear parameters
                        gear.teeth_num = original_teeth_num
                        gear.width = original_width
                        gear.modulus = original_modulus

                        return optimized_result, results_list

    def calc_centers_distance(self, gear_ratio):
        """Calculate the distance between the centers of the gears
        :param float gear_ratio: transmissions gear ratio

        :return: the distance between the transmissions gears centers  in [mm]
        :rtype: float
        """
        centers_distance = 0.5 * self.modulus * self.teeth_num * (gear_ratio + 1)
        return centers_distance

    @staticmethod
    def create_new_gear(gear2_prop):
        """Return a new instance of SpurGear

        :param dict gear2_prop: gear properties

        :returns: SpurGear object
        :type: SpurGear
        """
        gear2_prop['name'] = 'spur_gear'
        return SpurGear(**gear2_prop)

    @staticmethod
    def format_properties(properties):
        """Remove excess attributes form properties

        :param list properties: a list of gear properties

        :returns: A dictionary of properties
        :rtype: dict
        """
        prop_list = ['name', 'modulus', 'teeth_num', 'rpm', 'Qv', 'width', 'bearing_span', 'pinion_offset', 'enclosure',
                     'hardness', 'work_hours', 'number_of_cycles', 'pressure_angle', 'grade', 'crowned', 'adjusted',
                     'sensitive_use', 'nitriding', 'case_carb', 'material']
        # remove contact ratio from dictionary so it won't interfere with the new gear instantiation
        new_properties = {key: properties[key] for key in properties if key in prop_list}
        return new_properties

    def check_compatibility(self, gear):
        """Raise error if the pressure angle, helix angle or modulus of the gears don't match

        :param HelicalGear gear: gear object

        :raises ValueError("gear1 and gear2 have mismatch pressure_angle"):
        :raises ValueError("gear1 and gear2 have mismatch Helix_angle"):
        :raises ValueError("gear1 and gear2 are not the same type, they are no compatible"):
        :raises ValueError("gear1 and gear2 have mismatch modulus"):
        """
        if self.pressure_angle != gear.pressure_angle:
            # if pressure angles are different raise error
            raise ValueError("gear1 and gear2 have mismatch pressure_angle")

        if self.modulus != gear.modulus:
            # if modulus are different raise error
            raise ValueError("gear1 and gear2 have mismatch modulus")

        if type(self) is not type(gear):
            raise ValueError("gear1 and gear2 are not the same type, they are no compatible")
