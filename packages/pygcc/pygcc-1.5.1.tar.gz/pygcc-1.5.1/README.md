# `pygcc`

<img src="_static/PyGCC_logo_vector.jpg" alt="pygcc Logo" width="40%" align="right">

A tool for thermodynamic calculations and geochemical database generation

[![pyGeochemCalc Documentation](https://readthedocs.org/projects/pygcc/badge/?version=latest)](https://pygcc.readthedocs.io/en/latest/?badge=latest)
[![License: GNU General Public License v3.0](https://img.shields.io/badge/License-GNU%20General%20Public%20License%20v3.0-blue.svg?style=flat)](https://bitbucket.org/Tutolo-RTG/pygcc/src/master/LICENSE)


pyGeochemCalc (pygcc) is a python-based program for thermodynamic calculations and producing the 
Geochemist's Workbench (GWB), EQ3/6, TOUGHREACT, and PFLOTRAN thermodynamic database from 
ambient to deep Earth temperature and pressure conditions


pygcc is developed for use in the geochemical community by providing a consolidated 
set of existing and newly implemented functions for calculating the thermodynamic properties 
of gas, aqueous, and mineral (including solid solutions and variable-formula clays) species, 
as well as reactions amongst these species, over a broad range of temperature and pressure 
conditions, but is also well suited to being modularly introduced into other modeling tools 
as desired. The documentation is continually evolving, and more examples and tutorials will gradually be added (feel free to
request features or examples; see [Contributing](#contributing) below).

## Installation

[![PyPI](https://img.shields.io/pypi/v/pygcc.svg?style=flat)](https://pypi.org/project/pygcc/)
[![Compatible Python Versions](https://img.shields.io/pypi/pyversions/pygcc.svg?style=flat)](https://pypi.python.org/pypi/pygcc/)
[![pygcc downloads](https://img.shields.io/pypi/dm/pygcc.svg?style=flat)](https://pypistats.org/packages/pygcc)

```bash
$ pip install pygcc
```

## Examples

Check out the documentation for galleries of examples [General Usage](https://pygcc.readthedocs.io/en/latest/Example_1.html), 
[Integration with GWB](https://pygcc.readthedocs.io/en/latest/Example_2.html) and [Integration with EQ3/6](https://pygcc.readthedocs.io/en/latest/Example_3.html). 
If you would prefer to flip through notebooks on Bitbucket, these same examples can be found in the folder [`docs/`](https://bitbucket.org/Tutolo-RTG/pygcc/src/master/docs/).

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. 
By contributing to this project, you agree to abide by its terms. For more information, see the [documentation](https://pygcc.readthedocs.io/), 
particularly the [Contributing page](https://pygcc.readthedocs.io/en/latest/contributing.html) and 
[Code of Conduct](https://pygcc.readthedocs.io/en/latest/conduct.html). 

## License

`pygcc` was created by Adedapo Awolayo and Benjamin Tutolo. It is licensed under the terms of the GNU General Public License v3.0 license.

## Citation

If you use pygcc for your research, citation of the software would be appreciated. It helps to quantify the impact of 
pygcc, and build the pygcc community. For information on citing pygcc, 
[see the relevant docs page](https://pygcc.readthedocs.io/en/latest/pygcc_overview.html#citation-and-contact-information-a-class-anchor-id-section-6-a)

## Credits
`pygcc Logo` was designed by [`Yury Klyukin`](https://www.linkedin.com/in/yury-klyukin-68517ba2/), `pygcc` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
