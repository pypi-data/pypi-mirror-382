<!--
SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
SPDX-License-Identifier: BSD-2-Clause
-->

# Getting started with uvoxen

## Overview

This is a description of how to modify the `pyproject.toml` file of
an existing Python library so that the tests may be run using
the `uvoxen` tool.
Since `uvoxen` was written to ease the workflow of its author, some of
the steps may need modification for projects with different workflow
(e.g. not using Tox for testing, a different file layout, etc).

## Add the tool.uvoxen section

The first step in using `uvoxen` is to add a `tool.uvoxen` table to
the `pyproject.toml` file, and specify the version of its file format.
We also add an empty "environments list" variable and an empty
"environment definitions" section:

``` toml
[tool.uvoxen]
mediaType = "vnd.ringlet.devel.uvoxen.config/uvoxen.v0.3+toml"
envlist = [
]

[tool.uvoxen.env]
```

This documentation describes version 0.1 of the configuration file format;
later `uvoxen` versions may support more settings or change some of them in
incompatible ways.

These configuration settings should be enough so that `uvoxen` can be run
in query mode to make sure it can at least parse the `pyproject.toml` file:

``` sh
uvoxen list reqs
uvoxen list envs
uvoxen list pythons
```

The first two commands should output nothing; the third one should list
all of the Python versions declared as supported in
the `project.classifiers` list of the `pyproject.toml` file.

## Add a standalone test environment

Let us start with a test environment that does not require either
the project itself or its dependencies to be installed.
To add a `ruff` test environment that will run [the Ruff linter][ruff],
we need to first declare what packages should be installed.
The `uvoxen` tool relies on `uv` supporting [PEP 735][pep-735]
dependency groups, so let us add one of those:

``` toml
[dependency-groups]
testenv-ruff = [
  "ruff == 0.9.9",
]
```

Note that the `dependency-groups` section is outside of the `tool.uvoxen` one.

At this point, `uvoxen` should see this set of requirements;
the `uvoxen list reqs` command should output a single line, `testenv-ruff`.

Now we are ready to define the test environment itself:

``` toml
[tool.uvoxen.env.ruff]
dependency-groups = [
  "testenv-ruff",
]
commands = [
  "ruff check -- src/divert-and-modify tests/unit",
]
```

Now the `uvoxen list envs` command should output `ruff`.

With these definitions, `uvoxen` should be able to invoke `uv` to
create a virtual environment in the `.venv/` directory, install only
the packages listed in the `testenv-ruff` dependency group (i.e. only Ruff itself),
and then run the specified commands:

``` sh
uvoxen uv run -e ruff
```

Once this works, we can add `ruff` to the list of environments to be
run by default:

``` toml
[tool.uvoxen]
envlist = [
  "ruff",
]
```

And now all the defined environments can be run in the order specified in
that list:

``` sh
uvoxen uv run
```

## Use variables for parameters common to several test environments

If we now want to add a test environment that runs another linter, we may need to
specify the same list of directories - `src/divert-and-modify` and `tests/unit` -
in the commands to be run there.
The `uvoxen` tool supports variables of two types: strings and lists of strings.
They are defined in the `tool.uvoxen.defs` section:

``` toml
[tool.uvoxen.defs]
pyfiles = [
  "src/divert-and-modify",
  "tests/unit",
]
```

The variables may then be referenced in the commands using the Tox syntax:

``` toml
commands = [
  "ruff check -- {[defs]pyfiles}",
]
```

This is one of the leaky abstractions of `uvoxen` - since it started as
a way to run the same tests that can be run in a `tox.ini` file, it uses
syntax and concepts borrowed from Tox in several places.
It tries to expand the values of the variables in the same way Tox does;
it is possible that sometimes the results may vary, e.g. regarding
shell quoting of values containing special characters.
Also, `uvoxen` does not support the full Tox syntax or all the predefined
variables yet; see the [Configuration](config.md) section for details.

Now we are ready to add a second test environment that also uses Ruff to
check the formatting of the Python source files:

``` toml
[tool.uvoxen]
envlist = [
  "format",
  "ruff",
]

[tool.uvoxen.env.format]
dependency-groups = [
  "testenv-ruff",
]
commands = [
  "ruff check --config ruff-base.toml --select=D,I --diff -- {[defs]pyfiles}",
  "ruff format --config ruff-base.toml --check -- {[defs]pyfiles}",
]
```

Now `uvoxen uv run` should run the commands for both environments, one after
the other, recreating the `.venv` virtual environment between them.
With the peformance of the `uv` tool with cached module metadata,
recreating the environments should not be too slow.

## Run the tests using different Python versions

The `uvoxen` tool allows the Python version to be specified when running
tests using the `--python` (`-p`) option before the first subcommand is
specified:

``` sh
uvoxen -p 3.10 uv run
```

Also, it parses the `project.classifiers` list in the `pyproject.toml` file,
so it can be instructed to run the test environments with all supported
Python versions in order:

``` sh
uvoxen -p supported uv run
```

## Reuse dependency lists in other dependency groups

In some cases it may be useful to list the same Python libraries in
several different sets of requirements.
The PEP 735 dependency group specification defines the `include-group` syntax:

``` toml
[dependency-groups]
testenv-mypy = [
  {include-group = "testenv-unit-tests"},
  "mypy >= 1.7, < 2",
]
testenv-unit-tests = [
  "pytest >= 7, < 8",
]
```

The full list of requirements for a dependency group may be viewed using
the `req generate` subcommand; more about it later.

``` sh
uvoxen req generate -o - -g testenv-mypy
```

Now the `mypy` test environment may be defined:

``` toml
[tool.uvoxen.env.mypy]
dependency-groups = [
  "testenv-mypy",
]
commands = [
  "mypy -- {[defs]pyfiles}",
]
```

Note that the `uv` tool will always install the dependencies of the project,
even for environments that do not need the project itself installed.
This is the reason why the `mypy` type checker can now see the Python modules
that the project source files import in addition to the source files themselves.
This differs from the way Tox normally works; more on that later.

## Run a test that needs the project itself to be installed

Some test environments, e.g. unit tests, functional tests, continuous
integration tests, etc., will also need the project itself to be built and
installed into the virtual environment before the test can be run.
The `install-project` environment parameter will take care of that:

``` toml
[tool.uvoxen.env.unit-tests]
dependency-groups = [
  "testenv-unit-tests",
]
install-project = true
commands = [
  "pytest {posargs} tests/unit",
]
```

## Pass command-line arguments to the test commands

Another feature `uvoxen` has copied over from Tox is the use of
the `{posargs}` variable in a command string; it is replaced by
the command-line arguments passed to the `uvoxen uv run` subcommand itself.
Thus, with the above definition of the `unit-tests` environment,
`uvoxen` will pass the `-vv` and `-s` parameters to `pytest`:

``` sh
uvoxen uv run -- -vv -s
```

As with Tox, there is currently no way to specify command-line arguments to
be passed to specific environments if more than one of those is run.

## Export dependency groups into requirements files for other tools

Some external tools, e.g. the ReadTheDocs `mkdocs` generator, do not yet
understand dependency groups and expect to read requirements files.
The `req generate` subcommand will generate such a file for the specified
dependency group; if the `--output` (`-o`) option is not specified,
a `requirements/<groupname>.txt` file will be generated:

``` sh
uvoxen req generate -g docs
```

Sometimes it is useful to place some "hardcoded" text at the top or
the bottom of a generated file.
The `req generate` subcommand will honor the `header` and `footer`
parameters in the `tool.uvoxen.req` section:

``` toml
[tool.uvoxen.req]
header = """
# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

"""
```

The `--check` option will make `uvoxen` exit with a non-zero code if
the file contents differ from what it expects, without modifying
the file itself:

``` sh
uvoxen req generate --check -g docs
```

If the output filename is specified as a single dash, `uvoxen` will
not write to any files, but display the generated text on its
standard output stream instead:

``` sh
uvoxen req generate -o - -g testenv-mypy
```

There is no `--diff` option yet, although one is planned.

## Generate a Tox configuration file

For people who still like to use Tox as a test runner, `uvoxen` can export
the test environment settings into a `tox.ini` file using
the `tox generate` subcommand:

``` sh
uvoxen tox generate
```

As with `req`, the `--output` (`-o`) and `--check` command-line options are
supported:

``` sh
uvoxen tox generate -o - | diff -u tox.ini -
```

As with `req`, the `header` and `footer` parameters in
the `uvoxen.tox` section are honored; the `footer` one, in particular, may be
used to define additional Tox environments that `uvoxen` will not handle.
For that purpose, there is also the `uvoxen.tox.envlist-append` list that
specifies the names of Tox environments to be added to the `tox.envlist`
setting in the generated `tox.ini` file.

By default, `uvoxen` will output the Tox environment definitions in
the order they are listed in `tool.uvoxen.envlist` with any additional ones
placed at the end in lexicographical order of their names.
If preferred, the `tool.uvoxen.env-order` list may be used to specify
the order of some environments to be placed first; the rest will still be output in
lexicographical order.
This may be useful when first converting a `tox.ini` file to `pyproject.toml`
definitions for `uvoxen` - it can minimize the difference between
the generated `tox.ini` file and the original one.

## Specify environment variables to be set for or passed into the environments

Like Tox, `uvoxen` supports the `passenv` list and the `setenv` table for
test environments:

``` toml
[tool.uvoxen.env.docker]
dependency-groups = [
  "testenv-docker",
]
install-project = true
passenv = [
  "TEST_DOCKER_OPTS",
]
commands = [
  "python3 -m test_docker run {env:TEST_DOCKER_OPTS}",
]

[tool.uvoxen.env.docker.setenv]
PYTHONPATH = "{toxinidir}/tests/docker/python"
```

Some Tox predefined variables, e.g. `{envdir}` or `{toxinidir}`, may be
used in `setenv` value strings; see the configuration section for a full list.

## Add tags for running environments in stages

An environment may specify a `tags` list:

``` toml
[tool.uvoxen.env.reuse]
tags = [
  "check",
  "quick",
]
dependency-groups = [
  "testenv-reuse",
]
commands = [
  "reuse lint",
]
```

It is currently ignored by the `uv` runner, but it will be copied into
the `tox.ini` file by `tox generate`, so that the Tox environments may
later be run in parallel stages using [the `tox-stages` tool][test-stages]:

``` sh
uvoxen tox generate
tox-stages run
```

An additional `uv run-stages` subcommand is planned.

[ruff]: https://astral.sh/ruff "Ruff - lint at lightspeed"
[pep-735]: https://peps.python.org/pep-0735/ "PEP 735 – Dependency Groups in pyproject.toml"
[test-stages]: https://devel.ringlet.net/devel/test-stages "test-stages - run Tox tests in groups, stopping on errors"
