from me_toolbox.springs import HelicalCompressionSpring
from sympy import symbols

from springs import Spring

G = 75e3  # [Mpa]
d = symbols('diameter', real=True, positive=True, rational=True)
C = 8  # the spring index C is defined as D/diameter
D = C * d

Fmax = 575
# it is good practice for the max_force that compresses
# the spring to solid state to be: Fs=(1+zeta)Fmax
# where zeta is the overrun safety factor,
# it's customary that zeta=0.15 so Fs=1.15Fmax
z = 0.25
Fs = (1 + z) * Fmax
print(f"Fsolid = {Fs}")

# for music wire
Sut = Spring.material_prop('music wire', 6.5, metric=True, verbose=True)
print(f"Sut={Sut:.2f}")

spring = HelicalCompressionSpring(max_force=Fmax, wire_diameter=d, spring_diameter=D,
                                  ultimate_tensile_strength=Sut, end_type='squared and ground',
                                  shear_modulus=G, elastic_modulus=205e3, shear_yield_percent=0.45,
                                  spring_rate=6.189, set_removed=False, shot_peened=True,
                                  anchors='fixed-hinged', zeta=0.25)

# spring diameter for solid state safety factor of 1.5
print(f"minimum wire diameter for Fsolid = {spring.min_wire_diameter(1.5, solid=True)}")
print(f"minimum wire diameter for Fmax = {spring.min_wire_diameter(1.5)}")

spring.wire_diameter = 5.8079
spring.spring_diameter = C * 5.8079
print(f"Ls = {spring.solid_length}")
print(f"L0 = {spring.free_length}")
buckling = spring.buckling
print(f"collapse: {buckling[0]}, max free length (L0) = {buckling[1]}")
print(f"static safety factor = {spring.static_safety_factor()}")
nf, ns = spring.fatigue_analysis(575, 185, 99.999)
print(f"fatigue safety factor={nf}, safety factor for first cycle={ns}\n")

spring2 = HelicalCompressionSpring(max_force=Fmax, wire_diameter=6, spring_diameter=60,
                                   ultimate_tensile_strength=Sut, end_type='squared and ground',
                                   shear_modulus=G, elastic_modulus=205e3, shear_yield_percent=0.45,
                                   spring_rate=6, set_removed=False, shot_peened=True,
                                   anchors='fixed-hinged')
print()
print(f"static safety factor = {spring2.static_safety_factor()}")
print(f"minimum wire diameter for n=2: {spring2.min_wire_diameter(2)}")
buckling = spring2.buckling
print(f"buckling: {buckling[0]}, max free length (L0) = {buckling[1]} , L0= {spring2.free_length}")

print(f"the natural frequency = {spring2.natural_frequency} [Hz]")
