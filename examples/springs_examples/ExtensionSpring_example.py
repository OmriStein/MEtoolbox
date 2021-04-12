from springs import ExtensionSpring
from sympy import symbols, Eq, solveset

outer_diameter = 0.248
d = 0.035
D = outer_diameter - d
r1 = 0.106
r2 = 0.089
Fi = 1.19
Nb = 12.17
Fmax = 5.25
# Chrome-vanadium wire
Ap, m, yield_percent, bending_yield_percent = 140e3, 0.19, 0.45, 0.75
G, E = 11.6e6, 28.7e6

spring = ExtensionSpring(max_force=Fmax, initial_tension=1, wire_diameter=d, spring_diameter=D,
                         Ap=Ap, m=m, hook_r1=r1, hook_r2=r2, shear_modulus=G, elastic_modulus=E,
                         yield_percent=yield_percent, bending_yield_percent=bending_yield_percent,
                         spring_constant=None, active_coils=None, body_coils=12.17,
                         free_length=None, density=None, working_frequency=None)
# spring.get_info()
print(spring.static_safety_factor())
for i in range(1, 100):
    ds, dn = spring.min_wire_diameter(i)
    if dn is not None:
        print(i,dn)

