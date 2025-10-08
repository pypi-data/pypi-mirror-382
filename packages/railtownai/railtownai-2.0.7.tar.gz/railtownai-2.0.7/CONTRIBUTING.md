# Setup for development

## Setup steps

1. Setup your python venv in this repository: `python -m venv .venv`
1. Activate your venv: `.venv\Scripts\activate`
1. Ensure you have [flit installed](https://flit.pypa.io/en/stable/)
1. `flit install --python .venv/Scripts/python.exe`
1. `flit build`

## Running Tests

- Install all dependencies with `pip install -e ".[test]"`
- Run the tests: `python run_tests.py all`
  - Run only the unit tests: `python run_tests.py unit`
  - Run only the integration tests: `python run-tests.py integration`

## Publishing to PyPi Test Index

_Note: We will be using github actions to automatically release to PyPi in the future._

1. Ensure you bumped the `__version__` (semver) by using `python scripts/version_bump.py v2.0.5` (replace with your own version)
1. [Setup your .pypirc](https://flit.pypa.io/en/stable/upload.html)
1. `flit publish --repository testpypi`

## Publishing to PyPi Production Index

1. Same as above but ensure you've been added to the Railtown AI organization on PyPi
1. `flit publish`
1. We will make this a smoother process later...
