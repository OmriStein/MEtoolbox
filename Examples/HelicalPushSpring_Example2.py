from Springs import HelicalPushSpring
from sympy import symbols, Eq, solveset

D = symbols('D')
force = 238
L0 = 39.15
Lw = 25
d = 1.8
# music wire
G, Ap, m, yield_percent = 82.7e3, 2211, 0.145, 0.6
K = force / (L0 - Lw)
print(f"K={K}")
spring = HelicalPushSpring(force=force, wire_diameter=d, spring_diameter=D, Ap=Ap, m=m, shear_modulus=G,
                           end_type='squared and ground', yield_percent=yield_percent, set_removed=True,
                           shot_peened=False,
                           spring_constant=K)

# finding D with sympy
n_static = spring.static_safety_factor
n_solid = 1.2  # the safety factor for solid state
n = n_solid * 1.15  # the general safety factor the 1.15 is a convention
eq1 = Eq(n, n_static)
print(f"eq1: {eq1}")
solution = solveset(eq1, D)
print(f"Ds = {solution.args[0]}")
# finding D with the MinSpringDiameter method
print(f"Dm = {spring.MinSpringDiameter(1.2, solid=True)}")

# finding Na - number of active coils
print(f"Na = {spring.Na}")  # parametric expression
spring.spring_diameter = solution.args[0]  # assigning the D we found to the spring attributes
print(f"Na = {spring.Na}")  # finite number

# check design
print(f"Good design = {spring.CheckDesign()}")

spring.getInfo()
