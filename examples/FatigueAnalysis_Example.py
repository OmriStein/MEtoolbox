from fatigue_analysis import *
from math import pi
from sympy import symbols, solveset, Eq
from sympy.sets import Reals

# Normal load: N=F*(0.5+sin(wt))
# applied torque: T=2.5*F*sin(wt)

# finding factor of safety ad a function of the force F
F = symbols('F', real=True, positive=True)

# the extreme loads
normal_Force_min = -0.5 * F
normal_Force_max = 1.5 * F
torque_min = -2.5 * F
torque_max = 2.5 * F

# calculating mean and alternating forces
mean_force = (normal_Force_max + normal_Force_min) / 2
alternating_force = abs(normal_Force_max - normal_Force_min) / 2

mean_torque = (torque_max + torque_min) / 2
alternating_torque = abs(torque_max - torque_min) / 2

print(f"Fa={alternating_force}, Fm={mean_force}, Ta={alternating_torque}, Tm={mean_torque}")

Area = 0.25 * pi * 10 ** 2
# calculating the stresses
mean_normal_stress = uniform_stress(mean_force, Area)
alternating_normal_stress = uniform_stress(alternating_force, 0.25 * pi * 10 ** 2)

mean_shear_stress = torsion_stress(mean_torque, 5, (pi / 32) * 10 ** 4)
alternating_shear_stress = torsion_stress(alternating_torque, 5, (pi / 32) * 10 ** 4)

print(f"σaN={alternating_normal_stress}, σmN={mean_normal_stress},"
      f"𝜏aT={alternating_shear_stress}, 𝜏mT={mean_shear_stress}")

max_normal_stress = uniform_stress(normal_Force_max, Area)

endurance_limit = EnduranceLimit(Sut=700, surface_finish='machined', rotating=False, material='steel',
                                 max_normal_stress=max_normal_stress, max_bending_stress=0,
                                 stress_type="multiple", temp=25, reliability=90, diameter=10)

print(f"Se'={endurance_limit.unmodified}, Se={endurance_limit.modified:.2f}")
endurance_limit.get_factors()


# dynamic stress concentration factors
Kf = calc_kf(0.7, 2.35)
Kfs = calc_kf(0.75, 1.73)

print(f"Kf={Kf:.3f}, Kfs={Kfs:.3f}")

# creating fatigue_analysis object
fatigue_analysis = FatigueAnalysis(Sut=700, Sy=525, ductile=True, Kf_normal=Kf, Kf_torsion=Kfs,
                                   endurance_limit=endurance_limit,
                                   alternating_normal_stress=alternating_normal_stress,
                                   alternating_torsion_stress=alternating_shear_stress,
                                   mean_normal_stress=mean_normal_stress,
                                   mean_torsion_stress=mean_shear_stress)

print(f"Mean Equivalent Stress={fatigue_analysis.mean_equivalent_stress}\n"
      f"Alternating Equivalent Stress={fatigue_analysis.alternating_equivalent_stress}")

# safety factor
nF_modified_goodman = fatigue_analysis.modified_goodman
print(f"modified goodman safety factor (as a function of F): {nF_modified_goodman}")

# creating the safety factor equation and isolating F (F as a function of the safety factor)
nF = symbols('nF', real=True)
solution = solveset(Eq(nF, nF_modified_goodman), F, Reals)

# the force as a function of safety factor (nF)
F2 = solution.args[1].args[0]
print(f"the Force (as a function of nF): {F2}")

# The Force if the safety factor is 2
print(f"The Force for safety factor 2= {F2.subs(nF, 2):.2f}")

# Langer static safety factor
F3 = F2.subs(nF, 2)
print(f"Langer static safety factor= {fatigue_analysis.langer_static_yield.subs(F, F3):.2f} for F= {F3:.2f}[N]")

# using the get safety factor method
nF, nl = fatigue_analysis.get_safety_factor('modified Goodman')
print(f"Safety factors for infinite cycles: nF={nF.subs(F, 6e3)}, nl={nl.subs(F, 6e3)}")

# calculating the number of cycles until failure for F=6000
# assigning F=6000 in the mean and alternating stress attributes in the existing fatigue_analysis
fatigue_analysis.mean_equivalent_stress = fatigue_analysis.mean_equivalent_stress.subs(F, 6000)
fatigue_analysis.alternating_equivalent_stress = fatigue_analysis.alternating_equivalent_stress.subs(F, 6000)

print("Mean Equivalent Stress:", fatigue_analysis.mean_equivalent_stress,
      "\nAlternating Equivalent Stress:", fatigue_analysis.alternating_equivalent_stress)

# number of cycles until failure
print(f"N={fatigue_analysis.num_of_cycle()[0]:,.2e}, Sf={fatigue_analysis.num_of_cycle()[1]:,.2f}")

# Miners law Sf(5e8)=90[MPa]
# the format [number_of_repetitions,maximum_stress, minimum_stress]
stress_groups = [[2, 150, -50], [3, 200, -50], [2, 350, -100], [1, 400, -300], [1, 200, -50]]
N_total = fatigue_analysis.miner_rule(stress_groups, Sut=480, Se=90, Sy=410, z=-5.69)
print(f"number of cycles to failure = {N_total}")
