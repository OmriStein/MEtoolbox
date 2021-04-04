from math import log10
from sympy import sqrt
from tools import NotInRangeError, PrintAtributes
from sympy import oo
from FatigueAnalysis import EnduranceLimit


def CalcKf(q, Kt):
    """ Kf - dynamic stress concentration factor

        :keyword Kt: stress concentration theoretical factor
        :keyword q: notch Sensitivity """
    return 1 + q * (Kt - 1)


class FatigueAnalysis:
    """ Perform fatigue analysis"""

    # TODO: make endurance_limit optional and add option to input Se, Stress_type and Kc directly
    # TODO: replace Kc as a way to determine what to do in factors calculation

    def __init__(self, endurance_limit, ductile, Sut=None, Sy=None, Kf_bending=0, Kf_normal=0, Kf_torsion=0,
                 alternating_bending_stress=0, alternating_normal_stress=0, alternating_torsion_stress=0,
                 mean_bending_stress=0, mean_normal_stress=0, mean_torsion_stress=0):
        """ Note: all stresses are in [MPa]

        :keyword endurance_limit: EnduranceLimit object containing the modified Se
        :type endurance_limit: EnduranceLimit
        :keyword ductile: True if material is ductile
        :type ductile: bool
        :keyword Sut: Ultimate tensile strength in [Mpa]
        :type Sut: float
        :keyword Sy: Yield strength in [Mpa]
        :type Sy: float
        :type Kf_bending: float
        :type Kf_normal: float
        :type Kf_torsion: float
        :type alternating_bending_stress: float
        :type alternating_normal_stress: float
        :type alternating_torsion_stress: float
        :type mean_bending_stress: float
        :type mean_normal_stress: float
        :type mean_torsion_stress: float
        """

        self.Sut, self.Sy = Sut, Sy
        # self.endurance_limit = endurance_limit
        self.Se = endurance_limit.modified
        self.Kc = endurance_limit.Kc
        self.stress_type = endurance_limit.stress_type
        self.ductile = ductile
        self.Kf_bending, self.Kf_normal, self.Kf_torsion = Kf_bending, Kf_normal, Kf_torsion
        self.alternating_bending_stress = alternating_bending_stress
        self.alternating_normal_stress = alternating_normal_stress
        self.alternating_torsion_stress = alternating_torsion_stress
        self.mean_bending_stress = mean_bending_stress
        self.mean_normal_stress = mean_normal_stress
        self.mean_torsion_stress = mean_torsion_stress
        self.alternating_equivalent_stress = self.AlternatingEquivalentStress()
        self.mean_equivalent_stress = self.MeanEquivalentStress()

    def AlternatingEquivalentStress(self):
        """ Alternating equivalent stress """

        Kc = self.Kc
        if Kc == 1 and self.stress_type == 'multiple':
            corrected_bending = self.Kf_bending * self.alternating_bending_stress
            corrected_normal = self.Kf_normal * (self.alternating_normal_stress / 0.85)
            corrected_torsion = self.Kf_torsion * self.alternating_torsion_stress
            return sqrt((corrected_bending + corrected_normal) ** 2 + 3 * corrected_torsion ** 2)

        elif Kc == 1:
            return self.Kf_bending * self.alternating_bending_stress

        elif Kc == 0.85:
            return self.Kf_normal * self.alternating_normal_stress

        elif Kc == 0.59:
            return self.Kf_torsion * self.alternating_torsion_stress

    def MeanEquivalentStress(self):
        """ Mean equivalent stress """

        if self.ductile:
            # if the material is ductile no correction is needed
            Kf_bending, Kf_normal, Kf_torsion = 1, 1, 1
        else:
            Kf_bending, Kf_normal, Kf_torsion = self.Kf_bending, self.Kf_normal, self.Kf_torsion

        Kc = self.Kc
        if Kc == 1 and self.stress_type == 'multiple':
            corrected_bending = Kf_bending * self.mean_bending_stress
            corrected_normal = Kf_normal * self.mean_normal_stress
            corrected_torsion = Kf_torsion * self.mean_torsion_stress

            return sqrt((corrected_bending + corrected_normal) ** 2 + 3 * corrected_torsion ** 2)

        elif Kc == 1:
            return Kf_bending * self.mean_bending_stress

        elif Kc == 0.85:
            return Kf_normal * self.mean_normal_stress

        elif Kc == 0.59:
            return Kf_torsion * self.mean_torsion_stress

    @property
    def Ssu(self):
        """ Sut correction for shear stress """
        return 0.67 * self.Sut

    @property
    def Ssy(self):
        """ Sy correction for shear stress """
        return self.Sy / sqrt(3).evalf()

    @property
    def modified_goodman(self):
        """ Safety factor according to modified Goodman failure criterion
            a very common criterion

            :returns: Safety factor
            :rtype: any
            :raises ValueError: if Sut is not in the FatigueAnalysis call """

        if self.Sut is None:
            raise ValueError("Sut is None")

        if self.mean_equivalent_stress < 0:
            raise Exception("Not valid when the mean equivalent stress is negative,"
                            "use GetSafetyFactor instead ")

        ultimate_strength = self.Sut
        if self.Kc == 0.59:
            # Sut correction for shear stress
            ultimate_strength = self.Ssu

        return 1 / ((self.alternating_equivalent_stress / self.Se) + (self.mean_equivalent_stress / ultimate_strength))

    @property
    def soderberg(self):
        """ Safety factor according to Soderberg failure criterion
            the safest criterion

            :returns: Safety factor
            :rtype: any
            :raises ValueError: if Sy is not in the FatigueAnalysis call """

        if self.Sy is None:
            raise ValueError("Sy is None")

        if self.mean_equivalent_stress < 0:
            raise Exception("Not valid when the mean equivalent stress is negative,"
                            "use GetSafetyFactor instead ")

        yield_strength = self.Sy
        if self.Kc == 0.59:
            # Sut correction for shear stress
            yield_strength = self.Ssy

        return 1 / ((self.alternating_equivalent_stress / self.Se) +
                    (self.mean_equivalent_stress / yield_strength))

    @property
    def gerber(self):
        """ Safety factor according to Gerber failure criterion
            the most lenient criterion

            :returns: Safety factor
            :rtype: any
            :raises ValueError: if Sut is not in the FatigueAnalysis call """

        if self.Sut is None:
            raise ValueError("Sut is None")

        if self.mean_equivalent_stress < 0:
            raise Exception("Not valid when the mean equivalent stress is negative,"
                            "use GetSafetyFactor instead ")

        ultimate_strength = self.Sut
        if self.Kc == 0.59:
            # Sut correction for shear stress
            ultimate_strength = self.Ssu

        return 1 / ((self.alternating_equivalent_stress / self.Se) +
                    (self.mean_equivalent_stress / ultimate_strength) ** 2)

    @property
    def ASME_elliptic(self):
        """ Safety factor according to ASME Failure criterion
            it's customary to use Langer, as an assessment to yielding in the first cycle

            :returns: Safety factor
            :rtype: any
            :raises ValueError: if Sut is not in the FatigueAnalysis call """

        if self.Sut is None:
            raise ValueError("Sut is None")

        if self.mean_equivalent_stress < 0:
            raise Exception("Not valid when the mean equivalent stress is negative,"
                            "use GetSafetyFactor instead ")

        ultimate_strength = self.Sut
        if self.Kc == 0.59:
            # Sut correction for shear stress
            ultimate_strength = self.Ssu

        return 1 / ((self.alternating_equivalent_stress / self.Se) ** 2 +
                    (self.mean_equivalent_stress / ultimate_strength) ** 2)

    @property
    def langer_static_yield(self):
        """ Static safety factor according to Langer Failure criterion

            :returns: Safety factor
            :rtype: any
            :raises ValueError: if Sy is not in the FatigueAnalysis call """

        if self.Sy is None:
            raise ValueError("Sy is None")

        yield_strength = self.Sy
        if self.Kc == 0.59:
            # Sy correction for shear stress
            Ssy = 0.67 * self.Sut
            yield_strength = Ssy

        if self.mean_equivalent_stress > 0:
            # stress is in the first quadrant of the alternating-mean stress plan
            return yield_strength / (self.alternating_equivalent_stress + self.mean_equivalent_stress)
        else:
            # stress is in the second quadrant of the alternating-mean stress plan
            return yield_strength / (self.alternating_equivalent_stress - self.mean_equivalent_stress)

    def GetSafetyFactor(self, criterion, verbose=True):
        """ returns dynamic and static safety factors
            according to the alternating-mean stress
            plain quadrant where the stresses are in

            Note: Should always be used instead of accessing the individual safety factors properties directly
             """

        if self.mean_equivalent_stress > 0:
            # stress is in the first quadrant of the alternating-mean stress plan
            safety_factors = {'modified goodman': self.modified_goodman, 'soderberg': self.soderberg,
                              'gerber': self.gerber, 'asme-elliptic': self.ASME_elliptic}

            nF = safety_factors.get(criterion.lower(), 'Error')

            if nF == 'Error':
                raise ValueError(f"Unknown criterion - {criterion}\n"
                                 f"Available criteria: 'Modified Goodman', 'Soderberg', 'Gerber', 'ASME-elliptic'")

            msg = f"the {criterion} safety factor is: {nF}\n"

        else:
            # stress is in the second quadrant of the alternating-mean stress plan
            nF = self.Se / self.alternating_equivalent_stress
            msg = f"the dynamic safety factor is: {nF}\n"

        nl = self.langer_static_yield

        if verbose:
            print(msg + f"the Langer static safety factor is: {nl}")

        return nF, nl

    @property
    def Sm(self):
        return self.CalcSm(self.Sut)

    @staticmethod
    def CalcSm(Sut):
        """ Sm is the limit between Low cycle fatigue and high cycle fatigue """

        def f(x):
            """ f - fatigue strength fraction
                a function constructed from curve fitting to the f graph in Shigley's
                the range of the fit is ( 70[kPsi] < Sut < 200[kPsi] ) """
            return (-2.56710686e-16 * x ** 5 + 1.35729780e-12 * x ** 4 - 2.92474777e-09 * x ** 3 +
                    3.28990748e-06 * x ** 2 - 2.04929617e-03 * x + 1.38405394e+00)

        # TODO: add a proper warning and solutions to Sut out of graph range
        if Sut < 482.633:  # 482.633[Mpa] = 70[kPsi]
            print(f"Note: Sut={Sut} < 482.633[Mpa] (70[kPsi]) so f~0.9")
            return 0.9 * Sut
        elif Sut > 1378.95:
            print(f"Note: Sut={Sut} > 1378.95[Mpa] (200[kPsi]) which is out of the graph range, f={f(Sut)}")
        return f(Sut) * Sut

    def NumOfCycle(self, z=-3):
        """ calculate number of cycles until failure

            Note: z = log(N1) - log(N2), N1 - number of cycles at Sm, N2 - Number of cycles at Se
                for steel N1=1e3 and N2 = 1e6
            :keyword z: -3 for steel where N=1e6, -5 for a metal where N=1e8, -5.69 for a metal where N=5e8
            :returns: N - Number of cycles,
                      Sf - fatigue stress at failure
            """
        mean_stress = self.mean_equivalent_stress
        alternating_stress = self.alternating_equivalent_stress
        Se = self.Se
        Sut, Sy, Sm = self.Sut, self.Sy, self.Sm

        if mean_stress >= 0:
            reversible_stress = alternating_stress / (1 - (mean_stress / Sut))
        else:
            reversible_stress = alternating_stress

        if Sm < reversible_stress < Sy:
            # Low Cycle Fatigue
            if z != -3:
                raise ValueError("Number of cycles calculation for low cycle fatigue is only possible for z=-3 ")

            a = Sut
            b = (1 / z) * log10(Sut / Sm)

        elif Se < reversible_stress < Sm:
            # High Cycle Fatigue
            # a = Sm ** (1 - (3 / z)) / Se
            a = Sm * (Sm / Se) ** (-3 / z)
            b = (1 / z) * log10(Sm / Se)

        elif reversible_stress < Se:
            print(f"reversible_stress = {reversible_stress} < Se = {Se}, Number of cycles is infinite")
            return oo  # TODO: add to documentation the meaning of oo
        else:
            raise NotInRangeError("Reversible Stress", reversible_stress,
                                  (f'Sy={Sy}', f'Sm={Sm}', f'Se={Se}'))
        N = (reversible_stress / a) ** (1 / b)
        return N, a * N ** b

    def Miner(self, stress_groups, Sut, Se, Sy=None, z=-3, verbose=False, alt_mean=False, freq=False):
        """ Calculates total number of cycles for multiple periodical loads,
            the stress_groups format is as follow [number_of_repetitions, maximum_stress, minimum_stress]
            number_of_repetitions = frequency [Hz] * time

            Note: if the material don't have fatigue limit use the fatigue strength at Se=Sf(N=1e8)

            :param freq: if the input is frequency instead of number of repetition
            :param alt_mean: if True the stress_group structure contains
                alternating and mean stresses: [number_of_repetitions, alternating_stress, mean_stress]
                instead of the max and min stresses:[number_of_repetitions, maximum_stress, minimum_stress]
            :type stress_groups: list
            :keyword Sut: Ultimate tensile strength [MPa]
            :type Sut: float
            :keyword Sy: yield strength [MPa], if None only HCF is checked
            :type Sy: float
            :keyword Se: endurance limit [MPa]
            :type Se: float
            :keyword z: -3 for steel where N=1e6, -5 for a metal where N=1e8, -5.69 for a metal where N=5e8
            :type z: float
            :keyword verbose: printing the the groups
                [number_of_repetitions,maximum_stress, minimum_stress, reversible_stress, Number of cycles]
            :type verbose: bool
            :returns: Total number of cycles
            :rtype: float """

        Sm = self.CalcSm(Sut)
        for group in stress_groups:

            if not alt_mean:
                mean_stress = (group[1] + group[2]) / 2
                # group.append(mean_stress)
                alternating_stress = abs(group[1] - group[2]) / 2
                # group.append(alternating_stress)
            else:
                alternating_stress = group[1]
                mean_stress = group[2]

            if mean_stress >= 0:
                reversible_stress = alternating_stress / (1 - (mean_stress / Sut))
            else:
                reversible_stress = alternating_stress

            group.append(reversible_stress)

            if ((Sy is not None) and (Sm < reversible_stress < Sy)) or reversible_stress < Se:
                # inf num of cycle
                group.append(oo)

            elif Se < reversible_stress < Sm:
                # High Cycle Fatigue
                # TODO: this calculation is the same every iteration change to internal function and implement cash
                a = Sm * (Sm / Se) ** (-3 / z)
                b = (1 / z) * log10(Sm / Se)
                N = (reversible_stress / a) ** (1 / b)
                group.append(N)

            else:
                print(f"Reversible Stress = {reversible_stress} not in range, LCF-range=(Sm={Sm},Sy={Sy}), "
                      f"HCF-range(Se={Se},Sm={Sm})")
        result = 0
        for group in stress_groups:
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

    def getInfo(self):
        """ print object attributes """
        PrintAtributes(self)
