from me_toolbox.fasteners import Bolt
from me_toolbox.fasteners import ThreadedFastener
from me_toolbox.fasteners import BoltPattern


diameter, pitch, length, threaded_length, grade, E = 10, 1.5, 33, 26, '9.8', 207e3
Sy, Sut, Sp = Bolt.get_strength_prop(diameter, grade)
M10 = Bolt(diameter, pitch, length, threaded_length, Sy, Sut, Sp, E)
M10_fastener = ThreadedFastener(M10, [[5, 207e3], [10, 207e3]], nut=True, preload=32062.5)

diameter, pitch, length, threaded_length, grade, E = 5, 0.8, 23, 16, '9.8', 207e3
Sy, Sut, Sp = Bolt.get_strength_prop(diameter, grade)
M5 = Bolt(diameter, pitch, length, threaded_length, Sy, Sut, Sp, E)
M5_fastener = ThreadedFastener(M5, [[5, 207e3], [10, 207e3]], nut=True, preload=7850)

fasteners = [M10_fastener, M10_fastener, M5_fastener]
fasteners_locations = [[20, 45, 0], [-20, 45, 0], [0, 15, 0]]
force = [0, -8500, 0]  # [N]
force_location = [0, 0, 100]
axis_of_rotation = [[0, 0], [1, 0]]  # Two points on the axis of rotation
pattern = BoltPattern(fasteners, fasteners_locations, force, force_location,
                      axis_of_rotation, 'shank')

print(f"M5: ld={M5.shank_length}, lt={M5_fastener.griped_thread_length},"
      f"Ad={M5.nominal_area:.2f}, At={M5.stress_area:.2f}, kb={M5_fastener.bolt_stiffness:.2f},"
      f"km={M5_fastener.member_stiffness:.2f}, C={M5_fastener.fastener_stiffness:.3f}")

print(f"M10: ld={M10.shank_length}, lt={M10_fastener.griped_thread_length},"
      f"Ad={M10.nominal_area:.2f}, At={M10.stress_area:.2f}, kb={M10_fastener.bolt_stiffness:.2f},"
      f"km={M10_fastener.member_stiffness:.2f}, C={M10_fastener.fastener_stiffness:.3f}")

print(f"Fi={pattern.total_shear_force}\n\u03C4={pattern.shear_stress}")
print(f"P={pattern.fastener_load}\nFb={pattern.bolt_load}")

print(f"\u03C3={pattern.normal_stress}")
print(f"\u03C3eq={pattern.equivalent_stresses}")

M10_nL = M10_fastener.load_safety_factor(pattern.equivalent_stresses[0])
M5_nL = M5_fastener.load_safety_factor(pattern.equivalent_stresses[2])
print(f"M10_nL={M10_nL:.2f},M5_nL={M5_nL:.2f}")
M10_n0 = M10_fastener.separation_safety_factor(pattern.fastener_load[0])
M5_n0 = M5_fastener.separation_safety_factor(pattern.fastener_load[2])
print(f"M10_n0={M10_n0:.2f},M5_n0={M5_n0:.2f}")
M10_np = M10_fastener.proof_safety_factor(pattern.equivalent_stresses[0])
M5_np = M5_fastener.proof_safety_factor(pattern.equivalent_stresses[2])
print(f"M10_np={M10_np:.2f},M5_np={M5_np:.2f}")
