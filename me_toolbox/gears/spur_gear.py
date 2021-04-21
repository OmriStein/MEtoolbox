"""Module containing the SpurGear class"""
# I want the variables names to be the same as in AGMA pylint: disable=invalid-name
from math import pi, radians, cos, sin

from me_toolbox.gears.gear import Gear


class SpurGear(Gear):
    """A gear object that contains all of its design parameters (AGMA 2001-D04)"""

    # TODO: YN - add solution for low cycle of material not in the graph
    # TODO: Qv - add a way to calculate the Qv value as in AGMA 2001-D04

    def __init__(self, modulus, teeth_num, rpm, Qv, width, bearing_span, pinion_offset, enclosure,
                 hardness, pressure_angle, grade, work_hours=0, number_of_cycles=0, crowned=False,
                 adjusted=False, sensitive_use=False, nitriding=False, case_carb=False,
                 material='steel'):
        """ Instantiating SpurGear object

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
        :param str enclosure: type of enclosure
                            (open gearing / commercial enclosed / precision enclosed /
                            extra precision enclosed)
        :param float hardness: gear hardness in Brinell scale [HB]
        :param str material: gear material (steel, malleable iron, nodular iron, cast iron,
            aluminum bronze, tin bronze)
        :param float work_hours: number of hour of operation in [hr]
        :param float number_of_cycles: number of cycles of operation
        :param bool sensitive_use: if the gear is for sensitive use ( True / False )
        :param bool nitriding: heat treating process ( True / False )

        :returns: A SpurGear object
        :rtype: SpurGear
        """
        super().__init__(modulus, teeth_num, rpm, Qv, width, bearing_span, pinion_offset, enclosure,
                         hardness, pressure_angle, grade, work_hours, number_of_cycles, crowned,
                         adjusted, sensitive_use, nitriding, case_carb, material)

    def get_info(self):
        """Print all the class fields with values """
        for key in self.__dict__:
            print(f"{key} : {self.__dict__[key]}")

    def get_factors(self, verbose=True):
        """Print correction factors for gear strength analysis

        :param bool verbose: Print factors
        :rtype: dict
        """

        factors = {'factor_KB': self.KB, 'Kv': self.Kv, 'max_vel': self.maximum_velocity,
                   'factor_Ks': self.Ks, 'KH': self.KH, 'St': self.St, 'ZR': self.ZR, 'Sc': self.Sc,
                   'YN': self.YN, 'ZN': self.ZN, 'Yj': self.__dict__.get('Yj', None),
                   'Zw': self.__dict__.get('Zw', None)}

        if verbose:
            print("factor_KB= {KB}, Kv= {Kv}, maximum velocity= {max_vel}, \
                  \nfactor_Ks= {Ks}, KH= {KH}, St= {St}, ZR= {ZR}, Sc= {Sc}, \
                  \nYN= {YN}, ZN= {ZN}, Yj= {Yj}, Zw= {Zw}".format(**factors))

        if None in factors.values():
            print("None value caused by Transmission not been instantiated")

        return factors

    @staticmethod
    def ZI(gear1, gear2):
        """Geometric factor for contact failure,
        ZI is dependent on the gear ratio and pressure angel

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

        :param gears.transmission.Transmission transmission: Transmission object
            associated with the gears
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
            raise ValueError(f"pressure_angle={gear.pressure_angle} "
                             f"degrees but it can only be 20/25 degrees")

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

                # KH is a function of the gear width,
                # we assumed an initial width of 4πm to calculate KH,
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
                centers_distance = 0.5 * gear.modulus * gear.teeth_num * (
                        transmission.gear_ratio + 1)
                volume = 0.25 * pi * (gear.pitch_diameter ** 2) * gear.width
                f_string = f"m={gear.modulus}, N={gear.teeth_num}, b={gear.width:.2f}," \
                           f"spring_index={centers_distance:.2f}, V={volume:.2f}, α={alpha:.4f}"

                if gear.width < 3 * pi * gear.modulus:
                    # gear width is less than 3πm (b<3πm), gear width should be increased
                    # because the initial teeth number is minimal decrease modulus

                    modulus_list = [0.3, 0.4, 0.5, 0.8, 1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12,
                                    16, 20, 25]
                    # get previous modulus on the list
                    if gear.modulus > 0.3:
                        new_modulus = modulus_list[modulus_list.index(gear.modulus) - 1]
                    else:
                        raise ValueError(
                            "at Optimize: b<3πm but the modulus is the lowest possible")

                    if verbose:
                        # printing step result
                        v = gear.tangent_velocity
                        v_max = gear.maximum_velocity
                        msg = "b<3πm" if v < v_max else "b<3πm, v>v_max"
                        print(f_string, ',', msg)

                    # setting changes
                    gear.modulus = new_modulus

                elif gear.width > 5 * pi * gear.modulus:
                    # gear width is more than 5πm (b>5πm), gear width should be decreased
                    # because initial modulus is maximal increase teeth number

                    if verbose:
                        # print step result
                        v = gear.tangent_velocity
                        v_max = gear.maximum_velocity
                        msg = "b>5πm" if v < v_max else "b>5πm, v>v_max"
                        print(f_string, ',', msg)

                    # increasing teeth number by one
                    # (note: the gear teeth number can't exceed the
                    # biggest number specified in the Yj factor tables
                    # and for a pinion a number that will make its gear pass this number.
                    # this error is handled at the Yj function)
                    gear.teeth_num += 1
                else:
                    # gear width is within range (3πm<b<5πm)
                    if alpha > 1:
                        # if α>1 increase number of teeth
                        if verbose:
                            # print step result
                            v = gear.tangent_velocity
                            v_max = gear.maximum_velocity
                            print(f"{f_string}, 3πm<b<5πm, α>1" if v < v_max
                                  else "3πm<b<5πm, α>1, v>v_max")

                        # add result to least of viable results
                        results_list.append(
                            {'m': gear.modulus, 'N': gear.teeth_num, 'b': gear.width,
                             'spring_index': centers_distance, 'V': volume, 'alpha': alpha})
                        # increase teeth number
                        gear.teeth_num += 1
                    else:
                        # if α<=1 stop optimization and return the optimized value
                        # and a list of all viable options

                        # print optimization progress
                        if verbose:
                            # print step result
                            v = gear.tangent_velocity
                            v_max = gear.maximum_velocity
                            print(f"{f_string}, 3πm<b<5πm, α<=1" if v < v_max
                                  else "3πm<b<5πm, α<=1, v>v_max")

                        # find optimize feature
                        # optimize by width
                        if optimize_feature == 'width':
                            # create list of widths
                            width_list = [(dic['b'], index) for index, dic in
                                          enumerate(results_list)]
                            # get minimum width index
                            result_index = min(width_list)[1]
                            optimized_result = results_list[result_index]

                        # optimize by volume
                        elif optimize_feature == 'volume':
                            # create list of volumes
                            volume_list = [(dic['V'], index) for index, dic in
                                           enumerate(results_list)]
                            # get minimum volume index
                            result_index = min(volume_list)[1]
                            optimized_result = results_list[result_index]

                        # optimize by center distance
                        elif optimize_feature == 'center':
                            # create list of center distances
                            center_list = [(dic['spring_index'], index) for index, dic in
                                           enumerate(results_list)]
                            # get minimum center distance index
                            result_index = min(center_list)[1]
                            optimized_result = results_list[result_index]

                        elif optimize_feature == 'all':
                            width_list = [(dic['b'], index) for index, dic in
                                          enumerate(results_list)]
                            volume_list = [(dic['V'], index) for index, dic in
                                           enumerate(results_list)]
                            center_list = [(dic['spring_index'], index) for index, dic in
                                           enumerate(results_list)]

                            optimized_result = {'optimized width': results_list[min(width_list)[1]],
                                                'optimized volume': results_list[
                                                    min(volume_list)[1]],
                                                'optimized center': results_list[
                                                    min(center_list)[1]]}
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
        """Return new instance of SpurGear

        :param dict gear2_prop: gear properties

        :returns: SpurGear object
        :type: SpurGear
        """
        return SpurGear(**gear2_prop)

    @staticmethod
    def format_properties(properties):
        """Remove excess attributes form properties

        :param list properties: list of gear properties

        :returns: A dictionary of properties
        :rtype: dict
        """
        prop_list = ['modulus', 'teeth_num', 'rpm', 'Qv', 'width', 'bearing_span',
                     'pinion_offset', 'enclosure',
                     'hardness', 'work_hours', 'number_of_cycles', 'pressure_angle', 'grade',
                     'crowned', 'adjusted',
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
