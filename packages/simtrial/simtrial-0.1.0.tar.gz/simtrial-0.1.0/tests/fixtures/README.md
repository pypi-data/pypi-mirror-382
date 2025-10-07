# Reference data fixtures

The `.txt` files in this directory contain reference outputs from the original
simtrial R implementation. They are used to validate the Python port of the
piecewise exponential generator.

## Regenerating fixtures

The fixture generator script reproduces the draws using the R implementation
for specific seeds and parameter sets, and writes both the uniform random
numbers and the resulting event times to plain-text files without headers.

```sh
Rscript tests/fixtures/generate_piecewise_exponential.R
```

The pytest suite consumes these numbers with `numpy.loadtxt` to cross-check the
Python implementation against the reference algorithm.
