from Springs import HelicalPushSpring
from sympy import symbols

G = 75e3  # [Mpa]
d = symbols('d', real=True, positive=True, rational=True)
C = 8  # the spring index C is defined as D/d
D = C * d

Fmax = 575
# it is a good practice for the force that compresses the spring to solid state to be: Fs=(1+zeta)Fmax
# where zeta is the overrun safety factor, it's customary that zeta=0.15 so Fs=1.15Fmax
z = 0.25
Fs = (1 + z) * Fmax
print(f"Fsolid = {Fs}")

# for music wire
Ap = 2211
m = 0.145

spring = HelicalPushSpring(force=Fmax, Ap=Ap, m=m, wire_diameter=d, spring_diameter=D, zeta=0.25,
                           shear_modulus=G, end_type='squared and ground', spring_constant=6.189,
                           set_removed=False, shot_peened=True, yield_percent=0.4)

# spring diameter for solid state safety factor of 1.5
print(f"minimum wire diameter for Fsolid = {spring.MinWireDiameter(1.5, solid=True)}")
print(f"minimum wire diameter for Fmax = {spring.MinWireDiameter(1.5)}")

spring.wire_diameter = 5.8079
spring.spring_diameter = C * 5.8079
print(f"Ls = {spring.solid_length}")
print(f"L0 = {spring.free_length}")
buckling = spring.Buckling('fixed-hinged', 205e3)
print(f"collapse: {buckling[0]}, max free length (L0) = {buckling[1]}")
nf, ns = spring.FatigueAnalysis(575, 185, 99.999)
print(f"fatigue safety factor={nf}, safety factor for first cycle={ns}\n")

spring2 = HelicalPushSpring(force=Fmax, Ap=2211, m=0.145, wire_diameter=6, spring_diameter=60,
                            shear_modulus=G, end_type='squared and ground', spring_constant=6,
                            set_removed=False, shot_peened=True, yield_percent=0.45,
                            ends='fixed-hinged', elastic_modulus=205e3)
print()
print(f"static safety factor = {spring2.static_safety_factor}")
print(f"minimum wire diameter for n=2: {spring2.MinWireDiameter(2)}")
buckling = spring2.Buckling('fixed-hinged', 205e3)
print(f"buckling: {buckling[0]}, max free length (L0) = {buckling[1]} , L0= {spring2.free_length}")

print(f"the natural frequency = {spring2.NaturalFrequency(8050):.2e} [Hz]")
