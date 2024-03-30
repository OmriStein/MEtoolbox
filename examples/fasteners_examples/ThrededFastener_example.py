from me_toolbox.fasteners import ThreadedFastener
from me_toolbox.fasteners import Bolt
from me_toolbox.fatigue import EnduranceLimit
diameter, pitch, length, threaded_length, grade, E = 12, 1.75, 55, 30, '9.8', 207e3
Sy, Sut, Sp = Bolt.get_strength_prop(diameter, grade)
M12 = Bolt(diameter, pitch, length, threaded_length, Sy, Sut, Sp, E)

thickness = [25, 7, 25]
elastic = [153e3, 128e3, 207e3]
layers = [[t, E] for t, E in zip(thickness, elastic)]  # [[25,153e3], [7,128e3], [25,207e3]]

preload = M12.estimate_preload(reused=True)
fastener = ThreadedFastener(M12, layers, nut=False, preload=preload)

km = fastener.member_stiffness
kb = fastener.bolt_stiffness
C = fastener.fastener_stiffness
print(f"km={km*1e-3:.2f}[kN/mm]\nkb={kb*1e-3:.2f}[kN/mm]\nC={C:.2f}\n")

print(f"Sp={M12.proof_strength}, At={M12.stress_area:.2f}, Fp={M12.proof_load:.2f}\n")

external_force = 10000  # [N]
n0, nL, np = fastener.safety_factors(external_force).values()
print(f"n0={n0:.2f}")
print(f"nL={nL:.2f}")
print(f"np={np:.2f}")

# print("Fatigue:")
# unmodified_Se = EnduranceLimit.unmodified_Se(Sut, 'steel')
# Se = M12.endurance_limit(unmodified_Se, 'cold-drawn', 300, 0.9)
# print(f"unmodified_Se:{unmodified_Se},modified_Se:{Se}")