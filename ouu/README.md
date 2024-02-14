# Basic RBDO for Process under uncertainty using Dakota

RBDO is performed on the `large-tokamak` problem under uncertainty. Few optimisation parameters and few uncertain parameters are used to simplify this example. This minimises the objective function whilst constraining for the 90% probability of the sum of constraints being <= 0 under uncertainty, i.e. >=90% reliability.

It can be run with:
```
dakota -i ouu.in
```