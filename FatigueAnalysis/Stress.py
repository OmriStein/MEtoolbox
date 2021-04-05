# TODO: better stress calculation
def UniformStress(F, A):
    """ Returns stress assuming uniform distribution in cross section

        :keyword F: Force
        :keyword A: Cross section area
        :returns Stress
        :rtype: float
        """
    return F / A


def BendingStress(My, Iy, z, Mz=None, Iz=None, y=None):
    """ Bending stress in a principle system

        :keyword My: Moment in the y direction
        :type My: float
        :keyword Mz: Moment in the y direction
        :type Mz: float
        :keyword Iy: Area moment of inertia for the y direction
        :type Iy: float
        :keyword Iz: Area moment of inertia for the zeta direction
        :type Iz: float
        :keyword z: Coordinate
        :type z: float
        :keyword y: Coordinate
        :type y: float
        :returns: Bending Stress in a cross section
        :rtype: float """

    if Mz is None:
        return (My / Iy) * z
    else:
        return (My / Iy) * z, -(Mz / Iz) * y


def ShearBendingStress(V, Q, I, b):
    """ Shear stresses due to bending

        :keyword V: Shear force in y direction
        :type V: float
        :keyword Q: first moment of in cross section in y direction
        :type Q: float
        :keyword I: Area moment of inertia around the y axis
        :type I: float
        :keyword b: thickness
        :type b: float
        :returns: Shear stress resulting from bending
        :rtype: float"""

    return (V * Q) / (I * b)


def TorsionStress(T, r, J):
    """ Torsion stresses
        :keyword T: Cross section torque
        :keyword r: Stress radius coordinate
        :keyword J: Cross section polar moment of inertia
        :returns: Torsion Stress at r """
    return (T * r) / J


def MaxShearStress(V, A, shape):
    if shape == 'circle':
        return (4 * V) / (3 * A)
    elif shape == ' rectangle':
        return (3 * V) / (2 * A)
    else:
        raise ValueError(f"shape = {shape} is unknown")
