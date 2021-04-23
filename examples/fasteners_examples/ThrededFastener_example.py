from math import exp
from me_toolbox.fasteners import ThreadedFastener
from me_toolbox.fasteners import MetricBolt
from me_toolbox.fasteners import Bolt, UnBolt

d = 12
bolt = MetricBolt(d, 1.75, 'e', 3, 75, '8.8')
# bolt = UnBolt(3 / 8, 24, True, 3, True, 0.5, '1')

thickness = [25, 7, 25]
elastic = [153e3, 128e3, 207e3]

layers = [(t, E) for t, E in zip(thickness, elastic)]
grip_len = sum(thickness)
fastener = ThreadedFastener(bolt, grip_len, layers, 25e3, 18.12e3)
km = fastener.substrate_stiffness
kb = fastener.bolt_stiffness
k = fastener.stiffness_constant
print(f"km={km}\nkb={kb}\nk={k}")
print(f"Sp={bolt.proof_strength}, At={bolt.stress_area}, Fp={bolt.proof_load}")
bolt.estimate_pre_load()
print(fastener.separation_safety_factor)
print(fastener.load_safety_factor)
print(fastener.proof_safety_factor)