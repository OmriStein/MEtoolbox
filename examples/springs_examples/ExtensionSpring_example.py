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
G, E = 77.2e3, 203.4e3  # in [Mpa]
spring = ExtensionSpring(max_force=Fmax, initial_tension=Fi, wire_diameter=d, spring_diameter=D,
                         Ap=Ap, m=m, hook_r1=r1, hook_r2=r2, shear_modulus=G, elastic_modulus=E,
                         end_torsion_yield_percent=0.4, end_bending_yield_percent=0.75,
                         body_torsion_yield_percent=0.45,
                         spring_constant=None, active_coils=None, body_coils=12.17,
                         free_length=None, density=None, working_frequency=None)

n_body, n_hook_normal, n_hook_torsion = spring.static_safety_factor()
print(f"ns_body={n_body}, ns_hook_normal={n_hook_normal}, ns_hook_torsion={n_hook_torsion}")
nf_body, ns_body, nf_hook_bending, nf_hook_torsion = spring.fatigue_analysis(Fmax, Fmin, 50,)
print(f"nf_body={nf_body}, ns_body={ns_body}, nf_hook_bending={nf_hook_bending},"
      f"nf_hook_torsion={nf_hook_torsion}")
print(f"minimum spring diameter = {mi(spring.min_spring_diameter(1.5))}")
print(f"minimum wire diameter = {mi(spring.min_wire_diameter(1.5))}")
