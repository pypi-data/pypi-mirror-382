<!--
SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
SPDX-License-Identifier: BSD-2-Clause
-->

# Configuration settings

## Overview

The `uvoxen` tool is configured using the `pyproject.toml` file.
Most of the definitions are in the `tool.uvoxen` section, but
it also parses the `dependency-groups` one and
the `project.classifiers` list.

``` toml
[project]
classifiers = [
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.13",
]

[dependency-groups]
testenv-docker = [
  "build >= 1, < 2",
]
testenv-mypy = [
  {include-group = "testenv-unit-tests"},
  "mypy >= 1.7, < 2",
]
testenv-unit-tests = [
  "pytest >= 7, < 8",
]

[tool.uvoxen]
mediaType = "vnd.ringlet.devel.uvoxen.config/uvoxen.v0.3+toml"
envlist = [
  "mypy",
  "unit-tests",
]

[tool.uvoxen.defs]
pyfiles = [
  "src/divert-and-modify",
  "tests/unit",
]

[tool.uvoxen.req]
header = """
# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

"""

[tool.uvoxen.tox]
env-order = [
  "format",
  "reformat",
  "ruff",
]

envlist-add = [
  "unit-tests-pytest-7",
]

footer = """

[testenv:unit-tests-pytest-7]
...
"""

[tool.uvoxen.env.mypy]
dependency-groups = [
  "testenv-mypy",
]
commands = [
  "mypy -- {[defs]pyfiles}",
]

[tool.uvoxen.env.unit-tests]
dependency-groups = [
  "testenv-unit-tests",
]
install-project = true
commands = [
  "pytest {posargs} tests/unit",
]

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

## Variable expansion

In several places (commands run via `uv run`, environment variables
listed in `setenv` tables) the `uvoxen` tool will parse a string and
substitute variable specifications with expanded values.

### Variables from the defs section

The `tool.uvoxen.defs` section of the `pyproject.toml` file contains
variables (strings or lists of strings) that may be expanded using
the `{[defs]varname}` syntax.

### Environment variables

The `{env:NAME}` syntax may be used to substitute the string value of
a variable in the current process environment.

Default values (`{env:NAME:DEFAULT}`) or recursive substituton are not
supported yet.

### Predefined Tox variables

For compatibility with Tox environment definitions, the following will
be expanded:

- `{envdir}`: the full path to the virtual environment prepared for this test run
- `{posargs}`: additional command-line arguments passed to the `uv run` subcommand
- `{toxinidir}`: the full path to the directory containing the `pyproject.toml` file

## Configuration settings

### tool.uvoxen

General definitions for various `uvoxen` subcommands.

#### tool.uvoxen.mediaType

The media type of the `uvoxen` configuration itself:

- the Ringlet `uvoxen` vendor ID
- the version of the format of the configuration file itself
- the TOML identification suffix

This is a string value of the form `vnd.ringlet.devel.uvoxen.config/uvoxen.v0.3+toml`
with the only variable part being the major and minor version components,
in this case "0" and "3" respectively.

This version is similar to a semantic one: the major number will only be
incremented on incompatible changes (removing a setting or changing
the meaning or type of one), and the minor number will be incremenented
when new settings are added, but the meaning of the existing ones is
not changed.
Thus, a version of `uvoxen` that is capable of parsing configuration
files in the `2.3` format will be able to fully process files in
the `2.0`, `2.1`, and `2.2` ones, and it will be able to read files in
the `2.4` or `2.12` format, although some of their fields may be ignored.

There is no guarantee that versions of `uvoxen` will necessarily be able to
read files with a lower major version of the format.
The lowest and highest supported format versions are available as
the `format-min` and `format-max` features in the output of
the `uvoxen --features` command or the `uvoxen.defs.FEATURES` Python dictionary.

Added in format version 0.3.

#### tool.uvoxen.build-project

Boolean.

Whether to build the project at all or only run the tests.

The default value is true, which is correct for Python projects.
For projects that use `uvoxen` to only e.g. build the documentation or run
`reuse` checks, this should be set to false.

Added in format version 0.2.

#### tool.uvoxen.defs

Table of strings or lists of strings.

The keys are variable names; the values will be expanded in commands to be run or
environment variables to be set using Tox-like `{[defs]varname}` syntax.
The values may contain variables themselves: `{[defs]name}` for other variables,
`{env:NAME}` for environment variables, or predefined Tox ones such as
`{envdir}`, `{toxinidir}`, etc.

Added in format version 0.1.

#### tool.uvoxen.envlist

List of strings.

The environment names to be run by default by the `uv run` subcommand, or
to be output as `tox.envlist` by the `tox generate` / `tox run` ones.

Added in format version 0.1.

### tool.uvoxen.req

Definitions for the `req generate` subcommand.

#### tool.uvoxen.req.footer

Multiline string.

One or more lines of text to be placed at the bottom of the generated file.

Added in format version 0.1.

#### tool.uvoxen.req.header

Multiline string.

One or more lines of text to be placed at the top of the generated file.

Added in format version 0.1.

### tool.uvoxen.tox

Definitions for the `tox generate` subcommand.

#### tool.uvoxen.env-order

List of strings.

Environment names to be output first after the `tox` and `defs` sections of
the generated file.
Any environments not listed here will be output in lexicographical order of
their names.

Added in format version 0.1.

#### tool.uvoxen.envlist-append

List of strings.

Environment names to append to the end of the `tox.envlist` variable.

Added in format version 0.1.

#### tool.uvoxen.tox.footer

Multiline string.

One or more lines of text to be placed at the bottom of the generated file.

Added in format version 0.1.

#### tool.uvoxen.tox.header

Multiline string.

One or more lines of text to be placed at the top of the generated file.

Added in format version 0.1.

### tool.uvoxen.env

The definitions of the test environments themselves.

#### tool.uvoxen.env.NAME.allowlist-externals

List of strings

The names of allowed external commands that will be copied into
the `allowlist_externals` parameter of the Tox environment.

Added in format version 0.1.

#### tool.uvoxen.env.NAME.commands

List of strings.

The commands to be run in succession for this test environment.
When these commands are run via the `uv run` subcommand, Tox-style variables
(`{[defs]varname]}`, `{env:NAME}`, `{envdir}`, `{posargs}`, etc.)
will be expanded.

Added in format version 0.1.

#### tool.uvoxen.env.NAME.dependency-groups

List of strings.

The names of the dependency groups to be installed into the virtual
environment when running this test.
The groups must be defined in the `dependency-groups` top-level section of
the `pyproject.toml` file.

Added in format version 0.1.

#### tool.uvoxen.env.NAME.install-dependencies

Boolean.

Whether this test environment needs the project dependencies
(but not necessarily the project itself) to be installed into
the virtual environment.

This parameter is ignored by the `uv run` subcommand, but it causes
the `uv generate` one to omit the `skip_install=True` line, so that
the project itself will be installed into the Tox virtual environment.

Added in format version 0.1.

#### tool.uvoxen.env.NAME.install-project

Boolean.

Whether this test environment needs the project itself to be installed into
the virtual environment.

This parameter is ignored by the `uv run` subcommand, but it causes
the `uv generate` one to omit the `skip_install=True` line, so that
the project itself will be installed into the Tox virtual environment.

Added in format version 0.1.

#### tool.uvoxen.env.NAME.passenv

List of strings.

The names of additional environment variables that will be passed from
the current process environment into the one where the test is run.

Added in format version 0.1.

#### tool.uvoxen.env.NAME.setenv

Table of strings.

The names and values of environment variables to be set when running the test.
Variable specifications in the values will be expanded when the test is
run via the `uv run` subcommand.

Added in format version 0.1.

#### tool.uvoxen.env.NAME.tags

List of strings.

Tags that will be copied into the `tags` parameter of the Tox environment so that
it may later be selected or ordered for running by
[the `tox-stages` tool][test-stages].

A `uv run-stages` subcommand is planned; it will also make use of these.

Added in format version 0.1.

[test-stages]: https://devel.ringlet.net/devel/test-stages "test-stages - run Tox tests in groups, stopping on errors"
