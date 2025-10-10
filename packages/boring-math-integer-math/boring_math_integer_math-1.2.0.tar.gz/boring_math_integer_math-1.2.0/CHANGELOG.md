# CHANGELOG

PyPI boring-math-integer-math project.

## Semantic Versioning

Strict 3 digit semantic versioning.

- **MAJOR** version incremented for incompatible API changes
- **MINOR** version incremented for backward compatible added functionality
- **PATCH** version incremented for backward compatible bug fixes

See [Semantic Versioning 2.0.0](https://semver.org).

## Releases and other important milestones

### Update - 2025-10-08

Broke out combinatorics library (all two functions)
to its own GitHub repo: boring-math-combinatorics

Eventually boring-math-integer-math will be renamed
to boring-math-number-theory.

Both are part of my Boring Math hobby projects.

### Version 1.0.2 - PyPI release date 2025-08-04

Bad circulararray requirement in pyproject.toml

### Version 1.0.0 - PyPI release date 2025-08-04

After some flaying and several releases I finally got things settled
down with a 0.8.2 release. I updated docstrings to reflect a name
change, integer_math.num_theory -> integer_math.number_theory and
never made the change! Everything worked but the docstring had wrong
info. After making the changes and running pytest tests, I realized
I made an API breaking change. Sorry...

### Version 0.7.1 - PyPI release date 2025-07-14

- Fixed munged CHANGELOG and Documentation links for PyPI

### Version 0.7.0 - PyPI release date 2025-07-14

- First version to use pythonic_fp namespace
- no longer using dtools namespace packages

### Version 0.5.1 - PyPI release date 2025-04-TBD

- Made compatible with latest release dltools
  - dtools.circular-array   3.12.0
  - dtools.fp               1.6.0
  - dtools.queues           0.27.0
  - dtools.tuples           0.27.0

### Version 0.5.0 - PyPI release date 2025-01-17

- First PyPI release as bm.integer-math
- new doc location is
  [here](https://grscheller.github.io/boring-math-docs/)

### Version 0.4.7 - PyPI release date 2024-11-18

- Some minor additions
- consistency changes across all grscheller namespace PyPI repos

### Version 0.4.6 - PyPI release date 2024-10-20

- removed docs from repo
- docs for all grscheller namespace projects maintained
  [here](https://grscheller.github.io/grscheller-pypi-namespace-docs/)

### Version 0.4.4.5 - commit date 2024-09-08

- preparing to add more composite number tests
  - primality tests based on Wilson's theorem
    - becomes too slow when calculation starts using BigInts
  - added number theory symbols functions
    - implemented: `legendre_symbol(a, p)`
    - implemented: `jacobi_symbol(a, n)`

### Version 0.4.4.4 - commit date 2024-09-08

- re-implemented function primes
  - no longer using sieve of Eratosthenes algorithm
  - now using Wilson's theorem and incremental factorial generation

### Version 0.4.4 - PyPI release date 2024-09-01

- removed MathJax expressions
  - not worth the increased maintenance
  - can get almost the same results using `expresions` and unicode

### Version 0.4.3.1 - commit date 2024-08-17

- MathJax expressions used to render non-code mathematical expressions
  - pdoc accepts MathJax expressions with --math option
    - `$ pdoc --math -o . grscheller.boring_math`

### Version 0.4.3 - PyPI release date 2024-08-17

- updated to use grscheller.circular-array 3.4.1
  - this version of CA compares first with identity before trying equality
    - like Python builtins do
- now using pdoc instead of pdoc3 for documentation
- replaced github markdown with std markdown

### Version 0.4.0 - PyPI release date 2024-07-12

- updated to use grscheller.circular-array 3.3.1
- minimum Python version now 3.12
- target Python version now 3.13

### Version 0.3.1 - PyPI release date 2024-03-09

- reflecting grscheller.circular-array PyPI dependency change
  - dependencies = ["grscheller.circular-array >= 0.2.0, < 2.1"]

### Version 0.3.0 - PyPI release date 2024-03-02

- decided it a good time for a PyPI release
  - want to use some of the newer features in new endeavors
  - vastly improved documentation over last PyPI release

### Version 0.2.2.0 - commit date 2024-02-28

- renamed integer_math.mkCoprime to integer_math.coprime
  - did it now before PyPI v0.3.0
- realized pdoc uses Markdown as its preferred markup language
  - some differences
    - incorporates some GitHub Markdown additions
    - will format google-style & numpydoc style comments
    - lists are one dimensional, not hierarchical

### Version 0.2.0.0 - commit date 2024-02-21

- All implementations going forward for integer_math module will use
  just integer based algorithms. I can't really compete with C based
  code from the Python standard library. The algorithms will then be
  of use if ported to a platform without floating point arithmetic.
- added two new functions to the integer_math module
  - iSqrt() finds the int square root of an int
    - does same thing as math.isqrt()
  - isSqr() return true if integer argument is a perfect square

### Version 0.1.3 - PyPI release date 2024-02-20

- Forgot to update pyproject.toml dependencies
  - dependencies = ["grscheller.circular-array >= 0.1.1, < 1.1"]

### Version 0.1.2 - PyPI release date 2024-01-30

- now needs CircularArray v0.1.2
  - integer_math comb uses new foldL method of CircularArray
  - CircularArray was split out of grscheller.datastructures
- test suite written

### Version 0.1.1 - PyPI release date 2024-01-20

- fixed some negative value edge cases
  - lcm(0,0) now gives 0 instead of a divide by zero exception
    - some authors leave lcm(0, 0) as undefined
    - lcm(0, 0) = 0 does make sense
      - since `a * 0 = 0` for all `a >= 0`
      - 0 is the smallest non-negative integer a such that `a * 0 = 0`
      - most math theorems remain true for this case
- README.md improvements

### Version 0.1.0 - PyPI release date 2024-01-17

- initial PyPI grscheller.boring-math release
- updated pyproject.toml to align with grscheller.datastructures

### Version 0.0.9 - commit date 2024-01-14

- changed project's name from boring_math to boring-math
- both GitHub repo and future PyPI repo
- more in alignment with what I see on PyPI
- project is grscheller.boring-math
- package is still grscheller.boring_math

### Version 0.0.8 - commit date 2024-01-14

- working on pyproject.toml infrastructure for PyPI releases
- will use Flit as the packaging/publishing tool
- replaced bin/ scripts with `boring_math.integer_math_cli` entry-points

### Version 0.0.4 - commit date 2024-01-10

- first coding changes in years!
- gh-pages configured

### Version 0.0.0.3 - commit date 2023-12-06

- added pyproject.toml

### Version 0.0.0.2 - commit date 2023-12-06

- got package working again
  - did not understand iterators that well when I first wrote this package
- replaced my `take` with `itertools.islice`
- generated docs from docstrings with pdoc3

### Version 0.0.0.1 - commit date 2023-12-06

- fixed Markdown issues with first commit
- Added .gitignore file to anticipate pytest & __pycache__ directories

### Version 0.0.0.0 - commit date 2023-12-06

- first commit of source code with with the old pipfile build
  infrastructure removed.
