# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Configure and run tests using the `tox` tool."""

from __future__ import annotations

import dataclasses
import itertools
import typing

from . import base


if typing.TYPE_CHECKING:
    from typing import Final

    from uvoxen import parse


@dataclasses.dataclass(frozen=True)
class ToxRunner(base.Runner):
    """Generate `tox.ini`, run the tests using Tox."""

    def expand_tox_defs(self) -> str:
        """Expand the `[defs]` section: strings or lists of strings."""

        def single(name: str, value: str | list[str]) -> str:
            """Expand the value of a single definition."""
            match value:
                case str(value_str):
                    return f"{name} = {value_str}"

                case list(values):
                    lines: Final = " \\\n".join(f"  {item}" for item in values)
                    return f"{name} =\n{lines}"

                case other:
                    raise RuntimeError(repr(other))

        if not self.proj.defs:
            return ""

        expanded: Final = "\n".join(itertools.starmap(single, self.proj.defs.items()))
        return f"[defs]\n{expanded}"

    def get_tox_env_order(self) -> list[str]:
        """Get the order of the environments to write into the Tox configuration."""

        def listed_before_others(listed: list[str], envs: list[str]) -> list[str]:
            """Put the listed environments first."""
            return [*listed, *(name for name in envs if name not in listed)]

        return listed_before_others(
            self.proj.tox.env_order
            if self.proj.tox is not None and self.proj.tox.env_order is not None
            else self.proj.envlist,
            sorted(self.proj.env),
        )

    def generate_env(self, name: str, env: parse.Environment) -> str:
        """Generate the configuration for a single Tox environment."""
        commands: Final = "\n".join(f"  {cmd}" for cmd in env.commands)

        skip_install = (
            ""
            if not self.proj.build_project or env.install_project or env.install_dependencies
            else "\nskip_install = True"
        )

        tags = "" if env.tags is None else "\ntags =\n" + "\n".join(f"  {tag}" for tag in env.tags)

        dep_groups = (
            "\ndependency_groups =\n" + "\n".join(f"  {dep}" for dep in env.dependency_groups)
            if env.dependency_groups
            else ""
        )

        setenv = (
            "\nsetenv =\n"
            + "\n".join(f"  {name} = {value}" for name, value in sorted(env.setenv.items()))
            if env.setenv
            else ""
        )

        passenv = (
            "\npassenv =\n" + "\n".join(f"  {name}" for name in sorted(env.passenv))
            if env.passenv
            else ""
        )

        externals = (
            "\nallowlist_externals =\n" + "\n".join(f"  {item}" for item in env.allowlist_externals)
            if env.allowlist_externals is not None
            else ""
        )

        return f"""
[testenv:{name}]{skip_install}{tags}{dep_groups}{setenv}{passenv}{externals}
commands =
{commands}
"""

    def generate(
        self,
        *,
        check: bool,
        diff: bool,
        force: bool,
        noop: bool = False,
        output: str | None = None,
    ) -> None:
        """Write `tox.ini` out if necessary."""
        header: Final = "" if self.proj.tox is None else self.proj.tox.header
        footer: Final = "" if self.proj.tox is None else self.proj.tox.footer
        isolated_or_sdist = (
            "isolated_build = True" if self.proj.build_project else "skipsdist = True"
        )
        envlist: Final = "".join(
            f"\n  {name}"
            for name in [
                *self.proj.envlist,
                *(
                    self.proj.tox.envlist_append
                    if self.proj.tox is not None and self.proj.tox.envlist_append is not None
                    else []
                ),
            ]
        )
        defs_expanded: Final = self.expand_tox_defs()
        envs: Final = "".join(
            itertools.starmap(
                self.generate_env,
                ((name, self.proj.env[name]) for name in self.get_tox_env_order()),
            ),
        )
        res = f"""{header}[tox]
minversion = 4.22
envlist ={envlist}
{isolated_or_sdist}

{defs_expanded}
{envs}{footer}
"""[:-1]

        self.generate_file(
            check=check,
            diff=diff,
            force=force,
            noop=noop,
            output="tox.ini" if output is None else output,
            contents=res,
        )

    def run(self, *, envs: list[str], noop: bool = False) -> None:
        """Run `tox`."""
        self.run_command(
            [
                "uvx",
                *(["-p", self.cfg.python] if self.cfg.python is not None else []),
                "--with",
                "tox-uv",
                "--",
                "tox",
                "run-parallel",
                *(["-e", ",".join(envs)] if envs else []),
                "--",
                *self.posargs,
            ],
            noop=noop,
        )
