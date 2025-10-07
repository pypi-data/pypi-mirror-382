# Reference data fixtures

The `.txt` files in this directory contain reference outputs from the original
gsDesign2 R implementation. They are used to validate the Python port of the
`gridpts`, `h1`, and `hupdate` routines.

To regenerate the fixtures, run the helper script below (requires the
gsDesign2 R package to be installed):

```sh
Rscript tests/fixtures/generate_reference_data.R
```

The script recomputes each dataset via the package's internal functions and
writes the results in plain text so the pytest suite can consume them with
`numpy.loadtxt`.
