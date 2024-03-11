# large_tokamak solution point

Run the `large-tokamak` regression input file, and produce a converged mfile. Then convert this solution to an input file (`*sol_IN.DAT`). Then, add
```
* Once through only
ioptimz  = -2 * no optimisation
```
to the `*sol_IN.DAT` to convert it to a once-through, non-optimising run. This can then be used in reliability analysis or optimisation under uncertainty studies.