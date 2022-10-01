from me_toolbox.fasteners import Bolt
from me_toolbox.fasteners import ThreadedFastener
from me_toolbox.fasteners import BoltPattern


diameter, pitch, length, threaded_length, grade, E = 10, 1.5, 33, 26, '9.8', 207e3
Sp, Sut, Sy = Bolt.get_strength_prop(diameter, grade)
M10 = Bolt(diameter, pitch, length, threaded_length, Sy, Sut, Sp, E)
M10_fastener = ThreadedFastener(M10, [[5, 207e3], [10, 207e3]], nut=True)

diameter, pitch, length, threaded_length, grade, E = 5, 0.8, 23, 16, '9.8', 207e3
Sp, Sut, Sy = Bolt.get_strength_prop(diameter, grade)
M5 = Bolt(diameter, pitch, length, threaded_length, Sy, Sut, Sp, E)
M5_fastener = ThreadedFastener(M5, [[5, 207e3], [10, 207e3]], nut=True)

fasteners = [M10_fastener, M10_fastener, M5_fastener]
fasteners_locations = [[20, 45, 0], [-20, 45, 0], [0, 15, 0]]
force = [0, -8500, 0]  # [N]
preloads = [32062.5, 32062.5, 7850] # [N]
force_location = [0, 0, 100]
tilting_edge = [0, -0.000001, 0]
pattern = BoltPattern(fasteners, fasteners_locations, force, preloads, force_location, tilting_edge,
                      'shank')

M5_kb = (M5.nominal_area*M5.stress_area*M5.elastic_modulus)/(M5.nominal_area*M5_fastener.griped_thread_length+M5.stress_area*M5.shank_length)
M10_kb = (M10.nominal_area*M10.stress_area*M10.elastic_modulus)/(M10.nominal_area*M10_fastener.griped_thread_length+M10.stress_area*M10.shank_length)
print(f"M5: ld={M5.shank_length}, lt={M5_fastener.griped_thread_length},"
      f"Ad={M5.nominal_area:.2f}, At={M5.stress_area:.2f}, kb={M5_kb:.2f},"
      f"km={M5_fastener.member_stiffness:.2f}, C={M5_fastener.fastener_stiffness:.3f}")
print(f"M10: ld={M10.shank_length}, lt={M10_fastener.griped_thread_length},"
      f"Ad={M10.nominal_area:.2f}, At={M10.stress_area:.2f}, kb={M10_kb:.2f},"
      f"km={M10_fastener.member_stiffness:.2f}, C={M10_fastener.fastener_stiffness:.3f}")
print(f"Fi={pattern.total_shear_force}\n\u03C4={pattern.shear_stress}")
print(f"P={pattern.fastener_load}\nFb={pattern.bolt_load}")
print(f"\u03C3={pattern.normal_stress}")
print(f"\u03C3eq={pattern.equivalent_stresses}")
M10_nL = M10_fastener.load_safety_factor(preloads[0], pattern.equivalent_stresses[0])
M5_nL = M5_fastener.load_safety_factor(preloads[2], pattern.equivalent_stresses[2])
print(f"M10_nL={M10_nL:.2f},M5_nL={M5_nL:.2f}")
M10_n0 = M10_fastener.separation_safety_factor(preloads[0], pattern.fastener_load[0])
M5_n0 = M5_fastener.separation_safety_factor(preloads[2], pattern.fastener_load[2])
print(f"M10_n0={M10_n0:.2f},M5_n0={M5_n0:.2f}")
M10_np = M10_fastener.proof_safety_factor(pattern.equivalent_stresses[0])
M5_np = M5_fastener.proof_safety_factor(pattern.equivalent_stresses[2])
print(f"M10_np={M10_np:.2f},M5_np={M5_np:.2f}")
