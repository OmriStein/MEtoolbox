from me_toolbox.gears import SpurGear, Transmission, HelicalGear

pinion = SpurGear(name='pinion', modulus=4, pressure_angle=25, teeth_num=25, rpm=1500, grade=2, Qv=11, crowned=False,
                  adjusted=True, width=25, bearing_span=10, pinion_offset=2, enclosure='extra precision enclosed',
                  hardness=400, number_of_cycles=1e8, material='steel',sensitive_use=True)

gearbox = Transmission(gear1=pinion, oil_temp=65, reliability=0.999, power=50e3, gear_ratio=3.1,
                       driving_machine='light shock', driven_machine='moderate shock', SF=1.1, SH=1)

helical = HelicalGear(name='pinion', modulus=2, pressure_angle=20, teeth_num=37, rpm=2500, grade=1, Qv=12,
                      crowned=False, adjusted=False, width=50, bearing_span=100, pinion_offset=22.4,
                      enclosure='precision enclosed', hardness=160, number_of_cycles=1e6, material='steel',
                      helix_angle=20, sensitive_use=True)

helical_gearbox = Transmission(gear1=helical, oil_temp=100, reliability=0.999, power=50e3, gear_ratio=2.5,
                               driving_machine='uniform', driven_machine='uniform', SF=1, SH=1)

gearbox.get_info()
