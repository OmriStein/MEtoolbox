# me_toolbox.gears package

## Submodules

## me_toolbox.gears.helical_gear module

Module containing the HelicalGear class


### class me_toolbox.gears.helical_gear.HelicalGear(name, modulus, teeth_num, rpm, Qv, width, bearing_span, pinion_offset, enclosure, hardness, pressure_angle, helix_angle, grade, work_hours=0, number_of_cycles=0, crowned=False, adjusted=False, sensitive_use=False, nitriding=False, case_carb=False, material='steel')
Bases: `me_toolbox.gears.spur_gear.SpurGear`

A gear object that contains all of its design parameters (AGMA 2001-D04)


#### static Y_j(gear1, gear2)
Return Geometry factors for helical gear and pinion
Yj is dependent on the gear ratio, helix angle and both gears teeth numbers


* **Parameters**

    
    * **gear1** (*HelicalGear*) – Helical gear object


    * **gear2** (*HelicalGear*) – Helical gear object



* **Returns**

    Yj - Geometric factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### static ZI(gear1, gear2)
Return geometric factor for contact failure
ZI is dependent on the gear ratio, pressure angle, modulus and both gears teeth numbers


* **Parameters**

    
    * **gear1** (*HelicalGear*) – gear object


    * **gear2** (*HelicalGear*) – gear object



* **Returns**

    ZI - geometric factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property axial_modulus()
Calculate axial modulus


* **Returns**

    Gear’s axial modulus



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property axial_pitch()
Calculate axial pitch


* **Returns**

    Gear’s axial pitch



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### calc_centers_distance(gear_ratio)
calculate the distance between the centers of the gears


* **Parameters**

    **gear_ratio** ([*float*](https://docs.python.org/3/library/functions.html#float)) – transmissions gear ratio



* **Returns**

    the distance between the transmissions gears centers in [mm]



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### static calc_forces(gear, power)
Calculate forces on helical gear


* **Parameters**

    
    * **gear** (*HelicalGear*) – gear object


    * **power** ([*float*](https://docs.python.org/3/library/functions.html#float)) – power



* **Returns**

    Wt - tangent max_force in [N], Wr - radial max_force in [N], Wx - axial max_force in [N]



* **Return type**

    [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[float](https://docs.python.org/3/library/functions.html#float), [float](https://docs.python.org/3/library/functions.html#float), [float](https://docs.python.org/3/library/functions.html#float)]



#### check_compatibility(gear)
Raise error if the pressure angle, helix angle or modulus of the gears don’t match


* **Parameters**

    **gear** (*HelicalGear*) – gear object



* **Raises**

    
    * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError)**(****"gear1 and gear2 have mismatch pressure_angle"****)** – 


    * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError)**(****"gear1 and gear2 have mismatch Helix_angle"****)** – 


    * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError)**(****"gear1 and gear2 are not the same type****, ****they are no compatible"****)** – 


    * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError)**(****"gear1 and gear2 have mismatch modulus"****)** – 



#### static create_new_gear(gear2_prop)
return a new instance of HelicalGear


* **Parameters**

    **gear2_prop** ([*dict*](https://docs.python.org/3/library/stdtypes.html#dict)) – gear properties



* **Returns**

    HelicalGear object



* **Type**

    HelicalGear



#### static format_properties(properties)
Remove excess attributes form properties


* **Parameters**

    **properties** ([*list*](https://docs.python.org/3/library/stdtypes.html#list)) – a list of gear properties



* **Returns**

    A dictionary of properties



* **Return type**

    [dict](https://docs.python.org/3/library/stdtypes.html#dict)



#### optimization(transmission, optimize_feature='all', verbose=False)
Perform gear optimization


* **Parameters**

    
    * **transmission** (*gears.transmission.Transmission*) – Transmission object
    associated with the gear


    * **optimize_feature** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – property to optimize for (‘width’/’volume’/’center’)


    * **verbose** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – print optimization stages



* **Returns**

    optimized result (width in mm, volume in mm^3, center distance in mm)



* **Return type**

    [dict](https://docs.python.org/3/library/stdtypes.html#dict)



#### property pitch_diameter()
Calculate pitch diameter


* **Returns**

    Gear’s pitch diameter



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property tangent_modulus()
Calculate tangent modulus


* **Returns**

    Gear’s tangent modulus



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property tangent_pitch()
Calculate tangent pitch


* **Returns**

    Gear’s tangent pitch



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property tangent_pressure_angle()
Calculate tangent pressure angle


* **Returns**

    Gear’s tangent pressure angle



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)


## me_toolbox.gears.spur_gear module

Module containing the SpurGear class


### class me_toolbox.gears.spur_gear.SpurGear(name, modulus, teeth_num, rpm, Qv, width, bearing_span, pinion_offset, enclosure, hardness, pressure_angle, grade, work_hours=0, number_of_cycles=0, crowned=False, adjusted=False, sensitive_use=False, nitriding=False, case_carb=False, material='steel')
Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

A gear object that contains all of its design parameters (AGMA 2001-D04)


#### property KB()
Rim thickness factor, factor_KB is dependent on the number of teeth


* **Returns**

    Gear’s Rim thickness factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property KH()
Load distribution factor, KH is dependent on: the shape of teeth (crowned),
if teeth are adjusted after assembly (adjusted), the gear width in [mm],
pitch diameter in [mm], bearing span (the distance between the bearings center lines)
pinion offset (the distance from the bearing span center to the pinion mid-face)
enclosure type (open gearing, commercial enclosed, precision enclosed,
extra precision enclosed)


* **Returns**

    Gear’s load distribution factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property Ks()
Size factor, factor_Ks is dependent on the circular
pitch (p=πm) which in turn depends on the modulus


* **Returns**

    Gear’s size factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property Kv()
Dynamic factor, Kv is dependent on the pitch diameter in [mm],
the angular velocity in [rpm] and Qv (transmission accuracy grade number)

note: the equations here are from “Shigley’s Mechanical Engineering Design”

    in the AGMA standard the transmission accuracy grade number is Av instead of Qv
    and its value is inverted, high Qv is more accurate and high Av is less accurate


* **Returns**

    Gear’s Dynamic factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property Sc()
Contact safety factor, Sc is dependent on the gear
hardness in [HBN] and on the material grade
(material grade of the gear 1 for regular use 2 for military and sensitive uses)


* **Returns**

    Gear’s contact safety factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property St()
Bending safety factor, St is dependent on the gear’s

    hardness in [HBN] and the material grade
    (material grade of the gear 1 for regular use 2 for military and sensitive uses)


* **Returns**

    Gear’s bending safety factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property YN()
Bending strength stress cycle factor


* **Returns**

    Gear’s bending strength stress cycle factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### static Y_j(gear1, gear2)
Return Geometry factors for spur gear and pinion


* **Returns**

    Gear’s geometry factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### static ZI(gear1, gear2)
Geometric factor for contact failure,
ZI is dependent on the gear ratio and pressure angel


* **Parameters**

    
    * **gear1** (*SpurGear*) – gear object


    * **gear2** (*SpurGear*) – gear object



* **Returns**

    ZI - geometric factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property ZN()
Calculating contact strength stress cycle factor


* **Returns**

    Gear’s contact strength stress cycle



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property ZR()
For now ZR is 1 according to the AGMA standard
:rtype: int


#### calc_centers_distance(gear_ratio)
Calculate the distance between the centers of the gears
:param float gear_ratio: transmissions gear ratio


* **Returns**

    the distance between the transmissions gears centers  in [mm]



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### static calc_forces(gear, power)
Calculate forces on the gear


* **Parameters**

    
    * **gear** (*SpurGear*) – gear object


    * **power** ([*float*](https://docs.python.org/3/library/functions.html#float)) – power



* **Returns**

    Wt - tangent max_force in [N], Wr - radial max_force in [N]



* **Return type**

    [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[float](https://docs.python.org/3/library/functions.html#float), [float](https://docs.python.org/3/library/functions.html#float)]



#### check_compatibility(gear)
Raise error if the pressure angle, helix angle or modulus of the gears don’t match


* **Parameters**

    **gear** (*HelicalGear*) – gear object



* **Raises**

    
    * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError)**(****"gear1 and gear2 have mismatch pressure_angle"****)** – 


    * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError)**(****"gear1 and gear2 have mismatch Helix_angle"****)** – 


    * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError)**(****"gear1 and gear2 are not the same type****, ****they are no compatible"****)** – 


    * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError)**(****"gear1 and gear2 have mismatch modulus"****)** – 



#### static create_new_gear(gear2_prop)
Return a new instance of SpurGear


* **Parameters**

    **gear2_prop** ([*dict*](https://docs.python.org/3/library/stdtypes.html#dict)) – gear properties



* **Returns**

    SpurGear object



* **Type**

    SpurGear



#### cycles_or_hours()
Check if the gear number of cycles or work hours
were input and return the number of cycle


* **Returns**

    Gear’s Dynamic factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or [None](https://docs.python.org/3/library/constants.html#None)



* **Raises**

    [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – number of cycles and work hours entered but they’re not matching
    or no number of cycles or work hours entered



#### static format_properties(properties)
Remove excess attributes form properties


* **Parameters**

    **properties** ([*list*](https://docs.python.org/3/library/stdtypes.html#list)) – a list of gear properties



* **Returns**

    A dictionary of properties



* **Return type**

    [dict](https://docs.python.org/3/library/stdtypes.html#dict)



#### get_factors(verbose=True)
Print correction factors for gear strength analysis


* **Parameters**

    **verbose** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Print factors



* **Return type**

    [dict](https://docs.python.org/3/library/stdtypes.html#dict)



#### get_info()
Print all the class fields with values


#### optimization(transmission, optimize_feature='all', verbose=False)
Perform gear optimization


* **Parameters**

    
    * **transmission** (*gears.transmission.Transmission*) – Transmission object
    associated with the gears


    * **optimize_feature** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – property to optimize for (‘width’/’volume’/’center’)


    * **verbose** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – print optimization stages



* **Returns**

    optimized result (width in mm, volume in mm^3, center distance in mm)



* **Return type**

    [dict](https://docs.python.org/3/library/stdtypes.html#dict)



#### property pitch()
Calculate circular pitch


* **Returns**

    Gear’s circular pitch



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property pitch_diameter()
Calculate pitch diameter


* **Returns**

    Gear’s pitch diameter



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property tangent_velocity()
Convert tangent velocity to [m/s] from [rpm]


* **Returns**

    Gear’s tangent velocity



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)


## me_toolbox.gears.transmission module

Module containing the Transmission Class


### exception me_toolbox.gears.transmission.GearTypeError()
Bases: [`ValueError`](https://docs.python.org/3/library/exceptions.html#ValueError)

Error class, inherits from ValueError


### class me_toolbox.gears.transmission.Transmission(driving_machine, driven_machine, oil_temp, reliability, power, SF, gear1, gear2=None, gear_ratio=0, SH=1)
Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Transmission object containing the transmission design parameters
and methods to perform strength analysis on its gears. (AGMA 2001-D04)


#### property Ko()
overload factor
Ko is dependent on the type of driving motor type (Electric Motor/Turbine - uniform,
multi-cylinder engine - light shock, single-cylinder engine - medium shock)
and on the driven machine type (uniform, moderate shock, heavy shock)


#### property Ytheta()
calculating Temperature factor


* **Returns**

    y_theta - The temperature factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property Yz()
calculating Reliability factor
input: reliability_num - reliability percentage
output: Y_z - Reliability factor


#### property ZE()
Elastic coefficient
ZE is dependent on the gears material


#### allowed_bending_stress(gear)
calculating allowed bending stress


* **Parameters**

    **gear** (*Union**[**SpurGear**, **HelicalGear**]*) – gear object



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### allowed_contact_stress(gear)
calculating allowed contact stress


* **Parameters**

    **gear** (*Union**[**SpurGear**, **HelicalGear**]*) – gear object



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### bending_stress(gear)
calculating bending stress


* **Parameters**

    **gear** (*Union**[**SpurGear**, **HelicalGear**]*) – gear object



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property centers_distance()
calculate the distance between the centers of the gears


* **Returns**

    the distance between the transmissions gears centers in [mm]



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### check_undercut()
Checks undercut state


#### contact_stress(gear)
calculating contact stress


* **Parameters**

    **gear** (*Union**[**SpurGear**, **HelicalGear**]*) – gear object



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### get_factors(verbose=True)
retrieve transmission analysis factors


* **Parameters**

    **verbose** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – print factors



* **Return type**

    [dict](https://docs.python.org/3/library/stdtypes.html#dict)



#### get_info()
print all the class fields with values


#### life_expectency(gear, in_hours=False)
try calculating expected life span of the gear if not
possible return  stress cycle factors (YN/ZN)


* **Example**

    helical = HelicalGear(gear_properties)
    gearbox = Transmission(transmission_properties)
    gearbox.LifeExpectency(helical, in_hours=True)



* **Parameters**

    
    * **gear** (*Gear*) – gear object


    * **in_hours** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – return gears life expectency in hours



* **Returns**

    Number of cycles / work hours



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### minimal_hardness(gear)
return the minimum hardness of the gear to avoid failure


#### minimum_width_for_bending(gear)
calculating minimum gear width to withstand bending stress


* **Parameters**

    **gear** (*Union**[**SpurGear**, **HelicalGear**]*) – gear object



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### minimum_width_for_contact(gear)
calculating minimum gear width to withstand contact stress


* **Parameters**

    **gear** (*Union**[**SpurGear**, **HelicalGear**]*) – gear object



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### optimize(gear, optimize_feature='all', verbose=False)
perform gear optimization

example: result, results_list = gearbox.Optimize(pinion, optimize_feature=’volume’, verbose=True)

note: result of width in [mm], volume in [mm^3] and center distance in [mm]


* **Parameters**

    
    * **gear** (*SpurGear**, **HelicalGear*) – gear object


    * **optimize_feature** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – property to optimize for (‘width’/’volume’/’center’)


    * **verbose** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – print optimization stages



* **Returns**

    optimized result and list of other viable options



* **Return type**

    [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)


## Module contents
