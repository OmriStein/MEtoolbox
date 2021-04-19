# me_toolbox.tools package

## Submodules

## me_toolbox.tools.helpers module

module containing misc functions


### me_toolbox.tools.helpers.inch_to_millimetre(val)
convert inches in to millimeters


* **Parameters**

    **or list val** ([*float*](https://docs.python.org/3/library/functions.html#float)) – value to convert



* **Returns**

    converted value



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)



### me_toolbox.tools.helpers.millimetre_to_inch(val)
convert millimetres to inches


* **Parameters**

    **or list val** ([*float*](https://docs.python.org/3/library/functions.html#float)) – value to convert



* **Returns**

    converted value



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)



### me_toolbox.tools.helpers.newtons_to_pound_force(val)
convert newtons to pound max_force


* **Parameters**

    **or list val** ([*float*](https://docs.python.org/3/library/functions.html#float)) – value to convert



* **Returns**

    converted value



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)



### me_toolbox.tools.helpers.parse_input(obj, fields, kwargs)
adds attributes specified in kwargs to obj only if they are specified in fields
fields contain a dictionary of the anticipated attributes and their default value
if one exists, if not use the ‘’ as a place holder


* **Parameters**

    
    * **obj** – An object to which add the attributes


    * **fields** ([*dict*](https://docs.python.org/3/library/stdtypes.html#dict)) – A dictionary containing the desired attributes with default values


    * **kwargs** ([*dict*](https://docs.python.org/3/library/stdtypes.html#dict)) – a dictionary containing the keywords to check


```
from tools import parse_input
from tools import print_atributes
class P:
    def __init__(self,**kwargs):
        fields = {'name':'', 'age':'30', 'fav_color':'', 'hobby':'sky'}
        parse_input(self, fields, kwargs)

p=P(name='Omri', fav_color='blue')
print_atributes(p)
```


### me_toolbox.tools.helpers.percent_to_decimal(var)
if input in percent (>=1) convert to decimal


### me_toolbox.tools.helpers.pound_force_to_newtons(val)
convert pound max_force to newtons


* **Parameters**

    **or list val** ([*float*](https://docs.python.org/3/library/functions.html#float)) – value to convert



* **Returns**

    converted value



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float) or [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)



### me_toolbox.tools.helpers.print_atributes(obj)
prints all of the attributes of an object
excluding the dunder attributes and attributes
with a single leading underscore


* **Parameters**

    **obj** – any object


## me_toolbox.tools.table_interpolation module

module containing the table interpolation function


### exception me_toolbox.tools.table_interpolation.NotInRangeError(var, num, range_)
Bases: [`ValueError`](https://docs.python.org/3/library/exceptions.html#ValueError)


### me_toolbox.tools.table_interpolation.table_interpolation(x_row, x_col, data)
Get table in a numpy array form and two coordinates and
Interpolate the value in the table corresponding to those coordinates


* **Parameters**

    
    * **x_row** ([*float*](https://docs.python.org/3/library/functions.html#float)) – the x row from which to retrieve the value


    * **x_col** ([*float*](https://docs.python.org/3/library/functions.html#float)) – the x col from which to retrieve the value


    * **data** (*np.ndarray*) – the table as numpy array



* **Return type**

    [float](https://docs.python.org/3/library/functions.html#float)


## Module contents
