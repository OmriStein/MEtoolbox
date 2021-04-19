"""A module containing stress calculation functions"""


# TODO: better stress calculation
def uniform_stress(F, A):
    """Returns stress assuming uniform distribution in cross section

    :param float F: Force
    :param float A: Cross section area

    :returns Stress
    :rtype: float
    """
    return F / A


def bending_stress(My, Iy, z, Mz=None, Iz=None, y=None):
    """Bending stress in a principle system

    :param float My: Moment in the y direction
    :param float Mz: Moment in the y direction
    :param float Iy: Area moment of inertia for the y direction
    :param float Iz: Area moment of inertia for the zeta direction
    :param float z: Coordinate
    :param float y: Coordinate

    :returns: Bending Stress in a cross section
    :rtype: float
    """

    if Mz is None:
        return (My / Iy) * z
    else:
        return (My / Iy) * z, -(Mz / Iz) * y


def shear_bending_stress(V, Q, I, b):
    """ Shear stresses due to bending

    :param float V: Shear max_force in y direction
    :param float Q: first moment of in cross section in y direction
    :param float I: Area moment of inertia around the y axis
    :param float b: thickness

    :returns: Shear stress resulting from bending
    :rtype: float
    """

    return (V * Q) / (I * b)


def torsion_stress(T, r, J):
    """ Torsion stresses

    :param float T: Cross section torque
    :param float r: Stress radius coordinate
    :param float J: Cross section polar moment of inertia

    :returns: Torsion Stress at r
    :rtype: float
    """
    return (T * r) / J


def max_shear_stress(V, A, shape):
    """Returns The maximum shear stress for known shapes

    :param float V: Shear Stress
    :param float A: Cross section area
    :param str shape: Cross section shape

    :returns: Maximum shear Stress
    :rtype: float
    """
    if shape == 'circle':
        return (4 * V) / (3 * A)
    elif shape == ' rectangle':
        return (3 * V) / (2 * A)
    else:
        raise ValueError(f"shape = {shape} is unknown")
