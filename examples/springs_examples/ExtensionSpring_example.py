from springs import ExtensionSpring
from tools import inch_to_millimetre as im
from tools import pound_force_to_newtons as pn

outer_diameter = im(0.248)
d = im(0.035)
D = outer_diameter - d
r1 = im(0.106)
r2 = im(0.089)
Fi = pn(1.19)
Nb = 12.17
Fmax = pn(5)
Fmin = pn(1.5)
# Chrome-vanadium wire
Ap, m, yield_percent, bending_yield_percent = 2005, 0.168, 0.45, 0.75
G, E = 77.2e3, 203.4e3  # in [Mpa]

spring = ExtensionSpring(max_force=Fmax, initial_tension=Fi, wire_diameter=d, spring_diameter=D,
                         Ap=Ap, m=m, hook_r1=r1, hook_r2=r2, shear_modulus=G, elastic_modulus=E,
                         yield_percent=yield_percent, bending_yield_percent=bending_yield_percent,
                         spring_constant=None, active_coils=None, body_coils=12.17,
                         free_length=None, density=None, working_frequency=None)

nf_hook_a, nf_hook_b, nf_body, ns_body = spring.fatigue_analysis(Fmax, Fmin, 50, verbose=False)
print(f"nf_hook_a={nf_hook_a}, nf_hook_b={nf_hook_b}, nf_body={nf_body}, ns_body={ns_body}")
print(spring.min_spring_diameter(1.5))