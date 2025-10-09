# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Configure and run tests using the `uv` tool."""

from __future__ import annotations

import dataclasses
import itertools
import pathlib
import shlex
import typing

from uvoxen import defs
from uvoxen import expand_tox_vars

from . import base


if typing.TYPE_CHECKING:
    from typing import Final


@dataclasses.dataclass
class EnvUndefinedError(defs.Error):
    """One or more of the specified environments are not defined."""

    missing_envs: list[str]
    """The missing environments."""

    def __str__(self) -> str:
        """Provide a human-readable error message."""
        plu: Final = "" if len(self.missing_envs) == 1 else "s"
        return f"Undefined environment{plu}: {' '.join(self.missing_envs)}"


@dataclasses.dataclass(frozen=True)
class UvRunner(base.Runner):
    """Run commands using the `uv` tool."""

    resolution: str | None
    """The resolution mode to pass to `uv sync`."""

    def generate(
        self,
        *,
        check: bool,  # noqa: ARG002  # class inheritance
        diff: bool,  # noqa: ARG002  # class inheritance
        force: bool,  # noqa: ARG002  # class inheritance
        noop: bool = False,  # noqa: ARG002  # class inheritance
        output: str | None = None,  # noqa: ARG002  # class inheritance
    ) -> None:
        """Generate the test configuration if necessary."""
        self.cfg.log.info("Nothing to generate for `uv`")

    def run(self, *, envs: list[str], noop: bool = False) -> None:
        """Run commands."""
        missing_envs: Final = [env for env in envs if env not in self.proj.env]
        if missing_envs:
            raise EnvUndefinedError(missing_envs)

        for name, env in ((name, self.proj.env[name]) for name in envs):
            tox_globals = base.prepare_tox_vars(posargs=self.posargs)
            tox_env = expand_tox_vars.prepare_env(
                env=env,
                envdir=pathlib.Path(str(tox_globals["envdir"])),
            )
            self.cfg.log.debug("- prepared tox vars %(tox_globals)r", {"tox_globals": tox_globals})
            tvars = expand_tox_vars.Variables(
                env=tox_env,
                setenv=env.setenv,
                tox_globals=tox_globals,
                user_vars={"defs": self.proj.defs},
            )

            self.cfg.log.info("Running commands for the %(name)s environment", {"name": name})

            self.run_command(["rm", "-rf", "--", ".venv"], noop=noop)

            # sync
            self.run_command(
                [
                    "uv",
                    "sync",
                    *([] if self.cfg.python is None else ["-p", self.cfg.python]),
                    *(
                        []
                        if self.proj.build_project and env.install_project
                        else ["--no-install-project"]
                    ),
                    *([] if self.resolution is None else ["--resolution", self.resolution]),
                    *itertools.chain(
                        *(["--group", dep_group] for dep_group in env.dependency_groups),
                    ),
                ],
                noop=noop,
            )

            # run
            for cmd_raw in env.commands:
                cmd_exp = tvars.expand(cmd_raw)
                self.run_command(
                    ["uv", "run", "--no-sync", "--", *shlex.split(cmd_exp)],
                    env=tvars.env,
                    noop=noop,
                )
