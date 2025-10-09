# LISA Instrument

LISA Instrument simulates the measurement chain of LISA, including the
generation of instrumental noises, the simulation of optical signals (noises and
signals) and their interferometric detection, and the on board processing. It
delivers telemetry data.

LISA Instrument can be interfaced with other simulation tools, such as LISA
Orbits (to define constellation orbits), LISA GW Response (to inject
gravitational-wave signals), LISA Glitch (to inject instrumental artifacts),
etc.

## Physical models

A description of the underlying physical models can be found in [Unified model
for the LISA measurements and instrument simulations, Jean-Baptiste Bayle and
Olaf Hartwig, Phys. Rev. D 107, 083019
(2023)](https://journals.aps.org/prd/abstract/10.1103/PhysRevD.107.083019).

## Contributing

### Report an issue

We use the issue-tracking management system associated with the project provided
by Gitlab. If you want to report a bug or request a feature, open an issue at
<https://gitlab.in2p3.fr/lisa-simulation/instrument/-/issues>. You may also
thumb-up or comment on existing issues.

### Development environment

We strongly recommend to use [Poetry](https://python-poetry.org) to manage your
development environment. To setup the development environment, use the following
commands:

```shell
git clone git@gitlab.in2p3.fr:lisa-simulation/instrument.git
cd instrument
poetry install
poetry shell
pre-commit install
```

### Building documentation

We maintain a user manual created using sphinx. It is build in the continuous
integration. To create it locally, execute the commands below. The start page
will be created in `docs/_build/html/index.html`.

```shell
poetry install --with doc
poetry run make -C docs html
```


### Workflow

The project's development workflow is based on the issue-tracking system
provided by Gitlab, as well as peer-reviewed merge requests. This ensures
high-quality standards.

Issues are solved by creating branches and opening merge requests. Only the
assignee of the related issue and merge request can push commits on the branch.
Once all the changes have been pushed, the "draft" specifier on the merge
request is removed, and the merge request is assigned to a reviewer. He can push
new changes to the branch, or request changes to the original author by
re-assigning the merge request to them. When the merge request is accepted, the
branch is merged onto master, deleted, and the associated issue is closed.

### Linting and testing

We enforce [PEP 8 (Style Guide for Python
Code)](https://www.python.org/dev/peps/pep-0008/) with Pylint syntax checking.
Further, we use type annotations, checked using mypy.
We implement unit testing using the pytest framework.
Finally, we use Black as a formatter. You can run them locally

```shell
poetry run pylint lisainstrument
poetry run mypy lisainstrument
poetry run pytest
```

These checks are run in the continuous integration system. Corresponding
pre-commit hooks for the linting and formatting are also available in the
repository.


## Authors

* Jean-Baptiste Bayle (<j2b.bayle@gmail.com>)
* Olaf Hartwig (<olaf.hartwig@aei.mpg.de>)
* Wolfgang Kastaun (<wolfgang.kastaun@aei.mpg.de>)
* Martin Staab (<martin.staab@aei.mpg.de>)

## Acknowledgment

We are thankful to J. Waldmann for sharing his implementation of long power-law
noise time series generators, based on [Plaszczynski, S. (2005). Generating long
streams of 1/f^alpha noise](https://doi.org/10.1142/S0219477507003635).
We use a newly created noise generation framework based on the same principles.
For comparison, J. Waldmann's pyplnoise module is still distributed with this
project as a submodule.
You can find the original project at <https://github.com/janwaldmann/pyplnoise>.
