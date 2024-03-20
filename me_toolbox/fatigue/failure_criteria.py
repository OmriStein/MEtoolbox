"""module containing the FatigueCriteria class
containing the Failure criteria as described in
Shigley's Mechanical Engineering design
"""
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

        :raises Exception: if mean equivalent stress is negative
        """
        if mean_eq_stress < 0:
            raise ValueError("Not valid when the mean equivalent stress is negative")

        return 1 / ((alt_eq_stress / endurance_limit) + (mean_eq_stress / ultimate_strength))

    @staticmethod
    def soderberg(yield_strength, endurance_limit, alt_eq_stress, mean_eq_stress):
        """Safety factor according to Soderberg failure criterion
        Soderberg criterion guards against any yielding, but is biased low (the safest criterion)

        :returns: Safety factor
        :rtype: any

        :raises Exception: if mean equivalent stress is negative
        """
        if mean_eq_stress < 0:
            raise ValueError("Not valid when the mean equivalent stress is negative")

        return 1 / ((alt_eq_stress / endurance_limit) + (mean_eq_stress / yield_strength))

    @staticmethod
    def gerber(ultimate_strength, endurance_limit, alt_eq_stress, mean_eq_stress):
        """Safety factor according to Gerber failure criterion
        (the most lenient criterion)

        :returns: Safety factor
        :rtype: any
        :raises Exception: if mean equivalent stress is negative
        """
        if mean_eq_stress < 0:
            raise ValueError("Not valid when the mean equivalent stress is negative")

        alpha = ultimate_strength / mean_eq_stress
        beta = alt_eq_stress / endurance_limit
        return 0.5 * alpha ** 2 * beta * (-1 + sqrt(1 + 4 * alpha ** (-2) * beta ** (-2)))

    @staticmethod
    def asme_elliptic(yield_strength, endurance_limit, alt_eq_stress,
                      mean_eq_stress):
        """Safety factor according to ASME Failure criterion

        :returns: Safety factor
        :rtype: any

        :raises Exception: if mean equivalent stress is negative
        """
        if mean_eq_stress < 0:
            raise ValueError("Not valid when the mean equivalent stress is negative")

        return sqrt(1 / ((alt_eq_stress / endurance_limit) ** 2 + (
                mean_eq_stress / yield_strength) ** 2))

    @staticmethod
    def langer_static_yield(yield_strength, alt_eq_stress, mean_eq_stress):
        """ Static safety factor according to Langer Failure criterion
        it's customary to use Langer, as an assessment to yielding in the first cycle

        :returns: Safety factor
        :rtype: any
        """
        if mean_eq_stress > 0:
            # stress is in the first quadrant of the alternating-mean stress plan
            return yield_strength / (alt_eq_stress + mean_eq_stress)
        else:
            # stress is in the second quadrant of the alternating-mean stress plan
            return yield_strength / (alt_eq_stress - mean_eq_stress)

    @staticmethod
    def get_safety_factors(yield_strength, ultimate_strength, endurance_limit,
                           alt_eq_stress, mean_eq_stress, criterion, verbose=False):
        """Returns dynamic and static safety factors
        according to the quadrant in the alternating-mean
        stress plain where the stresses are in

        Note: Takes into account the stress direction and offer alternative calculation
        in case the mean equivalent stress is negative
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
            try:
                fatigue_safety_factor = safety_factors[criterion.lower()]

            except KeyError:
                raise Exception(f"Unknown criterion - {criterion}\n"
                                f"Available criteria are: 'Modified Goodman', 'Soderberg',"
                                f"'Gerber', 'ASME-elliptic'")

        else:
            # stress is in the second quadrant of the alternating-mean stress plan
            if verbose:
                print(f"NOTE: The mean stress = {mean_eq_stress} "
                      f"is negative, using alternative calculation")
            fatigue_safety_factor = endurance_limit / alt_eq_stress
            criterion = 'fatigue'

        static_safety_factor = FailureCriteria.langer_static_yield(yield_strength, alt_eq_stress,
                                                                   mean_eq_stress)
        if verbose:
            print(f"the {criterion} safety factor is: {fatigue_safety_factor}\n"
                  f"the Langer static safety factor is: {static_safety_factor}")

        return fatigue_safety_factor, static_safety_factor
