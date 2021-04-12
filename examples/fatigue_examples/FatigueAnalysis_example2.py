from fatigue import stress, EnduranceLimit, calc_kf, FatigueAnalysis
from math import pi, sqrt

Sut = 900  # [Mpa]
Sy = 700  # [Mpa]

Ft = 120  # [N]
Fn = 200  # [N]

N = Fn
V = Ft
T = 12 * 1e3  # [Nmm]
My = 5 * Ft
Mz = -100 * Fn
# equivalent moment
Me = sqrt(My ** 2 + Mz ** 2)

d = 16
A = 0.25 * pi * d ** 2
I = 0.25 * pi * (d / 2) ** 4
normal_stress = stress.uniform_stress(N, A)
bending_stress = stress.bending_stress(Me, I, 8)
torsion_stress = stress.torsion_stress(T, 8, 2 * I)
shear_stress = stress.max_shear_stress(V, A, 'circle')
print(f"Normal Stress = {normal_stress}\n"
      f"Bending Stress = {bending_stress}\n"
      f"Torsion Stress = {torsion_stress}\n"
      f"Shear Stress = {shear_stress}")

endurance_limit = EnduranceLimit(Sut=Sut, surface_finish='machined', rotating=True, max_bending_stress=bending_stress,
                                 max_normal_stress=normal_stress, material='steel', stress_type="multiple", temp=25,
                                 reliability=99, diameter=16)

print(f"Se'={endurance_limit.unmodified}, Se={endurance_limit.modified:.2f}")
endurance_limit.get_factors()

# dynamic stress concentration factors
Kf = calc_kf(0.9, 1.32)
Kfs = calc_kf(0.95, 1.12)

print(f"Kf={Kf:.3f}, Kfs={Kfs:.3f}")

fatigue_analysis = FatigueAnalysis(endurance_limit=endurance_limit, ductile=True, Sy=Sy,
                                   Kf_bending=Kf, Kf_torsion=Kfs, alt_bending_stress=bending_stress,
                                   mean_torsion_stress=torsion_stress)

print(f"Mean Equivalent Stress={fatigue_analysis.mean_eq_stress}\n"
      f"Alternating Equivalent Stress={fatigue_analysis.alt_eq_stress}\n")

nF, nl = fatigue_analysis.get_safety_factor('Modified Goodman', verbose=True)
soderberg_nF, _ = fatigue_analysis.get_safety_factor('Soderberg')
gerber_nF, _ = fatigue_analysis.get_safety_factor('gerber')
asme_nF, _ = fatigue_analysis.get_safety_factor('asme-elliptic')
print(f"soderberg={soderberg_nF} \ngerber={gerber_nF} \nasme={asme_nF}\n")

# miner for time to failure every group is of the following structure:
# [freq[Hz], alternating stresses, mean stresses]
# Note: In this case the stresses in the groups are alternating and mean (instead of the default max and min)
#       so the alt_mean flag should be True, and because we use frequency instead of number of repetitions
# the freq flag should be true
stresses = [[2, 700, 500], [5, 400, 540], [3, 900, -200]]
N_total = fatigue_analysis.miner_rule(stresses, Sut=1500, Se=750, verbose=True, alt_mean=True, freq=True)
