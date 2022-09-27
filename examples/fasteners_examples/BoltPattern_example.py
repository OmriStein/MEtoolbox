from me_toolbox.fasteners import MetricBolt
from me_toolbox.fasteners import ThreadedFastener
from me_toolbox.fasteners import BoltPattern

M10 = MetricBolt(10, 1.5, 33, '9.8', elastic_modulus=207e3, preload=32062.5)
M10_fastener = ThreadedFastener(M10, [[5, 207e3], [10, 207e3]])
M5 = MetricBolt(5, 0.8, 23, '9.8', elastic_modulus=207e3, preload=7850)
M5_fastener = ThreadedFastener(M5, [[5, 207e3], [10, 207e3]])
fasteners = [M10_fastener, M10_fastener, M5_fastener]
fasteners_locations = [[20, 45, 0], [-20, 45, 0], [0, 15, 0]]
force = [0, -8500, 0]  # [N]
force_location = [0, 0, 100]
tilting_edge = [0, -0.000001, 0]
pattern = BoltPattern(fasteners, fasteners_locations, force, force_location, tilting_edge)

print(f"M5 bolt stiffness = {M5_fastener.bolt_stiffness}")
print(f"M5 sub stiffness = {M5_fastener.substrate_stiffness}")
print(f"M5 fastener stiffness = {M5_fastener.fastener_stiffness}")

print(f"M10 bolt stiffness = {M10_fastener.bolt_stiffness}")
print(f"M10 sub stiffness = {M10_fastener.substrate_stiffness}")
print(f"M10 fastener stiffness = {M10_fastener.fastener_stiffness}")
print("----")
print(f"shear force = {pattern.shear_force}")
print(f"shear stress = {pattern.shear_stress}")
print("----")
print(f"normal force = {pattern.normal_force}")
print(f"bolt tension = {pattern.bolt_tension}")
print(f"normal stress = {pattern.normal_stress}")
print("----")
print(f"equivalent_stresses = {pattern.equivalent_stresses}")
print("----")
print(f"load safety factor = {pattern.load_safety_factor(minimal=False)}")
print(f"separation safety factor = {pattern.separation_safety_factor(minimal=False)}")
print(f"proof safety factor = {pattern.proof_safety_factor(minimal=False)}")

print(f"M10 bolt load safety factor:{M10_fastener.load_safety_factor(pattern.equivalent_stresses[0])}")
print(f"M5 bolt separation safety factor:{M5_fastener.separation_safety_factor(pattern.normal_force[2])}")
print(f"M5 bolt proof safety factor:{M5_fastener.proof_safety_factor(pattern.equivalent_stresses[2])}")
pattern.get_info()