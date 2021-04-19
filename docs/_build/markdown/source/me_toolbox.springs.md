# me_toolbox.springs package

## Submodules

## me_toolbox.springs.extension_spring module

A module containing the extension spring class


### class me_toolbox.springs.extension_spring.ExtensionSpring(max_force, initial_tension, wire_diameter, spring_diameter, hook_r1, hook_r2, shear_modulus, elastic_modulus, body_shear_yield_percent, end_normal_yield_percent, end_shear_yield_percent, Ap, m, spring_constant=None, active_coils=None, body_coils=None, shot_peened=False, free_length=None, density=None, working_frequency=None)
Bases: `me_toolbox.springs.spring.Spring`

An extension spring object


#### property active_coils()
getter for the `active_coils` attribute


* **Returns**

    The spring active coils



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property body_coils()
getter for the `body_coils` attribute


* **Returns**

    The spring body coils



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property body_shear_yield_strength()
Ssy - yield strength for shear
(shear_yield_stress = % \* ultimate_tensile_strength))


* **Returns**

    yield strength for shear stress



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### calc_active_coils()
Calculate Na which is the number of active coils
(using Castigliano’s theorem)


* **Returns**

    number of active coils



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### calc_body_coils()
Calculate active_coils which is the number of active coils (using Castigliano’s theorem)


* **Returns**

    number of active coils



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### calc_deflection(force)
Calculate the spring max_deflection (change in length) due to a specific max_force


* **Parameters**

    **or Symbol force** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Spring working max_force



* **Returns**

    Spring max_deflection



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### calc_free_length()
Calculates the free length of the spring


* **Returns**

    free_length - The free length



* **Return type**

    float of Symbol



#### calc_max_normal_stress(force)
Calculates the normal stress based on the max_force given


* **Parameters**

    **of Symbol force** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Working max_force of the spring



* **Returns**

    normal stress



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### check_design(verbose=False)
Check if the spring index,active_coils,zeta and free_length
are in acceptable range for a good design


* **Returns**

    True if all the checks are good



* **Return type**

    [bool](https://docs.python.org/3/library/functions.html#bool)



#### property end_normal_yield_strength()
getter for the yield strength attribute (Sy = % \* Sut)


* **Returns**

    end bending yield strength



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property end_shear_yield_strength()
getter for the yield strength attribute (Sy = % \* Sut)


* **Returns**

    end bending yield strength



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property factor_Kw()
K_W - Wahl shear stress concentration factor


* **Returns**

    Wahl shear stress concentration factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### fatigue_analysis(max_force, min_force, reliability, criterion='gerber', verbose=False, metric=True)
Fatigue analysis of the hook section
for normal and shear stress,and for the
body section for shear and static yield.


* **Parameters**

    
    * **max_force** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Maximal max_force acting on the spring


    * **min_force** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Minimal max_force acting on the spring


    * **reliability** ([*float*](https://docs.python.org/3/library/functions.html#float)) – in percentage


    * **criterion** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – fatigue criterion


    * **verbose** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – print more details


    * **metric** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Metric or imperial



* **Returns**

    Normal and shear safety factors for the hook section and
    static and dynamic safety factors for body section



* **Return type**

    [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[float](https://docs.python.org/3/library/functions.html#float), [float](https://docs.python.org/3/library/functions.html#float), [float](https://docs.python.org/3/library/functions.html#float), [float](https://docs.python.org/3/library/functions.html#float)]



#### property free_length()
getter for the `free_length` attribute


* **Returns**

    free length of the springs



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property hook_KA()
Returns The spring’s bending stress correction factor


* **Returns**

    Bending stress correction factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property hook_KB()
Returns The spring’s torsional stress correction factor


* **Returns**

    Torsional stress correction factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### property max_body_shear_stress()
The spring’s body torsion stress


* **Returns**

    Body torsion stress



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property max_deflection()
Returns the spring max_deflection, It’s change in length


* **Returns**

    Spring max_deflection



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### property max_hook_normal_stress()
The normal stress due to bending and axial loads


* **Returns**

    Normal stress



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### property max_hook_shear_stress()
The spring’s hook torsion stress


* **Returns**

    Hook torsion stress



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### min_spring_diameter(static_safety_factor)
return the minimum spring diameter to avoid static failure
according to the given safety factor.


* **Parameters**

    **static_safety_factor** ([*float*](https://docs.python.org/3/library/functions.html#float)) – factor of safety



* **Returns**

    The minimal spring diameter



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### min_wire_diameter(safety_factor, spring_index=None)
The minimal wire diameters (for shear and normal stresses)
for a given safety factor in order to avoid failure,

Because KA and KB contains d no simple solution is available as in the
HelicalPushSpring, so we assume an initial K and iterate until convergence,
be aware that for some static_safety_factor a convergence my not occur.

NOTE: for static use only


* **Parameters**

    
    * **safety_factor** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Static safety factor


    * **spring_index** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Spring index



* **Returns**

    The minimal wire diameter



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[Symbol, Symbol]



#### property spring_constant()
getter for the `spring_constant` attribute


* **Returns**

    The spring constant



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property spring_diameter()
Getter for the spring diameter attribute


* **Returns**

    The spring diameter



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### property static_safety_factor()
Returns the static safety factors for the hook (torsion and
bending), and for the spring’s body (torsion)


* **Returns**

    Spring’s body (torsion) safety factor, Spring’s hook bending safety factor,
    Spring’s hook torsion safety factor



* **Type**

    [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[float](https://docs.python.org/3/library/functions.html#float), [float](https://docs.python.org/3/library/functions.html#float), [float](https://docs.python.org/3/library/functions.html#float)] or [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[Symbol, Symbol, Symbol]



#### property wire_diameter()
Getter for the wire diameter attribute


* **Returns**

    The spring’s wire diameter



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol


## me_toolbox.springs.helical_push_spring module

A module containing the helical push spring class


### class me_toolbox.springs.helical_push_spring.HelicalPushSpring(max_force, wire_diameter, spring_diameter, end_type, shear_modulus, elastic_modulus, shear_yield_percent, Ap, m, spring_constant=None, active_coils=None, free_length=None, density=None, working_frequency=None, set_removed=False, shot_peened=False, anchors=None, zeta=0.15)
Bases: `me_toolbox.springs.spring.Spring`

A helical push spring object


#### property Fsolid()
calculate the max_force necessary to bring the spring to solid length
it is a good practice for the max_force that compresses the spring to
solid state to be greater than the maximum max_force anticipated so we
use this calculation: Fs=(1+zeta)Fmax in case the free length is unknown

Note: zeta is the overrun safety factor, it’s customary that zeta=0.15 so Fs=1.15Fmax


* **Returns**

    The max_force it takes to get the spring to solid length



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property active_coils()
getter for the `active_coils` attribute


* **Returns**

    The spring active coils



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property buckling()
Checks if the spring will buckle and find the
maximum free length to avoid buckling


* **Returns**

    True if spring is in danger of collapse and False if not,
    and the maximum free length(free_length) to avoid collapsing



* **Return type**

    [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[bool](https://docs.python.org/3/library/functions.html#bool), [float](https://docs.python.org/3/library/functions.html#float)]



#### calc_active_coils()
Calculate active_coils which is the number of active coils (using Castigliano’s theorem)


* **Returns**

    number of active coils



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### calc_deflection(force)
Calculate the spring deflection (change in length) due to a specific max_force


* **Parameters**

    **or Symbol force** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Spring working max_force



* **Returns**

    Spring deflection



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### calc_free_length()
Calculates the free length of the spring


#### calc_spring_index(solid_safety_factor)
Calculate Spring index for a certain safety factor if only wire diameter was given
but the spring diameter was not (from Shigley’s)


* **Parameters**

    **solid_safety_factor** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Spring’s safety factor for solid length



* **Returns**

    Spring’s index number



#### check_design()
Check if the spring index,active_coils,zeta and free_length
are in acceptable range for a good design


* **Returns**

    True if all the checks are good



* **Return type**

    [bool](https://docs.python.org/3/library/functions.html#bool)



#### property end_coils()
Ne - the end coils of the spring


* **Returns**

    Number of the spring end coils



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### property factor_KB()
K_B - Bergstrasser shear stress concentration factor (very close to factor_Kw)

NOT IMPLEMENTED!!!


* **Returns**

    Bergstrasser shear stress concentration factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property factor_Ks()
factor_Ks - Static shear stress concentration factor


* **Returns**

    Static shear stress concentration factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property factor_Kw()
K_W - Wahl shear stress concentration factor


* **Returns**

    Wahl shear stress concentration factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### fatigue_analysis(max_force, min_force, reliability, criterion='modified goodman', verbose=False, metric=True)
Returns safety factors for fatigue and
for first cycle according to Langer


* **Parameters**

    
    * **max_force** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Maximal max_force acting on the spring


    * **min_force** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Minimal max_force acting on the spring


    * **reliability** ([*float*](https://docs.python.org/3/library/functions.html#float)) – in percentage


    * **criterion** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – fatigue criterion


    * **verbose** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – print more details


    * **metric** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Metric or imperial



* **Returns**

    static and dynamic safety factor



* **Return type**

    [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[float](https://docs.python.org/3/library/functions.html#float), [float](https://docs.python.org/3/library/functions.html#float)]



#### property free_length()
getter for the `free_length` attribute


* **Returns**

    free length of the springs



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property max_deflection()
Returns the spring max_deflection, It’s change in length


* **Returns**

    Spring max_deflection



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### property max_shear_stress()
Return’s the shear stress


* **Returns**

    Shear stress



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### min_spring_diameter(safety_factor, wire_diameter, solid=False)
return the minimum spring diameter to avoid static failure
according to the specified safety factor, if the solid flag is True :attr:’Fsolid’
is used instead of `max_force`


* **Parameters**

    
    * **safety_factor** ([*float*](https://docs.python.org/3/library/functions.html#float)) – static safety factor


    * **wire_diameter** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Spring’s wire diameter


    * **solid** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – If true calculate to according to the solid max_force



* **Returns**

    The minimal spring diameter



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### min_wire_diameter(safety_factor, spring_diameter=None, spring_index=None, solid=False)
The minimal wire diameter for a given
safety factor in order to avoid failure,
according to the spring parameters.
if solid is True the calculation uses `Fsolid`
instead of `max_force`

Note: In order for the calculation to succeed the spring

    diameter or the spring index should be known


* **Parameters**

    
    * **safety_factor** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Static safety factor


    * **spring_diameter** ([*float*](https://docs.python.org/3/library/functions.html#float)) – The spring diameter


    * **spring_index** ([*float*](https://docs.python.org/3/library/functions.html#float)) – The spring index


    * **solid** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – If true calculate to according to the solid max_force



* **Returns**

    The minimal wire diameter



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### property shear_yield_strength()
Ssy - yield strength for shear
(shear_yield_stress = % \* ultimate_tensile_strength))


* **Returns**

    yield strength for shear stress



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property solid_length()
Ls - the solid length of the spring
(if the spring is fully compressed so the coils are touching each other)


* **Returns**

    Spring solid length (when all the coils are touching)



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### property spring_constant()
getter for the `spring_constant` attribute


* **Returns**

    The spring constant



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property spring_diameter()
Getter for the spring diameter attribute


* **Returns**

    The spring diameter



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### static_safety_factor(solid=False)
Returns the static safety factor according to the object attributes


* **Returns**

    static factor of safety



* **Type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### property total_coils()
Nt - the total coils of the spring


* **Returns**

    Number of the spring total coils



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### property wire_diameter()
Getter for the wire diameter attribute


* **Returns**

    The spring’s wire diameter



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol


## me_toolbox.springs.helical_torsion_spring module

A module containing the helical torsion spring class


### class me_toolbox.springs.helical_torsion_spring.HelicalTorsionSpring(max_moment, wire_diameter, spring_diameter, leg1, leg2, shear_modulus, elastic_modulus, yield_percent, Ap, m, spring_constant=None, active_coils=None, body_coils=None, shot_peened=False, density=None, working_frequency=None, radius=None, pin_diameter=None)
Bases: `me_toolbox.springs.spring.Spring`

A Helical torsion spring object


#### property active_coils()
getter for the `active_coils` attribute


* **Returns**

    The spring active coils



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property body_coils()
getter for the `body_coils` attribute


* **Returns**

    The spring body coils



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### calc_active_coils()
Calculate Na which is the number of active coils
(using Castigliano’s theorem)


* **Returns**

    number of active coils



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### calc_angular_deflection(moment, total=True)
Calculates the total angular deflection based on the moment given
if the total flag is True than the total angular deflection is calculated,
if False only the deflection of the coil body is calculated

NOTE: the units of the deflection is in [turns]


* **Parameters**

    
    * **of Symbol moment** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Working moment of the spring


    * **total** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – total or partial deflection



* **Returns**

    Total angular deflection



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### calc_body_coils()
Calculate active_coils which is the number of active coils (using Castigliano’s theorem)


* **Returns**

    number of active coils



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### calc_max_stress(moment)
Calculates the normal stress based on the moment given
NOTE: The calculation is for round wire torsion spring


* **Parameters**

    **of Symbol moment** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Working force of the spring



* **Returns**

    normal stress



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### calc_spring_constant()
Calculate spring constant in [N\*mm/turn] or [pound force\*inch/turn]


* **Returns**

    The spring constant



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property clearance()

#### property factor_ki()
Internal stress correction factor

:returns:stress concentration factor
:rtype: float


#### fatigue_analysis(max_moment, min_moment, reliability, criterion='gerber', verbose=False, metric=True)
Returns safety factors for fatigue and
for first cycle according to Langer


* **Parameters**

    
    * **max_moment** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Maximal max_force acting on the spring


    * **min_moment** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Minimal max_force acting on the spring


    * **reliability** ([*float*](https://docs.python.org/3/library/functions.html#float)) – in percentage


    * **criterion** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – fatigue criterion


    * **verbose** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – print more details


    * **metric** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Metric or imperial



* **Returns**

    static and dynamic safety factor



* **Return type**

    [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[float](https://docs.python.org/3/library/functions.html#float), [float](https://docs.python.org/3/library/functions.html#float)]



#### property helix_diameter()
The helix diameter


#### property max_angular_deflection()
The angular deflection due to the max moment
of *only* the coil body in [turns]


* **Returns**

    Max angular deflection



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### property max_angular_deflection_deg()
convert max angular deflection from [turns] to [degrees]


#### property max_stress()
The normal stress due to bending and axial loads


* **Returns**

    Normal stress



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### property max_total_angular_deflection()
The total angular deflection due to the max moment
this deflection is comprise out of the angular deflection
of the coil body and from the end deflection of a cantilever
for *each* leg.


* **Returns**

    Max angular deflection



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### property max_total_angular_deflection_deg()
convert max angular deflection from [turns] to [degrees]


#### min_spring_diameter(safety_factor, wire_diameter)
return the minimum spring diameter to avoid static failure
according to the specified safety factor


* **Parameters**

    
    * **safety_factor** ([*float*](https://docs.python.org/3/library/functions.html#float)) – static safety factor


    * **wire_diameter** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Spring’s wire diameter



* **Returns**

    The minimal spring diameter



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### min_wire_diameter(safety_factor, spring_diameter=None, spring_index=None)
The minimal wire diameter for a given safety factor
in order to avoid failure, according to the spring parameters

Note: In order for the calculation to succeed the

    spring diameter or the spring index should be known


* **Parameters**

    
    * **safety_factor** ([*float*](https://docs.python.org/3/library/functions.html#float)) – static safety factor


    * **spring_diameter** ([*float*](https://docs.python.org/3/library/functions.html#float)) – The spring diameter


    * **spring_index** ([*float*](https://docs.python.org/3/library/functions.html#float)) – The spring index



* **Returns**

    The minimal wire diameter



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property spring_const_deg()
convert the spring constant from
[N\*mm/turn] or [pound force\*inch/turn]
to [N\*mm/deg] or [pound force\*inch/deg]


#### property spring_constant()
getter for the `spring_constant` attribute


* **Returns**

    The spring constant



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property spring_diameter()
Getter for the spring diameter attribute


* **Returns**

    The spring diameter



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### property static_safety_factor()
Returns the static safety factor


* **Returns**

    Spring’s safety factor



* **Type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### property wire_diameter()
Getter for the wire diameter attribute


* **Returns**

    The spring’s wire diameter



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### property yield_strength()
Sy - yield strength
(shear_yield_stress = % \* ultimate_tensile_strength))

## me_toolbox.springs.spring module


### class me_toolbox.springs.spring.Spring(max_force, wire_diameter, spring_diameter, shear_modulus, elastic_modulus, shot_peened, density, working_frequency, Ap, m)
Bases: [`object`](https://docs.python.org/3/library/functions.html#object)


#### calc_max_shear_stress(force, k_factor)
Calculates the max shear stress based on the max_force applied


* **Parameters**

    
    * **of Symbol force** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Working max_force of the spring


    * **k_factor** ([*float*](https://docs.python.org/3/library/functions.html#float)) – the appropriate k factor for the calculation



* **Returns**

    Shear stress



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### calc_spring_constant()
Calculate spring constant (using Castigliano’s theorem)


* **Returns**

    The spring constant



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### get_info()
print all of the spring properties


#### static material_prop(material, diameter, metric=True)
Reads table A_and_m.csv from file and returns the
material properties Ap and m for Sut estimation


* **Parameters**

    
    * **material** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – The spring’s material


    * **diameter** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Wire diameter


    * **metric** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Metric or imperial



* **Returns**

    Ap and m for Sut estimation



* **Return type**

    ([float](https://docs.python.org/3/library/functions.html#float), [float](https://docs.python.org/3/library/functions.html#float))



#### natural_frequency(density)
Figures out what is the natural frequency of the spring


* **Parameters**

    **density** ([*float*](https://docs.python.org/3/library/functions.html#float)) – spring material density



* **Returns**

    Natural frequency



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### shear_endurance_limit(reliability, metric=True)
Sse - Shear endurance limit according to Zimmerli


* **Parameters**

    
    * **reliability** ([*float*](https://docs.python.org/3/library/functions.html#float)) – reliability in percentage


    * **metric** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – metric or imperial



* **Returns**

    Sse - Shear endurance limit



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property shear_ultimate_strength()
Ssu - ultimate tensile strength for shear


#### property spring_diameter()
Getter for the spring diameter attribute


* **Returns**

    The spring diameter



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### property spring_index()
C - spring index

Note: C should be in range of [4,12], lower C causes surface cracks,

    higher C causes the spring to tangle and require separate packing


* **Returns**

    The spring index



* **Type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### property ultimate_tensile_strength()
Sut - ultimate tensile strength


#### weight(density)
Return’s the spring *active coils* weight according to the specified density


* **Parameters**

    **density** ([*float*](https://docs.python.org/3/library/functions.html#float)) – The material density



* **Returns**

    Spring weight



* **Type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol



#### property wire_diameter()
Getter for the wire diameter attribute


* **Returns**

    The spring’s wire diameter



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or Symbol


## Module contents
