from me_toolbox.fasteners import ThreadedFastener
from me_toolbox.fasteners import MetricBolt
from me_toolbox.fasteners import UnBolt

bolt = MetricBolt(10, 1.5, 'e', 3, 20)
thickness = [2, 3, 3, 2, 3]
Elastic = [200e3, 70e3, 200e3, 200e3, 200e3]
layers = [(t, E) for t, E in zip(thickness, Elastic)]
grip_len = (sum([layer[0] for layer in layers]))
fastener = ThreadedFastener(bolt, grip_len, layers)

bolt = UnBolt(3 / 8, 24, True, 3, True, 1)
print(bolt.thread_length)
print(bolt.stress_area)
print(bolt.minor_area)

