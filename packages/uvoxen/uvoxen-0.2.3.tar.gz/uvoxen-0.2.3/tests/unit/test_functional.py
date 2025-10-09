# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Make sure that `uvoxen run` starts up at least."""

from __future__ import annotations

import subprocess  # noqa: S404
import sys
import typing


if typing.TYPE_CHECKING:
    from typing import Final


def test_list_envs() -> None:
    """Make sure that `uvoxen list --help` and `uvoxen list` work."""
    output_help: Final = subprocess.check_output(  # noqa: S603
        [sys.executable, "-m", "uvoxen", "list", "envs", "--help"],
        encoding="UTF-8",
    )
    assert "Usage: " in output_help
    assert "format" not in output_help.splitlines()

    lines_list: Final = subprocess.check_output(  # noqa: S603
        [sys.executable, "-m", "uvoxen", "list", "envs"],
        encoding="UTF-8",
    ).splitlines()
    assert lines_list == [
        "docs",
        "format",
        "mypy",
        "pyupgrade",
        "reformat",
        "reuse",
        "ruff",
        "unit-tests",
        "uvoxen-sync-check",
        "var-expand-test",
    ]

    pythons_list: Final = subprocess.check_output(  # noqa: S603
        [sys.executable, "-m", "uvoxen", "list", "pythons"],
        encoding="UTF-8",
    ).splitlines()
    assert pythons_list == ["3.11", "3.12", "3.13", "3.14"]

    reqs_list: Final = subprocess.check_output(  # noqa: S603
        [sys.executable, "-m", "uvoxen", "list", "reqs"],
        encoding="UTF-8",
    ).splitlines()
    assert reqs_list == [
        "docs",
        "testenv-mypy",
        "testenv-pyupgrade",
        "testenv-reuse",
        "testenv-ruff",
        "testenv-unit-tests",
    ]


def test_uv_run_noop() -> None:
    """Make sure that `uvoxen uv run --help` and `uvoxen uv run --noop` work."""
    output_help: Final = subprocess.check_output(  # noqa: S603
        [sys.executable, "-m", "uvoxen", "uv", "run", "--help"],
        encoding="UTF-8",
    )
    assert "Usage: " in output_help
    assert "uv sync" not in output_help.splitlines()

    lines_list: Final = subprocess.check_output(  # noqa: S603
        [sys.executable, "-m", "uvoxen", "-v", "uv", "run", "--noop", "-e", "format"],
        encoding="UTF-8",
    ).splitlines()
    assert lines_list == [
        "rm -rf -- .venv",
        "uv sync --no-install-project --group testenv-ruff",
        (
            "uv run --no-sync -- "
            "ruff check --config ruff-base.toml --select=D,I --diff -- src/uvoxen tests/unit"
        ),
        (
            "uv run --no-sync -- "
            "ruff format --config ruff-base.toml --check --diff -- src/uvoxen tests/unit"
        ),
    ]


def test_tox_generate() -> None:
    """Make sure that `uvoxen tox generate -o -` outputs something sensible."""
    output_help: Final = subprocess.check_output(  # noqa: S603
        [sys.executable, "-m", "uvoxen", "tox", "generate", "--help"],
        encoding="UTF-8",
    )
    assert "Usage: " in output_help
    assert "\nenvlist =\n" not in output_help.splitlines()

    output_gen: Final = subprocess.check_output(  # noqa: S603
        [sys.executable, "-m", "uvoxen", "-v", "tox", "generate", "-o", "-"],
        encoding="UTF-8",
    )
    assert (
        """[tox]
minversion = 4.22
envlist =
  ruff
  format
  reuse
  mypy
  unit-tests
"""
    ) in output_gen

    assert (
        """[testenv:docs]
skip_install = True
tags =
  docs
dependency_groups =
  docs
commands =
  mkdocs build
"""
        in output_gen
    )


def test_tox_run() -> None:
    """Make sure `uvoxen tox run --noop` outputs something sensible."""
    output_help: Final = subprocess.check_output(  # noqa: S603
        [sys.executable, "-m", "uvoxen", "tox", "run", "--help"],
        encoding="UTF-8",
    )
    assert "Usage: " in output_help
    assert "tox run-parallel" not in output_help

    lines_run: Final = subprocess.check_output(  # noqa: S603
        [
            sys.executable,
            "-m",
            "uvoxen",
            "-v",
            "tox",
            "run",
            "--noop",
            "--",
            "--some",
            "arg uments",
        ],
        encoding="UTF-8",
    ).splitlines()
    assert lines_run == [
        "uvx --with tox-uv -- tox run-parallel -- --some 'arg uments'",
    ]

    lines_run_supported: Final = subprocess.check_output(  # noqa: S603
        [sys.executable, "-m", "uvoxen", "-v", "-p", "supported", "tox", "run", "--noop"],
        encoding="UTF-8",
    ).splitlines()
    assert lines_run_supported == [
        "uvx -p 3.11 --with tox-uv -- tox run-parallel --",
        "uvx -p 3.12 --with tox-uv -- tox run-parallel --",
        "uvx -p 3.13 --with tox-uv -- tox run-parallel --",
        "uvx -p 3.14 --with tox-uv -- tox run-parallel --",
    ]
