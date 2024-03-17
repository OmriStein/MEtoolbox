from numpy import isclose

from me_toolbox.fasteners import Bolt
from me_toolbox.fasteners import ThreadedFastener
from me_toolbox.fasteners import BoltPattern

diameter, pitch, length, threaded_length, grade, E = 10, 1.5, 33, 26, '5.8', 207e3
Sp, Sut, Sy = Bolt.get_strength_prop(diameter, grade)
M10 = Bolt(diameter, pitch, length, threaded_length, Sy, Sut, Sp, E)
M10_fastener = ThreadedFastener(M10, [[10, 207e3], [50, 76e3]], nut=False)

diameter, pitch, length, threaded_length, grade, E = 8, 1.25, 30, 22, '5.8', 207e3
Sp, Sut, Sy = Bolt.get_strength_prop(diameter, grade)
M8 = Bolt(diameter, pitch, length, threaded_length, Sy, Sut, Sp, E)
M8_fastener = ThreadedFastener(M8, [[10, 207e3], [50, 76e3]], nut=False)

fasteners = [M10_fastener, M10_fastener, M8_fastener, M8_fastener]
fasteners_locations = [[-20, 20, 0], [-20, -20, 0], [-61, 0, 0], [-85, 0, 0]]
force = [0, 0, -8140]
preloads = [18750, 18750, 11812.5, 11812.5]
force_location = [40, 0, 0]

axis_of_rotation = [[0, 0], [0, 1]]
pattern = BoltPattern(fasteners, fasteners_locations, force, preloads, force_location,
                      axis_of_rotation, 'shank')

M8_kb = (M8.nominal_area * M8.stress_area * M8.elastic_modulus) / (
        M8.nominal_area * M8_fastener.griped_thread_length + M8.stress_area * M8.shank_length)
M10_kb = (M10.nominal_area * M10.stress_area * M10.elastic_modulus) / (
        M10.nominal_area * M10_fastener.griped_thread_length + M10.stress_area * M10.shank_length)
print(f"M8: ld={M8.shank_length}, lt={M8_fastener.griped_thread_length},"
      f"Ad={M8.nominal_area:.2f}, At={M8.stress_area:.2f}, kb={M8_kb:.2f},"
      f"km={M8_fastener.member_stiffness:.2f}, C={M8_fastener.fastener_stiffness:.3f}")
print(f"M10: ld={M10.shank_length}, lt={M10_fastener.griped_thread_length},"
      f"Ad={M10.nominal_area:.2f}, At={M10.stress_area:.2f}, kb={M10_kb:.2f},"
      f"km={M10_fastener.member_stiffness:.2f}, C={M10_fastener.fastener_stiffness:.3f}")
print(f"Fi={pattern.total_shear_force}\n\u03C4={pattern.shear_stress}")
print(f"PT={pattern.direct_normal_load}")
print(f"PM={pattern.bending_normal_load}")
print(f"P={pattern.fastener_load}\nFb={pattern.bolt_load}")
# print(f"PT={pattern.direct_normal_load}\nPMTV={pattern.bending_normal_load}")
print(f"\u03C3={pattern.normal_stress}")
print(f"\u03C3eq={pattern.equivalent_stresses}")

M10_nL, _, M8_nL, M8_nL_2 = [round(i, 2) for i in pattern.load_safety_factor(False)]
print(f"M10_nL={M10_nL:.2f},M8_nL={M8_nL:.2f},M8_nL_2={M8_nL_2:.2f}")

M10_n0, _, M8_n0, M8_n0_2 = [round(i, 2) for i in pattern.separation_safety_factor(False)]
print(f"M10_n0={M10_n0:.2f},M8_n0={M8_n0:.2f},M8_n0_2={M8_n0_2:.2f}")

M10_np, _, M8_np, M8_np_2 = [round(i, 2) for i in pattern.proof_safety_factor(False)]
print(f"M10_np={M10_np:.2f},M8_np={M8_np:.2f},M8_np_2={M8_np_2:.2f}")

print("------------")
fasteners2 = [M8_fastener, M8_fastener]
fasteners_locations2 = [[-61, 0, 0], [-85, 0, 0]]
preloads2 = [11812.5, 11812.5]
pattern2 = BoltPattern(fasteners2, fasteners_locations2, force, preloads2, force_location,
                       axis_of_rotation, 'shank')

print(f"Fi={pattern2.total_shear_force}\n\u03C4={pattern2.shear_stress}")
print(f"P={pattern2.fastener_load}\nFb={pattern2.bolt_load}")
# print(f"PT={pattern2.direct_normal_load}\nPMTV={pattern2.bending_normal_load}")
print(f"\u03C3={pattern2.normal_stress}")
print(f"\u03C3eq={pattern2.equivalent_stresses}")

M8_nL, M8_nL_2 = [round(i, 2) for i in pattern2.load_safety_factor(False)]
print(f"M8_nL={M8_nL:.2f},M8_nL_2={M8_nL_2:.2f}")

M8_n0, M8_n0_2 = [round(i, 2) for i in pattern2.separation_safety_factor(False)]
print(f"M8_n0={M8_n0:.2f},M8_n0_2={M8_n0_2:.2f}")

M8_np, M8_np_2 = [round(i, 2) for i in pattern2.proof_safety_factor(False)]
print(f"M8_np={M8_np:.2f},M8_np_2={M8_np_2:.2f}")

print(pattern.neutral_point)