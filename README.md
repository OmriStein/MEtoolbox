# me_toolbox

me_toolbox is a Python library meant to simplify the tedious
calculations of mechanical design and help speed up the design process.<br>
This library contains fatigue, gears, springs and fasteners analysis tools.<br>
This library is for my own personal use, use it at your own discretion.


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install me-toolbox.
```bash
 pip install me_toolbox 
```
<!--
--->

## Usage

```python
import me_toolbox.springs as springs 
import me_toolbox.gears as gears
import me_toolbox.fatigue as fatigue
import me_toolbox.fatigue as fatigue
import me_toolbox.fasteners as fasteners

spring = springs.HelicalSpring(...)

gear = gears.SpurGear(...)
transmission = gears.Transmission(...)

se = fatigue.EnduranceLimit(...)
fatigue_analysis = fatigue.FatigueAnalysis(se, ...)

bolt = fasteners.Bolt(...)
fastener = fasteners.ThreadedFastener(bolt, ...)
pattern = fasteners.BoltPattern(fasteners, ...)
```

For more detailed examples:
https://github.com/OmriStein/me-toolbox/tree/master/examples

## License
[MIT](https://choosealicense.com/licenses/mit/)
