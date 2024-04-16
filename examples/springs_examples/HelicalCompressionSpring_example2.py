from me_toolbox.springs import Spring, HelicalCompressionSpring
from sympy import symbols, Eq, solveset

D = symbols('D')
force = 238
L0 = 39.15
Lw = 25
d = 1.8
# music wire
G, E, yield_percent = 82.7e3, 203.4, 0.6
Sut = Spring.material_prop('music wire', 6.5, metric=True, verbose=True)
K = force / (L0 - Lw)
print(f"K={K}")
spring = HelicalCompressionSpring(max_force=force, wire_diameter=d, spring_diameter=D,
                                  ultimate_tensile_strength=Sut, end_type='squared and ground',
                                  shear_modulus=G, elastic_modulus=E, shear_yield_percent=0.45,
                                  spring_rate=K, set_removed=True, shot_peened=False)

# finding D with sympy
n_static = spring.static_safety_factor()
n_solid = 1.2  # the safety factor for solid state
n = n_solid * 1.15  # the general safety factor the 1.15 is convention
eq1 = Eq(n, n_static)
print(f"eq1: {eq1}")
solution = solveset(eq1, D)
print(f"Ds = {solution.args[0]}")
# finding D with the MinSpringDiameter method
print(f"Dm = {spring.min_spring_diameter(1.2, wire_diameter=spring.wire_diameter ,solid=True)}")

# finding active_coils - number of active coils
print(f"active_coils = {spring.active_coils}")  # parametric expression
spring.spring_diameter = solution.args[0]  # assigning the D we found to the spring attributes
print(f"active_coils = {spring.active_coils}")  # finite number

# check design
print(f"Good design = {spring.check_design()}")

# spring.get_info()
