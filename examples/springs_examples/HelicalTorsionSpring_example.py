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
spring = HelicalTorsionSpring(max_moment, wire_diameter=d, spring_diameter=D, leg1=l1, leg2=l2,
                              ultimate_tensile_strength=, yield_percent=0.78, shear_modulus=11.75e6,
                              elastic_modulus=28.5e6, spring_rate=, radius=1, arbor_diameter=0.4,
                              shot_peened=False, density=None, working_frequency=None)
eq = Eq(spring.static_safety_factor, 1)
F_sol = solve(eq, F)[0]
print(f"F = {F_sol}")
print(spring.max_angular_deflection.subs(F, F_sol))
print(spring.max_total_angular_deflection.subs(F, F_sol))
spring.max_moment = F_sol * 1

print(f"(nf,ns) = {spring.fatigue_analysis(5, 1, 50, verbose=True, metric=False)}")

# spring.get_info()
print(f"minimal wire diameter = {spring.min_wire_diameter(1.5)}")
