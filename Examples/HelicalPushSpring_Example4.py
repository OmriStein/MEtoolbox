from math import sqrt

from Springs import HelicalPushSpring
from sympy import symbols, Eq, solveset, I
from tools import PoundForceToNewtons, InchToMillimetre

d, D = symbols('d, D', real=True, positive=True)

# Chrome-vanadium wire
G, Ap, m, yield_percent = 81e3, 2211, 0.145, 0.45
Fmax = PoundForceToNewtons(20)  # [N]
Fmin = PoundForceToNewtons(5)  # [N]

min_deflection = InchToMillimetre(0.5)
max_deflection = InchToMillimetre(2)
# fw = 5  # [Hz]

K = Fmax / max_deflection

# solid length<1"
# L0<4

wire_sizes_inch = [0.080, 0.085, 0.090, 0.095, 0.105, 0.112]

spring = HelicalPushSpring(force=Fmax, wire_diameter=d, spring_diameter=D, Ap=Ap, m=m, shear_modulus=G,
                           end_type='squared and ground', yield_percent=yield_percent, set_removed=False,
                           shot_peened=False, spring_constant=K)
