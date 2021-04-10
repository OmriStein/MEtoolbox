from springs import HelicalPushSpring
from sympy import symbols, Eq, solveset

outer_diameter = 14.29
d = 2.337
D = outer_diameter - d
L0 = 111.12

# Chrome-vanadium wire
G, Ap, m, yield_percent = 77.2e3, 2005, 0.168, 0.45

K = symbols('K')
Fmax = 105.7  # [N]
Fmin = 12.24  # [N]
spring = HelicalPushSpring(max_force=Fmax, Ap=Ap, m=m, yield_percent=yield_percent, wire_diameter=d, spring_diameter=D,
                           shear_modulus=G, end_type='squared and ground', spring_constant=None, active_coils=21,
                           set_removed=False, shot_peened=False, free_length=L0)

nf, ns = spring.fatigue_analysis(Fmax, Fmin, 99, verbose=True)
print(f"nf = {nf}, ns = {ns}")
print(f"static safety factor = {spring.static_safety_factor()}")
print(f"solid safety factor = {spring.static_safety_factor(solid=True)}")

