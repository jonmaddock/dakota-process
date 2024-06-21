# Large Tokamak (LT) design points

- `lt_orig_IN.DAT`: The original large tokamak regression test input file from Process, which uses all equality constraints (f-values)
- `lt_IN.DAT`: The same file, but converted to inequality and equality constraints (no f-values), using the `prep_sol_for_uq.ipynb` notebook
- `lt_MFILE.DAT`: The optimised solution of the inequality-constrained large tokamak
- `lt_sol_IN.DAT`: Non-optimising (once through) large tokamak input file, with the `lt_MFILE.DAT` solution as the initial optimisation parameter vector
- `lt_sol_MFILE.DAT`: The output of the non-optimising large tokamak solution input

`lt_sol_IN.DAT` is the solution vector expressed as an input file, and can be used as a template for UQ studies around that design point.

- `lt_max_net_elec_IN.DAT`: inequality problem for maximising net electric power (no f-values).
- `lt_max_net_elec_MFILE.DAT`: solution for the above (found via MC study on CSD3)