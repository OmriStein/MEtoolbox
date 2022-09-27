from me_toolbox.fasteners import ThreadedFastener
from me_toolbox.fasteners import MetricBolt
from me_toolbox.fasteners import Bolt, UNBolt
from me_toolbox.fatigue import EnduranceLimit, FatigueAnalysis

M12 = MetricBolt(12, 1.75, 75, '8.8')
# bolt = UNBolt(3 / 8, 24, True, 3, True, 0.5, '1')

thickness = [25, 7, 25]
elastic = [153e3, 128e3, 207e3]
layers = [[t, E] for t, E in zip(thickness, elastic)]  # [[25,153e3], [7,128e3], [25,207e3]]
fastener = ThreadedFastener(M12, layers, pre_load=25e3, load=18.12e3)

km = fastener.substrate_stiffness
kb = fastener.bolt_stiffness
C = fastener.fastener_stiffness
print(f"km={km*1e-3:.2f}[kN/mm]\nkb={kb*1e-3:.2f}[kN/mm]\nC={C:.2f}\n")

print(f"Sp={M12.proof_strength}, At={M12.stress_area:.2f}, Fp={M12.proof_load:.2f}\n")

M12.estimate_pre_load()

print(f"n0={fastener.separation_safety_factor:.2f}")
print(f"nL={fastener.load_safety_factor:.2f}")
print(f"np={fastener.proof_safety_factor:.2f}")

