<!--
SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
SPDX-License-Identifier: BSD-2-Clause
-->

# uvoxen - generate test configuration files and run tests

\[[Home][ringlet-home] | [GitLab][gitlab] | [PyPI][pypi] | [ReadTheDocs][readthedocs]\]

## Overview

The `uvoxen` tool allows test environments to be defined in
the `pyproject.toml` file with a syntax relatively similar to
the one used for Tox configuration.
It can then:

- run tests defined in these environments using the `uv` tool
- output Tox configuration and run Tox instead
- export the dependency groups into text files

See the [Getting started][ringlet-getting-started] section for an introduction.

The `uvoxen` tool expects test dependencies to be defined as
[PEP 735 dependency groups][pep-735] in the `pyproject.toml` file.

## Examples

These are some of the ways to use `uvoxen`; see
the [Getting started][ringlet-getting-started] and
the [Configuration][ringlet-config] sections for more information.

### Run tests using `uv`

The `uvoxen uv run` command runs one or more test environments in succession,
recreating the `.venv` virtual environment in between.
The commands defined in the environments are run using the `uv` tool.

``` sh
uvoxen uv run
```

If the `--python` (`-p`) command-line option is specified before the `uv`
subcommand, `uvoxen` will use that Python version to run the tests:

``` sh
uvoxen -p 3.10 uv run -e mypy,unit-tests
```

If the special value `supported` is passed as a Python version, `uvoxen` will
run all the selected environments for all the Python versions that are
listed as supported in the `project.classifiers` section of
the `pyproject.toml` file:

``` sh
uvoxen -p supported uv run
```

### Generate a Tox configuration file

The `uvoxen tox generate` command will export the environment definitions into
a `tox.ini` file so that Tox may be used later (or separately):

``` sh
uvoxen tox generate
```

If the `--check` command-line option is specified, `uvoxen` will not modify
the `tox.ini` file, but it will exit with a non-zero code if any changes
need to be made:

``` sh
uvoxen tox generate --check
```

### Generate requirements files from the dependency groups

The `uvoxen req generate` command will export the list of dependencies
defined in the specified dependency group into a text file suitable for
use with e.g. the ReadTheDocs `mkdocs` runner:

``` sh
uvoxen req generate -g docs
```

If the `--output` (`-o`) option is not specified, the generated file will
be named `requirements/<group>.txt`, e.g. `requirements/docs.txt`.

If the `--check` command-line option is specified, `uvoxen` will not modify
the `requirements/docs.txt` file, but it will exit with a non-zero code if
any changes need to be made:

``` sh
uvoxen req generate --check -g docs
```

## Contact

The `uvoxen` tool was written by [Peter Pentchev][roam].
It is developed in [a GitLab repository][gitlab].
This documentation is hosted at [Ringlet][ringlet-home] with a copy at [ReadTheDocs][readthedocs].

[roam]: mailto:roam@ringlet.net "Peter Pentchev"
[gitlab]: https://gitlab.com/ppentchev/uvoxen "The uvoxen GitLab repository"
[pep-735]: https://peps.python.org/pep-0735/ "PEP 735 – Dependency Groups in pyproject.toml"
[pypi]: https://pypi.org/project/uvoxen/ "The uvoxen Python Package Index page"
[readthedocs]: https://uvoxen.readthedocs.io/ "The uvoxen ReadTheDocs page"
[ringlet-config]: https://devel.ringlet.net/devel/uvoxen/config/ "The Configuration documentation at Ringlet"
[ringlet-getting-started]: https://devel.ringlet.net/devel/uvoxen/getting-started/ "The Getting Started documentation at Ringlet"
[ringlet-home]: https://devel.ringlet.net/devel/uvoxen/ "The Ringlet uvoxen homepage"
