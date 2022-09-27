from me_toolbox.fasteners import MetricBolt
from me_toolbox.fasteners import ThreadedFastener
from me_toolbox.fasteners import BoltPattern

M8 = MetricBolt(8, 1.25, 30, '5.8', elastic_modulus=207e3, preload=11812.5)
M10 = MetricBolt(10, 1.5, 33, '5.8', elastic_modulus=207e3, preload=18750)

M8_fastener = ThreadedFastener(M8, [[10, 207e3], [50, 76e3]], nut=False)
M10_fastener = ThreadedFastener(M10, [[10, 207e3], [50, 76e3]], nut=False)

fasteners = [M10_fastener, M10_fastener, M8_fastener, M8_fastener]
fasteners_locations = [[-20, 20, 0], [-20, -20, 0], [-61, 0, 0], [-85, 0, 0]]

force = [0, 0, -8140]
force_location = [40, 0, 0]

tilting_edge = [0.000001, 0, 0]
pattern = BoltPattern(fasteners, fasteners_locations, force, force_location, tilting_edge)

print(f"load safety factor={pattern.load_safety_factor(minimal=False)}")
# print(f"separation safety factor={pattern.separation_safety_factor(minimal=False)}")
# print(f"proof safety factor={pattern.proof_safety_factor(minimal=False)}")
# pattern.get_info()
# pattern2 = BoltPattern(fasteners[2:], fasteners_locations[2:], force, force_location, tilting_edge)
#
# print(f"load safety factor={pattern2.load_safety_factor(minimal=False)}")
# pattern.get_info()
