# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Test the Tox expansion emulator."""

from __future__ import annotations

import dataclasses
import pathlib
import shlex
import typing

from uvoxen import expand_tox_vars as etv


if typing.TYPE_CHECKING:
    from typing import Final


ENV_TRIVIAL: Final = {
    "USERNAME": "jrl",
}
"""Some simulated environment variables."""

GLOBALS_TRIVIAL: Final[dict[str, str | list[str]]] = {
    "toxinidir": "/nonexistent",
    "envdir": "/nosuch/env",
    "posargs": [],
}
"""Some simulated Tox global variables."""

GLOBALS_TRIVIAL_EXPANDED: Final[dict[str, str]] = {
    f"{{{name}}}": value if isinstance(value, str) else shlex.join(value)
    for name, value in GLOBALS_TRIVIAL.items()
}
"""The cached version of the Tox global variables."""

TRIVIAL_VARS_EXPANDED: Final = {
    "env": ENV_TRIVIAL,
    "setenv": {},
    "tox_globals": GLOBALS_TRIVIAL,
    "user_vars": {},
    "cache": GLOBALS_TRIVIAL_EXPANDED,
}


def test_empty() -> None:
    """No variables or anything."""
    tvars: Final = etv.Variables(
        env=dict(ENV_TRIVIAL),
        setenv={},
        tox_globals=dict(GLOBALS_TRIVIAL),
        user_vars={},
    )

    # Make sure the `__post_init__()` method did not do anything rash."""
    assert dataclasses.asdict(tvars) == TRIVIAL_VARS_EXPANDED


def test_already_cached() -> None:
    """Look things up in the pre-generated cache."""
    tvars: Final = etv.Variables(
        env=dict(ENV_TRIVIAL),
        setenv={},
        tox_globals=dict(GLOBALS_TRIVIAL),
        user_vars={},
    )
    assert dataclasses.asdict(tvars) == TRIVIAL_VARS_EXPANDED

    assert tvars.expand("{toxinidir}") == GLOBALS_TRIVIAL["toxinidir"]
    assert dataclasses.asdict(tvars) == TRIVIAL_VARS_EXPANDED


def run_expansion_list(tvars: etv.Variables, steps: list[tuple[str, str, dict[str, str]]]) -> None:
    """Expand the strings one by one, make sure the cache is updated."""
    cache = dict(tvars.cache)
    for line, expanded, added in steps:
        assert tvars.expand(line) == expanded, repr(tvars)
        assert tvars.cache == {**cache, **added}
        cache = dict(tvars.cache)


def test_non_recursive() -> None:
    """Expand a couple of single variables without recursion."""
    tvars: Final = etv.Variables(
        env=dict(ENV_TRIVIAL),
        setenv={},
        tox_globals=dict(GLOBALS_TRIVIAL),
        user_vars={
            "defs": {"pyfiles": ["src/projname", "tests/unit"]},
            "something": {"else": "nothing-really"},
        },
    )
    assert tvars.cache == GLOBALS_TRIVIAL_EXPANDED

    no_vars: Final = "no variables at all"
    something_else: Final = "{[something]else}"
    nothing_really: Final = "nothing-really"
    sentence: Final = f"This is {something_else}, is it not?"
    sentence_exp: Final = f"This is {nothing_really}, is it not?"
    defs_pyfiles: Final = "{[defs]pyfiles}"
    src_files: Final = "src/projname tests/unit"
    cmd: Final = f"ruff --check {defs_pyfiles}"
    cmd_exp: Final = f"ruff --check {src_files}"
    run_expansion_list(
        tvars,
        [
            (no_vars, no_vars, {no_vars: no_vars}),
            (no_vars, no_vars, {}),
            (
                sentence,
                sentence_exp,
                {
                    sentence: sentence_exp,
                    nothing_really: nothing_really,
                    something_else: nothing_really,
                },
            ),
            (no_vars, no_vars, {}),
            (something_else, nothing_really, {}),
            (no_vars, no_vars, {}),
            (
                cmd,
                cmd_exp,
                {
                    cmd: cmd_exp,
                    defs_pyfiles: src_files,
                    "src/projname": "src/projname",
                    "tests/unit": "tests/unit",
                },
            ),
            (defs_pyfiles, src_files, {}),
            (sentence, sentence_exp, {}),
        ],
    )


def test_expand_recursively() -> None:  # noqa: PLR0914  # this is weird
    """Expand some variables recursively."""
    cmd_ruff = "{[commands]ruff}"
    cmd_ruff_exp: Final = "ruff --config ruff-base.toml"
    cmd_ruff_format: Final = "{[commands]ruff_format}"
    cmd_ruff_format_exp: Final = f"{cmd_ruff_exp} format"

    contrib_something_else: Final = "contrib/something-else"
    src_projname: Final = "src/projname"
    src_selftest: Final = "src/selftest"
    tests_unit: Final = "tests/unit"

    defs_pyfiles_mypy: Final = "{[defs]pyfiles_mypy}"
    defs_pyfiles_mypy_exp: Final = f"{src_projname} {src_selftest}"
    defs_pyfiles_ruff: Final = "{[defs]pyfiles_ruff}"
    defs_pyfiles_ruff_exp: Final = tests_unit
    defs_pyfiles_black: Final = "{[defs]pyfiles_black}"
    defs_pyfiles_black_exp: Final = f"{defs_pyfiles_mypy_exp} {defs_pyfiles_ruff_exp}"
    defs_pyfiles: Final = "{[defs]pyfiles}"
    defs_pyfiles_exp: Final = f"{defs_pyfiles_black_exp} {contrib_something_else}"

    cmd_ruff_format_pyfiles: Final = f"{cmd_ruff_format} {defs_pyfiles}"
    cmd_ruff_format_pyfiles_exp: Final = (
        f"{cmd_ruff_exp} format {src_projname} {src_selftest} {tests_unit} {contrib_something_else}"
    )

    tvars: Final = etv.Variables(
        env=dict(ENV_TRIVIAL),
        setenv={},
        tox_globals=dict(GLOBALS_TRIVIAL),
        user_vars={
            "defs": {
                "pyfiles": [defs_pyfiles_black, contrib_something_else],
                "pyfiles_black": [defs_pyfiles_mypy, defs_pyfiles_ruff],
                "pyfiles_mypy": [src_projname, src_selftest],
                "pyfiles_ruff": [tests_unit],
            },
            "commands": {
                "ruff": cmd_ruff_exp,
                "ruff_format": f"{cmd_ruff} format",
            },
        },
    )
    assert tvars.cache == GLOBALS_TRIVIAL_EXPANDED

    run_expansion_list(
        tvars,
        [
            (
                cmd_ruff_format,
                cmd_ruff_format_exp,
                {
                    cmd_ruff: cmd_ruff_exp,
                    cmd_ruff_exp: cmd_ruff_exp,
                    cmd_ruff_format: cmd_ruff_format_exp,
                    f"{cmd_ruff} format": cmd_ruff_format_exp,
                },
            ),
            (
                cmd_ruff_format_pyfiles,
                cmd_ruff_format_pyfiles_exp,
                {
                    cmd_ruff_format_pyfiles: cmd_ruff_format_pyfiles_exp,
                    contrib_something_else: contrib_something_else,
                    defs_pyfiles: defs_pyfiles_exp,
                    defs_pyfiles_black: defs_pyfiles_black_exp,
                    defs_pyfiles_mypy: defs_pyfiles_mypy_exp,
                    defs_pyfiles_ruff: defs_pyfiles_ruff_exp,
                    src_projname: src_projname,
                    src_selftest: src_selftest,
                    tests_unit: tests_unit,
                },
            ),
        ],
    )


def test_expand_tox_too() -> None:
    """Also expand Tox variables."""
    defs_pyfiles: Final = "{[defs]pyfiles}"
    defs_pyfiles_exp: Final = "tests/unit"
    cmd_pytest: Final = "{[commands]pytest}"
    posargs: Final = "{posargs}"
    posargs_exp: Final = "-vv -k 'test_expand and more'"
    cmd_pytest_cmd: Final = f"pytest {posargs} {defs_pyfiles}"
    cmd_pytest_exp: Final = f"pytest {posargs_exp} {defs_pyfiles_exp}"

    tvars: Final = etv.Variables(
        env=dict(ENV_TRIVIAL),
        setenv={},
        tox_globals=etv.prepare_tox_vars(
            toxinidir=pathlib.Path("/nonexistent"),
            envdir=pathlib.Path("/nonesuch/venv"),
            posargs=["-vv", "-k", "test_expand and more"],
        ),
        user_vars={
            "commands": {
                "pytest": cmd_pytest_cmd,
            },
            "defs": {
                "pyfiles": defs_pyfiles_exp,
            },
        },
    )
    assert tvars.cache[posargs] == posargs_exp

    run_expansion_list(
        tvars,
        [
            (
                cmd_pytest,
                cmd_pytest_exp,
                {
                    cmd_pytest: cmd_pytest_exp,
                    cmd_pytest_cmd: cmd_pytest_exp,
                    defs_pyfiles: defs_pyfiles_exp,
                    defs_pyfiles_exp: defs_pyfiles_exp,
                },
            ),
            (defs_pyfiles, defs_pyfiles_exp, {}),
        ],
    )


def test_setenv() -> None:
    """Test `setenv` processing."""
    mypypath: Final = "{toxinidir}/stubs and more"
    mypypath_exp: Final = f"{GLOBALS_TRIVIAL['toxinidir']}/stubs and more"
    typeshed: Final = "{env:MYPYPATH}/typeshed"
    typeshed_exp: Final = f"{mypypath_exp}/typeshed"

    tvars: Final = etv.Variables(
        env=dict(ENV_TRIVIAL),
        setenv={
            "MYPYPATH": mypypath,
            "TYPESHED": typeshed,
        },
        tox_globals=dict(GLOBALS_TRIVIAL),
        user_vars={},
    )
    assert tvars.cache == {
        **GLOBALS_TRIVIAL_EXPANDED,
        "{env:MYPYPATH}": mypypath_exp,
        "{env:MYPYPATH}/typeshed": typeshed_exp,
        "{env:TYPESHED}": typeshed_exp,
        mypypath: mypypath_exp,
    }

    run_expansion_list(
        tvars,
        [
            ("{env:MYPYPATH}", mypypath_exp, {}),
            ("{env:TYPESHED}", typeshed_exp, {}),
            (
                "{env:NONESUCH}",
                "",
                {
                    "{env:NONESUCH}": "",
                },
            ),
        ],
    )
