# OptCalc

OptCalc is a fast C-based Black–Scholes option calculator with Python bindings.

## Example
```python
import optcalc

optcalc.set_params(100, 105, 30, 0.3, 0.01)
optcalc.genOptionSer()
print(optcalc.getCallArr())
