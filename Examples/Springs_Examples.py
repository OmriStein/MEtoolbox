from Springs import HelicalPushSpring
from sympy import symbols

G = 75e3  # [Mpa]
d = symbols('d', real=True, positive=True, rational=True)
C = 8  # the spring index C is defined as D/d
D = C * d

Fmax = 575
# it is a good practice for the force that compresses the spring to solid state to be: Fs=(1+z)Fmax
# where z is the overrun safety factor, it's customary that z=0.15 so Fs=1.15Fmax
z = 0.25
Fs = (1 + z) * Fmax
print(f"Fsolid = {Fs}")

# for music wire
Ap = 2211
m = 0.145

# diam
spring = HelicalPushSpring(force=Fmax, Ap=Ap, m=m, wire_diameter=d, spring_diameter=D, z=0.25,
                           shear_modulus=G, end_type='squared and ground', spring_constant=6.189,
                           set_removed=False, shot_peened=True, yield_percent=0.45)

# spring diameter for solid state safety factor of 1.5
print(f"minimum wire diameter for Fsolid = {spring.MinWireDiameter(1.5, solid=True)}")
print(f"minimum wire diameter for Fmax = {spring.MinWireDiameter(1.5)}")

spring.wire_diameter = 5.8079
spring.spring_diameter = C * 5.8079
print(f"Ls = {spring.solid_length}")
print(f"L0 = {spring.free_length}")
collapse = spring.Collapse('fixed-hinged', 205e3)
print(f"collapse: {collapse[0]}, max free length (L0) = {collapse[1]} ")
