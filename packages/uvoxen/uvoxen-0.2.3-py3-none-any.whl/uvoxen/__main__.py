# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Generate test configuration files, run tests."""

from __future__ import annotations

import dataclasses
import sys
import typing
from typing import Annotated

import cappa

from . import defs
from . import parse
from . import util
from .run import base
from .run import req
from .run import tox
from .run import uv


if typing.TYPE_CHECKING:
    from typing import Final


PY_SUPPORTED: Final = "supported"
"""The magic Python version meaning "run for all supported Python versions"."""


@dataclasses.dataclass(frozen=True)
class Mode:
    """The chosen action."""

    cfg: defs.Config
    """The runtime configuration settings."""


@dataclasses.dataclass(frozen=True)
class ModeListEnvs:
    """List the defined environments."""


def cmd_features() -> None:
    """Display program features information and exit."""
    print("Features: " + " ".join(f"{name}={value}" for name, value in defs.FEATURES.items()))
    sys.exit(0)


@cappa.command(name="envs")
@dataclasses.dataclass(frozen=True)
class CmdListEnvs:
    """List the defined test environments."""

    @staticmethod
    def run(cfg: defs.Config) -> None:
        """List the environments."""
        try:
            proj: Final = parse.pyproject(cfg)
            print("\n".join(name for name in sorted(proj.env)))
        except defs.Error as err:
            sys.exit(f"Could not list the test environments: {err}")


@cappa.command(name="pythons")
@dataclasses.dataclass(frozen=True)
class CmdListPythons:
    """List the supported Python versions."""

    @staticmethod
    def run(cfg: defs.Config) -> None:
        """List the Python versions."""
        try:
            proj: Final = parse.pyproject(cfg)
            print("\n".join(proj.python_supported))
        except defs.Error as err:
            sys.exit(f"Could not list the supported Python versions: {err}")


@cappa.command(name="reqs")
@dataclasses.dataclass(frozen=True)
class CmdListReqs:
    """List the defined dependency groups."""

    @staticmethod
    def run(cfg: defs.Config) -> None:
        """List the defined dependency groups."""
        try:
            proj: Final = parse.pyproject(cfg)
            print("\n".join(sorted(proj.python_dependency_groups)))
        except defs.Error as err:
            sys.exit(f"Could not list the project dependency groups: {err}")


@cappa.command(name="list")
@dataclasses.dataclass(frozen=True)
class CmdList:
    """List various configuration settings."""

    cmd: cappa.Subcommands[CmdListEnvs | CmdListPythons | CmdListReqs]
    """List something or something else."""

    def run(self, cfg: defs.Config) -> None:
        """List something."""
        self.cmd.run(cfg)


@cappa.command(name="generate")
@dataclasses.dataclass(frozen=True)
class CmdReqGenerate:
    """Generate the `requirements/groupname.txt` file."""

    group: Annotated[str, cappa.Arg(required=True, short=True, long=True)]
    """The dependency group to generate the requirements file for."""

    check: Annotated[bool, cappa.Arg()]
    """Check whether the file is up to date."""

    diff: Annotated[bool, cappa.Arg()]
    """In check mode, display a diff."""

    force: Annotated[bool, cappa.Arg(short=True)]
    """Only write the file out if it has changed."""

    noop: Annotated[bool, cappa.Arg(short="N")]
    """No-operation mode; display what would be done."""

    output: Annotated[str | None, cappa.Arg(short=True)]
    """The name of the file to write to, or '-' for standard output."""

    def run(self, cfg: defs.Config) -> None:
        """Generate the file."""
        try:
            proj: Final = parse.pyproject(cfg)

            runner = req.ReqRunner(cfg=cfg, proj=proj, posargs=[], group=self.group)
            runner.generate(
                check=self.check,
                diff=self.diff,
                force=self.force,
                noop=self.noop,
                output=self.output,
            )
        except base.NeedsRegeneratingError as err:
            sys.exit(str(err))
        except defs.Error as err:
            sys.exit(f"Could not generate the requirements file: {err}")


@cappa.command(name="req")
@dataclasses.dataclass(frozen=True)
class CmdReq:
    """Export dependency groups as requirement text files."""

    cmd: cappa.Subcommands[CmdReqGenerate]
    """Do something related to requirement groups."""

    def run(self, cfg: defs.Config) -> None:
        """Do something."""
        self.cmd.run(cfg)


@cappa.command(name="generate")
@dataclasses.dataclass(frozen=True)
class CmdToxGenerate:
    """Generate the `requirements/groupname.txt` file."""

    check: Annotated[bool, cappa.Arg()]
    """Check whether the file is up to date."""

    diff: Annotated[bool, cappa.Arg()]
    """In check mode, display a diff."""

    force: Annotated[bool, cappa.Arg(short=True)]
    """Only write the file out if it has changed."""

    noop: Annotated[bool, cappa.Arg(short="N")]
    """No-operation mode; display what would be done."""

    output: Annotated[str | None, cappa.Arg(short=True)]
    """The name of the file to write to, or '-' for standard output."""

    def run(self, cfg: defs.Config) -> None:
        """Generate the file."""
        try:
            proj: Final = parse.pyproject(cfg)

            if cfg.python is None:
                cfg.log.info("Generating tox.ini using the default Python version")
            else:
                cfg.log.info("Generating tox.ini using  Python %(pyver)s", {"pyver": cfg.python})

            runner = tox.ToxRunner(cfg=cfg, proj=proj, posargs=[])
            runner.generate(
                check=self.check,
                diff=self.diff,
                force=self.force,
                noop=self.noop,
                output=self.output,
            )
        except base.NeedsRegeneratingError as err:
            sys.exit(str(err))
        except defs.Error as err:
            sys.exit(f"Could not generate the Tox configuration: {err}")


@cappa.command(name="run")
@dataclasses.dataclass(frozen=True)
class CmdToxRun:
    """Run test environments using Tox."""

    env: Annotated[str | None, cappa.Arg(short=True, long=True)]
    """The environments to run commands for."""

    force: Annotated[bool, cappa.Arg(short=True)]
    """Only write the file out if it has changed."""

    noop: Annotated[bool, cappa.Arg(short="N")]
    """No-operation mode; display what would be done."""

    posargs: Annotated[list[str], cappa.Arg(num_args=-1)] = dataclasses.field(default_factory=list)
    """Additional arguments to pass to `tox run`."""

    def run(self, cfg: defs.Config) -> None:
        """Run the tests."""
        try:
            proj: Final = parse.pyproject(cfg)

            py_versions: Final = (
                [cfg.python] if cfg.python != PY_SUPPORTED else proj.python_supported
            )
            for pyver in py_versions:
                if pyver is None:
                    cfg.log.info("Running the tests for the default Python version")
                else:
                    cfg.log.info("Running the tests for Python %(pyver)s", {"pyver": pyver})

                runner = tox.ToxRunner(
                    cfg=dataclasses.replace(cfg, python=pyver),
                    proj=proj,
                    posargs=self.posargs,
                )
                runner.generate(check=False, diff=False, force=self.force, noop=self.noop)
                runner.run(envs=self.env.split(",") if self.env is not None else [], noop=self.noop)
        except defs.Error as err:
            sys.exit(f"Could not run the tests using Tox: {err}")


@cappa.command(name="tox")
@dataclasses.dataclass(frozen=True)
class CmdTox:
    """Generate the `tox.ini` file and run tests using Tox."""

    cmd: cappa.Subcommands[CmdToxGenerate | CmdToxRun]
    """Do something related to Tox."""

    def run(self, cfg: defs.Config) -> None:
        """Generate the file or run the tests."""
        self.cmd.run(cfg)


@cappa.command(name="run")
@dataclasses.dataclass(frozen=True)
class CmdUvRun:
    """Run test environments using uv."""

    env: Annotated[str | None, cappa.Arg(short=True, long=True)]
    """The environments to run commands for."""

    force: Annotated[bool, cappa.Arg(short=True)]
    """Only write the file out if it has changed."""

    noop: Annotated[bool, cappa.Arg(short="N")]
    """No-operation mode; display what would be done."""

    resolution: Annotated[str | None, cappa.Arg(long=True)]
    """The resolution mode to pass to `uv sync`."""

    posargs: Annotated[list[str], cappa.Arg(num_args=-1)] = dataclasses.field(default_factory=list)
    """Additional arguments to pass to `uv run`."""

    def run(self, cfg: defs.Config) -> None:
        """Run the test environments."""
        try:
            proj: Final = parse.pyproject(cfg)

            py_versions: Final = (
                [cfg.python] if cfg.python != PY_SUPPORTED else proj.python_supported
            )
            for pyver in py_versions:
                if pyver is None:
                    cfg.log.info("Running the tests for the default Python version")
                else:
                    cfg.log.info("Running the tests for Python %(pyver)s", {"pyver": pyver})

                runner = uv.UvRunner(
                    cfg=dataclasses.replace(cfg, python=pyver),
                    proj=proj,
                    posargs=self.posargs,
                    resolution=self.resolution,
                )
                runner.generate(check=False, diff=False, force=self.force, noop=self.noop)
                runner.run(
                    envs=self.env.split(",") if self.env is not None else proj.envlist,
                    noop=self.noop,
                )
        except defs.Error as err:
            sys.exit(f"Could not run the tests using uv: {err}")


@cappa.command(name="uv")
@dataclasses.dataclass(frozen=True)
class CmdUv:
    """Run tests using the uv tool."""

    cmd: cappa.Subcommands[CmdUvRun]
    """Do something related to `uv`."""

    def run(self, cfg: defs.Config) -> None:
        """Run the tests."""
        self.cmd.run(cfg)


@dataclasses.dataclass(frozen=True)
class Uvoxen:
    """Generate test configuration files and run tests."""

    cmd: cappa.Subcommands[CmdList | CmdReq | CmdTox | CmdUv]
    """Do something or something else."""

    features: Annotated[
        bool,
        cappa.Arg(action=cmd_features, has_value=False, num_args=0, hidden=True),
    ] = False
    """Display program features information and exit."""

    python: Annotated[str | None, cappa.Arg(short=True, long=True)] = None
    """The Python version to use, or 'supported' for all."""

    quiet: Annotated[bool, cappa.Arg(short=True)] = False
    """Quiet operation; only display warning and error messages."""

    verbose: Annotated[bool, cappa.Arg(short=True)] = False
    """Verbose operation; display diagnostic output."""

    def run(self) -> None:
        """Do something."""
        cfg = defs.Config(
            log=util.build_logger(quiet=self.quiet, verbose=self.verbose),
            python=self.python,
            verbose=self.verbose,
        )
        self.cmd.run(cfg)


def main() -> None:
    """Generate test configuration files and run tests."""
    args: Final = cappa.parse(Uvoxen, completion=False)
    if args.features:
        sys.exit("Internal error: how did we get to main() with features=True?")

    args.run()


if __name__ == "__main__":
    main()
