from me_toolbox.springs import ExtensionSpring
from me_toolbox.tools import inch_to_millimetre as im
from me_toolbox.tools import millimetre_to_inch as mi
from me_toolbox.tools import pound_force_to_newtons as pn

outer_diameter = im(0.248)
d = im(0.035)
D = outer_diameter - d
r1 = im(0.106)
r2 = im(0.089)
Fi = pn(1.19)
Nb = 12.17
Fmax = pn(5)
Fmin = pn(1.5)
# Hard drawn wire
Ap, m = 1783, 0.190
Sut = Ap / ( d ** m )
G, E = 77.2e3, 203.4e3  # in [Mpa]

spring = ExtensionSpring(max_force=Fmax, initial_tension=Fi, wire_diameter=d, spring_diameter=D,
                         ultimate_tensile_strength=Sut, hook_r1=r1, hook_r2=r2, shear_modulus=G,
                         elastic_modulus=E, body_shear_yield_percent=0.45,
                         hook_normal_yield_percent=0.75, hook_shear_yield_percent=0.4,
                         spring_rate=30, shot_peened=False, density=None, working_frequency=None)

static_safety_factor = spring.static_safety_factor()
print(static_safety_factor)
fatigue_safety_factor = spring.fatigue_analysis(Fmax, Fmin, 50, )
print(fatigue_safety_factor)
# print(f"minimum spring diameter = {mi(spring.min_spring_diameter(1.5))}")
# print(f"minimum wire diameter = {mi(spring.min_wire_diameter(1.5, spring.spring_index))}")
