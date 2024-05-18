"""module containing the FatigueAnalysis class and
calc_kf for calculating dynamic stress concentration factor
"""
from math import log10, inf
from sympy import sqrt

from me_toolbox.tools import print_atributes
from me_toolbox.fatigue import FailureCriteria

from icecream import ic

class FatigueAnalysis:
    """Perform fatigue analysis"""

    def __init__(self, modified_endurance_limit, stress_type, ductile, ultimate_tensile_strength,
                 yield_strength=None, Kf_bending=0, Kf_normal=0, Kf_torsion=0,
                 alt_bending_stress=0, alt_normal_stress=0, alt_torsion_stress=0,
                 mean_bending_stress=0, mean_normal_stress=0, mean_torsion_stress=0):
        """ Instantiating fatigue object
        Note: all stresses are in [MPa]
        :param float modified_endurance_limit: The modified endurance limit (Se)
        :type str stress_type: Type of stress loading (bending', 'axial', 'torsion', 'shear', 'multiple')
        :param bool ductile: True if material is ductile
        :type ultimate_tensile_strength: Ultimate tensile strength (Sut) of the material in [MPa]
        :param float yield_strength: Yield strength in [MPa]
        :param float Kf_bending: dynamic stress concentration factor for bending
        :param Kf_normal: dynamic stress concentration factor for normal
        :param Kf_torsion: dynamic stress concentration factor for torsion
        :param float alt_bending_stress: Alternating bending stress
        :param float alt_normal_stress: Alternating normal stress
        :param float alt_torsion_stress: Alternating torsion stress
        :param float mean_bending_stress: Mean bending stresses
        :param float mean_normal_stress: Mean normal stresses
        :param float mean_torsion_stress: Mean torsion stresses
        """

        self.Sy = yield_strength
        self.Se = modified_endurance_limit
        self.Sut = ultimate_tensile_strength
        self.stress_type = stress_type
        self.ductile = ductile
        self.Kf_bending, self.Kf_normal, self.Kf_torsion = Kf_bending, Kf_normal, Kf_torsion
        self.alt_bending_stress = alt_bending_stress
        self.alt_normal_stress = alt_normal_stress
        self.alt_torsion_stress = alt_torsion_stress
        self.mean_bending_stress = mean_bending_stress
        self.mean_normal_stress = mean_normal_stress
        self.mean_torsion_stress = mean_torsion_stress
        self.alt_eq_stress = self.calc_alt_eq_stress()
        self.mean_eq_stress = self.calc_mean_eq_stress()

    @staticmethod
    def calc_kf(q, Kt):
        """Calculating the dynamic stress concentration factor (Kf)
        (this calculation is the same for the shear concentration factor)

        :param float Kt: stress concentration theoretical factor
        :param float q: notch Sensitivity

        :returns: dynamic stress concentration factor
        :rtype: float
        """
        return 1 + q * (Kt - 1)

    @staticmethod
    def calc_thread_kf(grade, manufacturing):
        """Calculating the dynamic stress concentration factor (Kf) for threads

        :param float grade: The grade of the bolt
        :param string manufacturing: Manufacturing methode 'Rolled Threads' or 'Cut Threads'

        :returns: dynamic stress concentration factor for threads
        :rtype: float
        """
        if manufacturing != "Rolled Threads" and manufacturing != "Cut Threads":
            raise ValueError(f"The only exceptable manufacturing methods are 'Rolled Threads' and "
                             f"'Cut Threads'")
        if 3.6 <= grade <= 5.8:
            options = {"Rolled Threads": 2.2, "Cut Threads": 2.8}
        elif 6.6 <= grade <= 10.9:
            options = {"Rolled Threads": 3, "Cut Threads": 3.8}
        else:
            raise ValueError(f"Grade entered is {grade} but grade can only be in the range of"
                             f"3.6 to 5.8 or 6.6 to 0.9")
        return options[manufacturing]

    def calc_alt_eq_stress(self):
        """Returns the alternating equivalent stress according to the load type indicated by Kc

        :returns: Alternating equivalent stress
        :rtype: float
        """

        if self.stress_type == 'multiple':
            corrected_bending = self.Kf_bending * self.alt_bending_stress
            corrected_normal = self.Kf_normal * (self.alt_normal_stress / 0.85)
            corrected_torsion = self.Kf_torsion * self.alt_torsion_stress
            return sqrt((corrected_bending + corrected_normal) ** 2 + 3 * corrected_torsion ** 2)

        elif self.stress_type == 'bending':
            return self.Kf_bending * self.alt_bending_stress

        elif self.stress_type == 'axial':
            return self.Kf_normal * self.alt_normal_stress

        elif self.stress_type == 'torsion' or self.stress_type == 'shear':
            return self.Kf_torsion * self.alt_torsion_stress

    def calc_mean_eq_stress(self):
        """Returns the mean equivalent stress according to the load type indicated by Kc

        :returns: Mean equivalent stress
        :rtype: float
        """
        if self.ductile:
            # if the material is ductile no correction is needed
            Kf_bending, Kf_normal, Kf_torsion = 1, 1, 1
        else:
            Kf_bending, Kf_normal, Kf_torsion = self.Kf_bending, self.Kf_normal, self.Kf_torsion

        if self.stress_type == 'multiple':
            corrected_bending = Kf_bending * self.mean_bending_stress
            corrected_normal = Kf_normal * self.mean_normal_stress
            corrected_torsion = Kf_torsion * self.mean_torsion_stress

            return sqrt((corrected_bending + corrected_normal) ** 2 + 3 * corrected_torsion ** 2)

        elif self.stress_type == 'bending':
            return Kf_bending * self.mean_bending_stress

        elif self.stress_type == 'axial':
            return Kf_normal * self.mean_normal_stress

        elif self.stress_type == 'torsion' or self.stress_type == 'shear':
            return Kf_torsion * self.mean_torsion_stress

    @property
    def shear_ultimate_strength(self):
        """Returns shear_ultimate_strength which is the
        ultimate_tensile_strength correction for shear stress

        :returns: Sst - ultimate shear tensile strength
        :type: float
        """
        return 0.67 * self.Sut

    @property
    def shear_yield_stress(self):
        """Returns shear_yield_strength which is the Sy correction for shear stress

        :returns: shear_yield_strength - yield stress for shear
        :type: float
        """
        return self.Sy / sqrt(3).evalf()

    @property
    def modified_goodman(self):
        """Safety factor according to modified Goodman failure criterion
        (very common criterion)

        :returns: Safety factor
        :rtype: any

        :raises ValueError: if ultimate_tensile_strength is not in the fatigue call
        """

        if self.mean_eq_stress < 0:
            return None

        ultimate_strength = self.Sut
        if self.stress_type == 'torsion' or self.stress_type == 'shear':
            # ultimate_tensile_strength correction for shear stress
            ultimate_strength = self.shear_ultimate_strength

        return FailureCriteria.modified_goodman(ultimate_strength, self.Se,
                                                self.alt_eq_stress,
                                                self.mean_eq_stress)

    @property
    def soderberg(self):
        """Safety factor according to Soderberg failure criterion
        (the safest criterion)

        :returns: Safety factor
        :rtype: any

        :raises ValueError: if Sy is not in the fatigue call
        """

        if self.mean_eq_stress < 0:
            return None

        yield_strength = self.Sy
        if self.stress_type == 'torsion' or self.stress_type == 'shear':
            # ultimate_tensile_strength correction for shear stress
            yield_strength = self.shear_yield_stress

        return FailureCriteria.soderberg(yield_strength, self.Se,
                                         self.alt_eq_stress,
                                         self.mean_eq_stress)

    @property
    def gerber(self):
        """Safety factor according to Gerber failure criterion
        (the most lenient criterion)

        :returns: Safety factor
        :rtype: any
        :raises ValueError: if ultimate_tensile_strength is not in the fatigue call
        """

        if self.mean_eq_stress < 0:
            return None

        ultimate_strength = self.Sut
        if self.stress_type == 'torsion' or self.stress_type == 'shear':
            # ultimate_tensile_strength correction for shear stress
            ultimate_strength = self.shear_ultimate_strength

        return FailureCriteria.gerber(ultimate_strength, self.Se,
                                      self.alt_eq_stress,
                                      self.mean_eq_stress)

    @property
    def ASME_elliptic(self):
        """Safety factor according to ASME Failure criterion

        :returns: Safety factor
        :rtype: any

        :raises ValueError: if ultimate_tensile_strength is not in the fatigue call
        """

        if self.mean_eq_stress < 0:
            return None

        yield_strength = self.Sut
        if self.stress_type == 'torsion' or self.stress_type == 'shear':
            # ultimate_tensile_strength correction for shear stress
            yield_strength = self.shear_yield_stress

        return FailureCriteria.asme_elliptic(yield_strength, self.Se, self.alt_eq_stress,
                                             self.mean_eq_stress)

    @property
    def langer_static_yield(self):
        """ Static safety factor according to Langer Failure criterion
        it's customary to use Langer, as an assessment to yielding in the first cycle

        :returns: Safety factor
        :rtype: any

        :raises ValueError: if Sy is not in the fatigue call
        """

        yield_strength = self.Sy
        if self.stress_type == 'torsion' or self.stress_type == 'shear':
            # yield_strength correction for shear stress
            Ssy = 0.67 * self.Sut
            yield_strength = Ssy

        return FailureCriteria.langer_static_yield(yield_strength,
                                                   self.alt_eq_stress,
                                                   self.mean_eq_stress)

    def get_safety_factors(self, criterion, verbose=False):
        """Returns dynamic and static safety factors
        according to the quadrant in the alternating-mean
        stress plain where the stresses are in

        Note: Should always be used instead of accessing the
        individual safety factors properties directly because it takes into account the
        stress direction

        :param str criterion: The criterion to use (modified goodman, soderberg, gerber,
         asme-elliptic)
        :param bool verbose: Print the result

        :returns: dynamic and static safety factors
        :rtype: tuple[float, float]
        """

        return FailureCriteria.get_safety_factors(self.Sy, self.Sut, self.Se, self.alt_eq_stress,
                                                  self.mean_eq_stress, criterion, verbose)

    @property
    def Sm_stress(self):
        """Getter for the Sm_stress (at 1e3 cycles) property

        :returns: Sm - stress at 1e3 cycles
        :rtype: float
        """
        return self.calc_Sm(self.Sut)

    @staticmethod
    def calc_Sm(Sut):
        """Calculate Sm_stress which is the stress at 1e3 cycles, the boundary
        dividing Low cycle fatigue and high cycle fatigue

        :param Sut: Ultimate tensile strength

        :returns: Sm_stress stress
        :rtype: float
        """

        def f(x):
            """ f - fatigue strength fraction
                function constructed from curve fitting to the f graph in Shigley's
                the range of the fit is ( 70[kPsi] < ultimate_tensile_strength < 200[kPsi] ) """
            return (-2.56710686e-16 * x ** 5 + 1.35729780e-12 * x ** 4 - 2.92474777e-09 * x ** 3 +
                    3.28990748e-06 * x ** 2 - 2.04929617e-03 * x + 1.38405394e+00)

        # TODO: add proper warning and solutions to ultimate_tensile_strength out of graph range
        if Sut < 482.633:  # 482.633[Mpa] = 70[kPsi]
            # print(f"Note: ultimate_tensile_strength={Sut} < 482.633[Mpa] (70[kPsi]) so f~0.9")
            return 0.9 * Sut
        elif Sut > 1378.95:
            # print(
            #     f"Note: ultimate_tensile_strength={Sut} > 1378.95[Mpa] (200[kPsi]) which is out of "
            #     f"the graph range, f={f(Sut)}")
            return  0.75 * Sut
        return f(Sut) * Sut

    def num_of_cycles(self, z=-3):
        """Returns the number of cycles until failure

        Note: zeta = log(N1) - log(N2)
              N1 - number of cycles at Sm,
              N2 - Number of cycles at Se (for steel N1=1e3 and N2 = 1e6 -> z=-3)

        :param float z: -3 for steel where N=1e6, -5 for metal where N=1e8,
            -5.69 for metal where N=5e8

        :returns: The Number of cycles and the fatigue stress at failure
        :rtype: tuple[float, float]
        """
        return self.calc_num_of_cycles(self.mean_eq_stress, self.alt_eq_stress, self.Se, self.Sut,
                                       self.Sy, z=-3)

    @staticmethod
    def calc_num_of_cycles(mean_eq_stress, alt_eq_stress, endurance_limit,
                           ultimate_tensile_strength, yield_strength, z=-3):
        """ calculate number of cycles until failure

        Note: zeta = log(N1) - log(N2)
              N1 - number of cycles at Sm,
              N2 - Number of cycles at Se (for steel N1=1e3 and N2 = 1e6 -> z=-3)

        :param mean_eq_stress: Mean equivalent stresses
        :param alt_eq_stress: Alternating equivalent stresses
        :param endurance_limit: Endurance limit
        :param ultimate_tensile_strength: Ultimate tensile strength
        :param yield_strength: Yield Strength
        :param float z: -3 for steel where N=1e6, -5 for metal where N=1e8,
            -5.69 for metal where N=5e8

        :returns: The Number of cycles and the fatigue stress at failure
        :rtype: tuple[float, float] or tuple[float, None]
        """
        mean_stress = mean_eq_stress
        alternating_stress = alt_eq_stress
        Se = endurance_limit
        Sut = ultimate_tensile_strength
        Sy = yield_strength
        Sm = FatigueAnalysis.calc_Sm(Sut)

        # if mean_stress is larger or equal to Sut then the reversible_stress is either negative or
        # undefined because of a division by zero error
        if mean_stress >= Sut:
            return 0, None

        # calculating the reversible stress (σ_rev)
        if mean_stress >= 0:
            reversible_stress = alternating_stress / (1 - (mean_stress / Sut))
        else:
            reversible_stress = alternating_stress


        # Low Cycle Fatigue
        if Sm < reversible_stress < Sy:
            if z != -3:
                raise ValueError(f"Number of cycles calculation for low cycle fatigue"
                                 f" is only possible for zeta=-3")

            a = Sut
            b = (1 / z) * log10(Sut / Sm)

        # High Cycle Fatigue
        elif Se < reversible_stress < Sm:
            a = Sm * (Sm / Se) ** (-3 / z)
            b = (1 / z) * log10(Sm / Se)

        elif reversible_stress < Se:
            return inf, None  # inf is from math module - short for infinity
        else:
            return  0, None
        N = (reversible_stress / a) ** (1 / b)
        return N, a * N ** b

    def miner_rule(self, stress_groups, Sut, Se, Sy=None, z=-3, verbose=False,
                   alt_mean=False, freq=False):
        """ Calculates total number of cycles for multiple periodic loads,
        the stress_groups format is as follows:
        [number_of_repetitions, maximum_stress, minimum_stress]

        Note: number_of_repetitions = frequency [Hz] * time

        Note: if the material don't have fatigue limit use the fatigue strength at Se=Sf(N=1e8)

        :param list stress_groups: list containing the pick stresses and number of repetition
        :param float Sut: Ultimate tensile strength [MPa]
        :param float Sy: yield strength [MPa], if None only HCF is checked
        :param float Se: endurance limit [MPa]
        :param float z: -3 for steel where N=1e6, -5 for metal where N=1e8, -5.69 for a metal
            where N=5e8
        :param bool verbose: printing the groups
            [number_of_repetitions,maximum_stress, minimum_stress, reversible_stress, Number of
            cycles]
        :param bool freq: if the input is frequency instead of number of repetition
        :param bool alt_mean: if True the stress_group structure contains
            alternating and mean stresses: [number_of_repetitions, alternating_stress, mean_stress]
            instead of the max and min stresses:
            [number_of_repetitions, maximum_stress, minimum_stress]

        :returns: Total number of cycles
        :rtype: float
        """

        Sm = self.calc_Sm(Sut)
        for group in stress_groups:

            # if the stress given are minimum and maximum instead of alternating and mean
            if not alt_mean:
                mean_stress = (group[1] + group[2]) / 2
                alternating_stress = abs(group[1] - group[2]) / 2
            else:
                alternating_stress = group[1]
                mean_stress = group[2]

            # calculate the reversible stress according to the mean stress sign
            if mean_stress >= 0:
                reversible_stress = alternating_stress / (1 - (mean_stress / Sut))
            else:
                reversible_stress = alternating_stress

            group.append(reversible_stress)

            if ((Sy is not None) and (Sm < reversible_stress < Sy)) or reversible_stress < Se:
                # infinite num of cycle - either the stress is less than
                # the endurance limit or its low cycle fatigue
                group.append(inf)

            elif Se < reversible_stress < Sm:
                # High Cycle Fatigue
                # TODO: this calculation is the same every
                #   iteration consider change to internal function and implement cash
                a = Sm * (Sm / Se) ** (-3 / z)
                b = (1 / z) * log10(Sm / Se)
                N = (reversible_stress / a) ** (1 / b)
                group.append(N)

            else:
                # print error but don't stop the loop
                print(
                    f"Reversible Stress = {reversible_stress} not in range,"
                    f"LCF-range=(Sm_stress={Sm},Sy={Sy}), "
                    f"HCF-range(Se={Se},Sm_stress={Sm})")

        result = 0
        for group in stress_groups:
            # summing n/N
            result += (group[0] / group[-1])
            if verbose:
                print(group)

        N_total = float(1 / result)

        if verbose:
            if freq:
                print(f"total time = {N_total:.2f} [s]")
            else:
                print(f"N_total = {N_total:.2f}")
        return N_total

    def get_info(self):
        """print object attributes"""
        print_atributes(self)
