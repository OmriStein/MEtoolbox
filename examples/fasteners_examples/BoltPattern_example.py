# from me_toolbox.fasteners import ThreadedFastener
from me_toolbox.fasteners import MetricBolt
from me_toolbox.fasteners import BoltPattern
# from me_toolbox.fasteners import Bolt, UNBolt
# from me_toolbox.fatigue import EnduranceLimit, FatigueAnalysis
# import numpy as np
import sympy

M16 = MetricBolt(16, 2, 30, '8.8')
#
# print(f"Sp={M16.proof_strength}, At={M16.stress_area:.2f}, Fp={M16.proof_load:.2f}\n")
#
# M16.estimate_pre_load()
#
# thickness = [10, 15]
# elastic = [207e3, 207e3]
# layers = [[t, E] for t, E in zip(thickness, elastic)]  # [[10,207e3], [15,207e3]]
# fastener = ThreadedFastener(M16, layers, pre_load=0.75*M16.proof_load, load=1e-3)
#
# km = fastener.substrate_stiffness
# kb = fastener.bolt_stiffness
# C = fastener.fastener_stiffness
#
# print(f"km={km*1e-3:.2f}[kN/mm]\nkb={kb*1e-3:.2f}[kN/mm]\nC={C:.2f}\n")
#
# print(f"n0={fastener.separation_safety_factor:.2f}")
# print(f"nL={fastener.load_safety_factor:.2f}")
# print(f"np={fastener.proof_safety_factor:.2f}")

# bolts type and location
# bolts = [[M16, [75, -60, 0]],
#          [M16, [75, 60, 0]],
#          [M16, [-75, 60, 0]],
#          [M16, [-75, -60, 0]]]  # [mm]
# # force and location
# force = [0, -16, 0]  # [KN]
# force_location = [425, 0, 0]
# pattern = BoltPattern(bolts, force, force_location)


M20 = MetricBolt(20, 2.5, 30, '8.8')
bolts2 = [[M20, [-100, 0, 0]],
          [M20, [0, 0, 0]],
          [M20, [100, 0, 0]],
          [M20, [200, 0, 0]]]

p = sympy.Symbol('p')
force2 = [0, 1, 0]
force_location2 = [0, 0, 0]
pattern2 = BoltPattern(bolts2, force2, force_location2)
# pattern2.get_info()
