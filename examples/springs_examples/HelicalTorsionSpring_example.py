from me_toolbox.springs import HelicalTorsionSpring
from sympy import symbols, Eq, solve

F = symbols('F')
max_moment = F * 1
d = 0.072
OD = (19 / 32)
D = OD - d
Nb = 4.25
l1 = 1
l2 = l1
spring = HelicalTorsionSpring(max_moment, Ap=201e3, m=0.145, yield_percent=0.78, wire_diameter=d,
                              spring_diameter=D, leg1=l1, leg2=l2, shear_modulus=11.75e6,
                              elastic_modulus=28.5e6, spring_constant=None, active_coils=None,
                              body_coils=Nb, shot_peened=False, density=None,
                              working_frequency=None, radius=1, pin_diameter=0.4)
eq = Eq(spring.static_safety_factor, 1)
F_sol = solve(eq, F)[0]
print(f"F = {F_sol}")
print(spring.max_angular_deflection.subs(F, F_sol))
print(spring.max_total_angular_deflection.subs(F, F_sol))
spring.max_moment = F_sol * 1

print(spring.fatigue_analysis(5, 1, 50, verbose=True, metric=False))
