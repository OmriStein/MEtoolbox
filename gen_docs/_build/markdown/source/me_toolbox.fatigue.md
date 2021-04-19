# me_toolbox.fatigue package

## Submodules

## me_toolbox.fatigue.endurance_limit module

a module containing the EnduranceLimit class


### class me_toolbox.fatigue.endurance_limit.EnduranceLimit(Sut, surface_finish, rotating, max_normal_stress, max_bending_stress, stress_type, temp, reliability, material=None, unmodified_endurance=None, A95=None, diameter=None, height=None, width=None)
Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

calculates Marin modification factors and return modified endurance limit


#### property Ka()
Surface condition modification factor


* **Returns**

    Ka - surface finish factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property Kb()
Size modification factor


* **Returns**

    Kb - size factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property Kc()
Load modification factor

:returns Kc - stress type factor
:rtype: float


#### property Kd()
Temperature modification factor


* **Returns**

    factor_Ks - temperature factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property Ke()
Reliability factor


* **Returns**

    Ke - reliability factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property Kf()
Miscellaneous effects factor


#### calc_A95(A95)

#### get_factors()
print Marine factors


#### property modified()
Returns the endurance limit modified by the Marin factors


* **Returns**

    Modified endurance limit



* **Type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property unmodified()
Return the unmodified endurance limit based on the material and ultimate_tensile_strength


* **Returns**

    Unmodified endurance limit



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)


## me_toolbox.fatigue.failure_criteria module

a module containing the FatigueCriteria class
containing the Failure criteria as described in
Shigley’s Mechanical Engineering design


### class me_toolbox.fatigue.failure_criteria.FailureCriteria()
Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Bundling the fatigue criteria together


#### static asme_elliptic(yield_strength, endurance_limit, alt_eq_stress, mean_eq_stress)
Safety factor according to ASME Failure criterion


* **Returns**

    Safety factor



* **Return type**

    any



* **Raises**

    [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – if ultimate_tensile_strength is not in the fatigue call



#### static gerber(ultimate_strength, endurance_limit, alt_eq_stress, mean_eq_stress)
Safety factor according to Gerber failure criterion
(the most lenient criterion)


* **Returns**

    Safety factor



* **Return type**

    any



* **Raises**

    [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – if ultimate_tensile_strength is not in the fatigue call



#### static get_safety_factor(yield_strength, ultimate_strength, endurance_limit, alt_eq_stress, mean_eq_stress, criterion, verbose=False)
Returns dynamic and static safety factors
according to the quadrant in the alternating-mean
stress plain where the stresses are in

Note: Should always be used instead of accessing the
individual safety factors properties directly


* **Parameters**

    
    * **criterion** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – The criterion to use


    * **yield_strength** ([*float*](https://docs.python.org/3/library/functions.html#float)) – The yield strength (Sy or Ssy)


    * **ultimate_strength** ([*float*](https://docs.python.org/3/library/functions.html#float)) – The yield strength (Sut or Ssu)


    * **endurance_limit** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Modified endurance limit (Se)


    * **alt_eq_stress** ([*float*](https://docs.python.org/3/library/functions.html#float)) – alternating stresses


    * **mean_eq_stress** ([*float*](https://docs.python.org/3/library/functions.html#float)) – mean stresses


    * **verbose** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Print the result



* **Returns**

    dynamic and static safety factors



* **Return type**

    [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[float](https://docs.python.org/3/library/functions.html#float), [float](https://docs.python.org/3/library/functions.html#float)]



#### static langer_static_yield(yield_strength, alt_eq_stress, mean_eq_stress)
Static safety factor according to Langer Failure criterion
it’s customary to use Langer, as an assessment to yielding in the first cycle


* **Returns**

    Safety factor



* **Return type**

    any



* **Raises**

    [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – if Sy is not in the fatigue call



#### static modified_goodman(ultimate_strength, endurance_limit, alt_eq_stress, mean_eq_stress)
Safety factor according to modified Goodman failure criterion
(a very common criterion)


* **Returns**

    Safety factor



* **Return type**

    any



* **Raises**

    [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – if ultimate_tensile_strength is not in the fatigue call



#### static soderberg(yield_strength, endurance_limit, alt_eq_stress, mean_eq_stress)
Safety factor according to Soderberg failure criterion
(the safest criterion)


* **Returns**

    Safety factor



* **Return type**

    any



* **Raises**

    [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – if Sy is not in the fatigue call


## me_toolbox.fatigue.fatigue_analysis module

module containing the FatigueAnalysis class and
calc_kf for calculating dynamic stress concentration factor


### class me_toolbox.fatigue.fatigue_analysis.FatigueAnalysis(endurance_limit, ductile, Sy=None, Kf_bending=0, Kf_normal=0, Kf_torsion=0, alt_bending_stress=0, alt_normal_stress=0, alt_torsion_stress=0, mean_bending_stress=0, mean_normal_stress=0, mean_torsion_stress=0)
Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Perform fatigue analysis


#### property ASME_elliptic()
Safety factor according to ASME Failure criterion


* **Returns**

    Safety factor



* **Return type**

    any



* **Raises**

    [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – if ultimate_tensile_strength is not in the fatigue call



#### property Sm_stress()
Getter for the Sm_stress property


* **Returns**

    Sm - stress at 1e3 cycles



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### static calc_Sm(Sut)
Calculate Sm_stress which is the stress at 1e3 cycles, the boundary
dividing Low cycle fatigue and high cycle fatigue


* **Parameters**

    **Sut** – Ultimate tensile strength



* **Returns**

    Sm_stress stress



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### calc_alt_eq_stress()
Returns the alternating equivalent stress according to the load type indicated by Kc


* **Returns**

    Alternating equivalent stress



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### calc_mean_eq_stress()
Returns the mean equivalent stress according to the load type indicated by Kc


* **Returns**

    Mean equivalent stress



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property gerber()
Safety factor according to Gerber failure criterion
(the most lenient criterion)


* **Returns**

    Safety factor



* **Return type**

    any



* **Raises**

    [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – if ultimate_tensile_strength is not in the fatigue call



#### get_info()
print object attributes


#### get_safety_factor(criterion, verbose=False)
Returns dynamic and static safety factors
according to the quadrant in the alternating-mean
stress plain where the stresses are in

Note: Should always be used instead of accessing the
individual safety factors properties directly


* **Parameters**

    
    * **criterion** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – The criterion to use


    * **verbose** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Print the result



* **Returns**

    dynamic and static safety factors



* **Return type**

    [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[float](https://docs.python.org/3/library/functions.html#float), [float](https://docs.python.org/3/library/functions.html#float)]



#### property langer_static_yield()
Static safety factor according to Langer Failure criterion
it’s customary to use Langer, as an assessment to yielding in the first cycle


* **Returns**

    Safety factor



* **Return type**

    any



* **Raises**

    [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – if Sy is not in the fatigue call



#### miner_rule(stress_groups, Sut, Se, Sy=None, z=- 3, verbose=False, alt_mean=False, freq=False)
Calculates total number of cycles for multiple periodic loads,
the stress_groups format is as follows:
[number_of_repetitions, maximum_stress, minimum_stress]

Note: number_of_repetitions = frequency [Hz] \* time

Note: if the material don’t have fatigue limit use the fatigue strength at Se=Sf(N=1e8)


* **Parameters**

    
    * **stress_groups** ([*list*](https://docs.python.org/3/library/stdtypes.html#list)) – a list containing the pick stresses and number of repetition


    * **Sut** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Ultimate tensile strength [MPa]


    * **Sy** ([*float*](https://docs.python.org/3/library/functions.html#float)) – yield strength [MPa], if None only HCF is checked


    * **Se** ([*float*](https://docs.python.org/3/library/functions.html#float)) – endurance limit [MPa]


    * **z** ([*float*](https://docs.python.org/3/library/functions.html#float)) – -3 for steel where N=1e6, -5 for a metal where N=1e8, -5.69 for a metal
    where N=5e8


    * **verbose** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – printing the groups
    [number_of_repetitions,maximum_stress, minimum_stress, reversible_stress, Number of
    cycles]


    * **freq** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – if the input is frequency instead of number of repetition


    * **alt_mean** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – if True the stress_group structure contains
    alternating and mean stresses: [number_of_repetitions, alternating_stress, mean_stress]
    instead of the max and min stresses:
    [number_of_repetitions, maximum_stress, minimum_stress]



* **Returns**

    Total number of cycles



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property modified_goodman()
Safety factor according to modified Goodman failure criterion
(a very common criterion)


* **Returns**

    Safety factor



* **Return type**

    any



* **Raises**

    [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – if ultimate_tensile_strength is not in the fatigue call



#### num_of_cycle(z=- 3)
calculate number of cycles until failure

Note: zeta = log(N1) - log(N2), N1 - number of cycles at Sm_stress,

    N2 - Number of cycles at Se for steel N1=1e3 and N2 = 1e6


* **Parameters**

    **z** ([*float*](https://docs.python.org/3/library/functions.html#float)) – -3 for steel where N=1e6, -5 for a metal where N=1e8,
    -5.69 for a metal where N=5e8



* **Returns**

    The Number of cycles and the fatigue stress at failure



* **Return type**

    [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[float](https://docs.python.org/3/library/functions.html#float), [float](https://docs.python.org/3/library/functions.html#float)]



#### property shear_ultimate_strength()
Returns shear_ultimate_strength which is the
ultimate_tensile_strength correction for shear stress


* **Returns**

    Sst - ultimate shear tensile strength



* **Type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property shear_yield_stress()
Returns shear_yield_strength which is the Sy correction for shear stress


* **Returns**

    shear_yield_strength - yield stress for shear



* **Type**

    [float](https://docs.python.org/3/library/functions.html#float)



#### property soderberg()
Safety factor according to Soderberg failure criterion
(the safest criterion)


* **Returns**

    Safety factor



* **Return type**

    any



* **Raises**

    [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – if Sy is not in the fatigue call



### me_toolbox.fatigue.fatigue_analysis.calc_kf(q, Kt)
Kf - dynamic stress concentration factor


* **Parameters**

    
    * **Kt** ([*float*](https://docs.python.org/3/library/functions.html#float)) – stress concentration theoretical factor


    * **q** ([*float*](https://docs.python.org/3/library/functions.html#float)) – notch Sensitivity



* **Returns**

    dynamic stress concentration factor



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)


## me_toolbox.fatigue.stress module

A module containing stress calculation functions


### me_toolbox.fatigue.stress.bending_stress(My, Iy, z, Mz=None, Iz=None, y=None)
Bending stress in a principle system


* **Parameters**

    
    * **My** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Moment in the y direction


    * **Mz** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Moment in the y direction


    * **Iy** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Area moment of inertia for the y direction


    * **Iz** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Area moment of inertia for the zeta direction


    * **z** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Coordinate


    * **y** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Coordinate



* **Returns**

    Bending Stress in a cross section



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



### me_toolbox.fatigue.stress.max_shear_stress(V, A, shape)
Returns The maximum shear stress for known shapes


* **Parameters**

    
    * **V** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Shear Stress


    * **A** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Cross section area


    * **shape** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Cross section shape



* **Returns**

    Maximum shear Stress



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



### me_toolbox.fatigue.stress.shear_bending_stress(V, Q, I, b)
Shear stresses due to bending


* **Parameters**

    
    * **V** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Shear max_force in y direction


    * **Q** ([*float*](https://docs.python.org/3/library/functions.html#float)) – first moment of in cross section in y direction


    * **I** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Area moment of inertia around the y axis


    * **b** ([*float*](https://docs.python.org/3/library/functions.html#float)) – thickness



* **Returns**

    Shear stress resulting from bending



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



### me_toolbox.fatigue.stress.torsion_stress(T, r, J)
Torsion stresses


* **Parameters**

    
    * **T** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Cross section torque


    * **r** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Stress radius coordinate


    * **J** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Cross section polar moment of inertia



* **Returns**

    Torsion Stress at r



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)



### me_toolbox.fatigue.stress.uniform_stress(F, A)
Returns stress assuming uniform distribution in cross section


* **Parameters**

    
    * **F** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Force


    * **A** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Cross section area


:returns Stress
:rtype: float

## Module contents
