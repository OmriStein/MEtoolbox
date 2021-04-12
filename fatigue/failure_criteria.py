"""Fatigue Failure criteria as described in Shigley's Mechanical Engineering design"""
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

        return 1 / ((alt_eq_stress / endurance_limit) + (
                mean_eq_stress / ultimate_strength))

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

        return 1 / ((alt_eq_stress / endurance_limit) + (
                mean_eq_stress / yield_strength))

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

        # return 1 / ((alt_eq_stress / endurance_limit) + (
        #         mean_eq_stress / ultimate_strength) ** 2)
        alpha = ultimate_strength / mean_eq_stress
        beta = alt_eq_stress / endurance_limit
        return 0.5 * alpha ** 2 * beta*(-1 + sqrt(1 + 4 * alpha ** (-2) * beta ** (-2)))

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

        return sqrt(1 / ((alt_eq_stress / endurance_limit) ** 2 + (
                mean_eq_stress / yield_strength) ** 2))

    @staticmethod
    def langer_static_yield(yield_strength, alt_eq_stress, mean_eq_stress):
        """ Static safety factor according to Langer Failure criterion
        it's customary to use Langer, as an assessment to yielding in the first cycle

        :returns: Safety factor
        :rtype: any

        :raises ValueError: if Sy is not in the fatigue call
        """
        if mean_eq_stress > 0:
            # stress is in the first quadrant of the alternating-mean stress plan
            return yield_strength / (alt_eq_stress + mean_eq_stress)
        else:
            # stress is in the second quadrant of the alternating-mean stress plan
            return yield_strength / (alt_eq_stress - mean_eq_stress)
