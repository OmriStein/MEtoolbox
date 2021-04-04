import sympy

from Springs import HelicalPushSpring
from sympy import symbols, Eq, solveset, pprint, simplify, nsimplify
from sympy.sets import Reals
from math import pi

d = symbols('d', real=True, positive=True, rational=True)
G = 75e3  # [Mpa]
C = 8
D = C * d

Fmax = 575
Fs = 1.25 * Fmax
spring = HelicalPushSpring(force=Fs, Ap=2211, m=sympy.Rational(0.145), wire_diameter=d, spring_diameter=D,
                           shear_modulus=G, end_type='squared and ground', spring_constant=6.189,
                           set_removed=False, shot_peened=True, yield_percent=0.45)

print(spring.MinimalWireDiameter(1.5))
