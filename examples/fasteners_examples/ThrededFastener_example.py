from me_toolbox.fasteners import ThreadedFastener
from me_toolbox.fasteners import Bolt

diameter, pitch, length, threaded_length, grade, E = 12, 1.75, 55, 30, '9.8', 207e3
Sp, Sut, Sy = Bolt.get_strength_prop(diameter, grade)
M12 = Bolt(diameter, pitch, length, threaded_length, Sy, Sut, Sp, E)

thickness = [25, 7, 25]
elastic = [153e3, 128e3, 207e3]
layers = [[t, E] for t, E in zip(thickness, elastic)]  # [[25,153e3], [7,128e3], [25,207e3]]

fastener = ThreadedFastener(M12, layers, nut=False)

km = fastener.member_stiffness
kb = fastener.bolt_stiffness
C = fastener.fastener_stiffness
print(f"km={km*1e-3:.2f}[kN/mm]\nkb={kb*1e-3:.2f}[kN/mm]\nC={C:.2f}\n")

print(f"Sp={M12.proof_strength}, At={M12.stress_area:.2f}, Fp={M12.proof_load:.2f}\n")

preload = M12.estimate_preload(reused=True)
external_force = 10000  # [N]
bolt_load = fastener.bolt_load(preload, external_force)
eq = fastener.bolt_stress(bolt_load,M12.stress_area)
print(f"n0={fastener.separation_safety_factor(preload, external_force):.2f}")
print(f"nL={fastener.load_safety_factor(preload, eq):.2f}")
print(f"np={fastener.proof_safety_factor(eq):.2f}")

