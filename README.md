# me_toolbox

me_toolbox is a Python library meant to simplify the tedious
calculations of mechanical design and help speed up the design
process. This library contains general fatigue analysis tools
and gears and springs design tools.

<!--
## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install me_toolbox.
```bash
 pip install me_toolbox 
```
--->

## Usage

```python
import me_toolbox.springs as springs 
import me_toolbox.gears as gears
spring_obj = springs.HelicalSpring(...)
gear_obj = gears.SpurGear(...)
trasmission_obj = gears.Transmission(...)
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)