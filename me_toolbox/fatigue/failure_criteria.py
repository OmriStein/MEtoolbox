"""a module containing the FatigueCriteria class
containing the Failure criteria as described in
Shigley's Mechanical Engineering design"""
from sympy import sqrt


class FailureCriteria:
    """Bundling the fatigue criteria together"""

    @staticmethod
    def modified_goodman(ultimate_strength, endurance_limit, alt_eq_stress,
                         mean_eq_stress):
        """Safety factor according to modified Goodman failure criterion
        (a very common criterion)

        :returns: Safety factor
        :rtype: any

        :raises ValueError: if ultimate_tensile_strength is not in the fatigue call
        """
        if mean_eq_stress < 0:
            raise Exception("Not valid when the mean equivalent stress is negative,"
                            "use get_safety_factor method instead ")

        try:
            return 1 / ((alt_eq_stress / endurance_limit) + (
                    mean_eq_stress / ultimate_strength))
        except TypeError:
            return None

    @staticmethod
    def soderberg(yield_strength, endurance_limit, alt_eq_stress, mean_eq_stress):
        """Safety factor according to Soderberg failure criterion
        (the safest criterion)

        :returns: Safety factor
        :rtype: any

        :raises ValueError: if Sy is not in the fatigue call
        """
        if mean_eq_stress < 0:
            raise Exception("Not valid when the mean equivalent stress is negative,"
                            "use get_safety_factor method instead ")

        try:
            return 1 / ((alt_eq_stress / endurance_limit) + (
                    mean_eq_stress / yield_strength))
        except TypeError:
            return None

    @staticmethod
    def gerber(ultimate_strength, endurance_limit, alt_eq_stress, mean_eq_stress):
        """Safety factor according to Gerber failure criterion
        (the most lenient criterion)

        :returns: Safety factor
        :rtype: any
        :raises ValueError: if ultimate_tensile_strength is not in the fatigue call
        """
        if mean_eq_stress < 0:
            raise Exception("Not valid when the mean equivalent stress is negative,"
                            "use get_safety_factor method instead ")

        try:
            alpha = ultimate_strength / mean_eq_stress
            beta = alt_eq_stress / endurance_limit
            return 0.5 * alpha ** 2 * beta * (-1 + sqrt(1 + 4 * alpha ** (-2) * beta ** (-2)))
        except TypeError:
            return None

    @staticmethod
    def asme_elliptic(yield_strength, endurance_limit, alt_eq_stress,
                      mean_eq_stress):
        """Safety factor according to ASME Failure criterion

        :returns: Safety factor
        :rtype: any

        :raises ValueError: if ultimate_tensile_strength is not in the fatigue call
        """
        if mean_eq_stress < 0:
            raise Exception("Not valid when the mean equivalent stress is negative,"
                            "use get_safety_factor method instead ")
        try:
            return sqrt(1 / ((alt_eq_stress / endurance_limit) ** 2 + (
                    mean_eq_stress / yield_strength) ** 2))
        except TypeError:
            return None

    @staticmethod
    def langer_static_yield(yield_strength, alt_eq_stress, mean_eq_stress):
        """ Static safety factor according to Langer Failure criterion
        it's customary to use Langer, as an assessment to yielding in the first cycle

        :returns: Safety factor
        :rtype: any

        :raises ValueError: if Sy is not in the fatigue call
        """
        try:
            if mean_eq_stress > 0:
                # stress is in the first quadrant of the alternating-mean stress plan
                return yield_strength / (alt_eq_stress + mean_eq_stress)
            else:
                # stress is in the second quadrant of the alternating-mean stress plan
                return yield_strength / (alt_eq_stress - mean_eq_stress)

        except TypeError:
            return None

    @staticmethod
    def get_safety_factor(yield_strength, ultimate_strength, endurance_limit,
                          alt_eq_stress, mean_eq_stress, criterion, verbose=False):
        """Returns dynamic and static safety factors
        according to the quadrant in the alternating-mean
        stress plain where the stresses are in

        Note: Should always be used instead of accessing the
        individual safety factors properties directly

        :param str criterion: The criterion to use
        :param float yield_strength: The yield strength (Sy or Ssy)
        :param float ultimate_strength: The yield strength (Sut or Ssu)
        :param float endurance_limit: Modified endurance limit (Se)
        :param float alt_eq_stress: alternating stresses
        :param float mean_eq_stress: mean stresses
        :param bool verbose: Print the result

        :returns: dynamic and static safety factors
        :rtype: tuple[float, float]
        """

        if mean_eq_stress > 0:
            # stress is in the first quadrant of the alternating-mean stress plan
            args = (endurance_limit, alt_eq_stress, mean_eq_stress)
            safety_factors = {
                'modified goodman': FailureCriteria.modified_goodman(ultimate_strength, *args),
                'soderberg': FailureCriteria.soderberg(yield_strength, *args),
                'gerber': FailureCriteria.gerber(ultimate_strength, *args),
                'asme-elliptic': FailureCriteria.asme_elliptic(yield_strength, *args)}

            nF = safety_factors.get(criterion.lower(), 'Error')

            if nF == 'Error':
                raise ValueError(f"Unknown criterion - {criterion}\n"
                                 "Available criteria: 'Modified Goodman', 'Soderberg',"
                                 "'Gerber', 'ASME-elliptic'")

        else:
            # stress is in the second quadrant of the alternating-mean stress plan
            if verbose:
                print(f"NOTE: The mean stress = {mean_eq_stress} "
                      f"is negative, using alternative calculation")
            nF = endurance_limit / alt_eq_stress
            criterion = 'fatigue'

        nl = FailureCriteria.langer_static_yield(yield_strength, alt_eq_stress, mean_eq_stress)

        if verbose:
            if nl is None:
                print("Couldn't calculate Langer static safety factor,"
                      "the yield_strength is None")

            if nF is None:
                if yield_strength is None:
                    print(f"Couldn't calculate {criterion} static safety factor, "
                          f"the yield_strength is None")
                elif ultimate_strength is None:
                    print(f"Couldn't calculate {criterion} static safety factor, "
                          f"the ultimate_strength is None")

            if nF is not None and nl is not None:
                print(f"the {criterion} safety factor is: {nF}\n"
                      f"the Langer static safety factor is: {nl}")
            elif nF is None and nl is not None:
                print(f"the Langer static safety factor is: {nl}")
            elif nl is None and nF is not None:
                print(f"the {criterion} safety factor is: {nF}\n")

        return nF, nl
