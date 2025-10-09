# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Run commands for the specified environments."""

from __future__ import annotations

import dataclasses
import pathlib
import shlex
import subprocess  # noqa: S404
import typing

from uvoxen import defs
from uvoxen import expand_tox_vars
from uvoxen import parse


if typing.TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Final


@dataclasses.dataclass
class NotRegularFileError(defs.Error):
    """The specified output path points to something that is not a regular file."""

    path: pathlib.Path
    """The path to what we expected to be a file."""

    def __str__(self) -> str:
        """Provide a human-readable error message."""
        return f"Not a regular file: {self.path}"


@dataclasses.dataclass
class NeedsRegeneratingError(defs.Error):
    """One or more test configuration files need to be regenerated."""

    paths: list[pathlib.Path]
    """The paths to the files that need to be regenerated."""

    def __str__(self) -> str:
        """Provide a human-readable error message."""
        return f"Need to regenerate {' '.join(str(path) for path in self.paths)}"


@dataclasses.dataclass
class CommandError(defs.Error):
    """An error that occurred when running a command."""

    cmd: list[str]
    """The command we tried to run."""

    @property
    def cmdstr(self) -> str:
        """A string representation of the command we tried to run."""
        return shlex.join(self.cmd)

    def __str__(self) -> str:
        """Provide a human-readable error message."""
        return f"Error running the `{self.cmdstr}` command: {self!r}"


@dataclasses.dataclass
class CommandRunError(CommandError):
    """Could not run the specified command at all."""

    err: Exception
    """The error that occurred."""

    def __str__(self) -> str:
        """Provide a human-readable error message."""
        return f"Could not run the `{self.cmdstr}` command: {self.err}"


@dataclasses.dataclass
class CommandFailedError(CommandError):
    """The specified command exited with a non-zero code."""

    code: int
    """The exit code."""

    def __str__(self) -> str:
        """Provide a human-readable error message."""
        return f"The `{self.cmdstr}` command exited with code {self.code}"


def prepare_tox_vars(*, posargs: list[str]) -> dict[str, str | list[str]]:
    """Simulate (to some extent) the way Tox prepares its environment variables."""
    toxinidir: Final = pathlib.Path.cwd()
    return expand_tox_vars.prepare_tox_vars(
        toxinidir=toxinidir,
        envdir=toxinidir / ".venv",
        posargs=posargs,
    )


@dataclasses.dataclass(frozen=True)
class Runner:
    """Abstract base class for running commands for environments."""

    cfg: defs.Config
    """The runtime configuration."""

    posargs: list[str]
    """The command-line arguments passed for this run."""

    proj: parse.Project
    """The project to run environments for."""

    def _generate_file_check_only(
        self,
        *,
        output: str,
        opath: pathlib.Path,
        contents: str,
        diff: bool,
        is_up_to_date: Callable[[], bool],
    ) -> None:
        """Handle check-only mode according to the other options."""
        if is_up_to_date():
            self.cfg.log.info("The %(output)s file is up to date", {"output": output})
            return

        if diff:
            subprocess.run(  # noqa: S603
                ["diff", "-u", "--", opath, "-"],  # noqa: S607
                check=False,
                encoding="UTF-8",
                input=contents,
            )

        raise NeedsRegeneratingError([opath])

    def generate_file(  # noqa: PLR0913  # this function does many things
        self,
        *,
        check: bool,
        diff: bool,
        force: bool,
        noop: bool,
        output: str,
        contents: str,
    ) -> None:
        """Write a file out if needed."""
        if output == "-":
            print(contents, end="")  # noqa: T201
            return

        opath: Final = pathlib.Path(output)
        if opath.is_symlink() or (opath.exists() and not opath.is_file()):
            raise NotRegularFileError(opath)

        def is_up_to_date() -> bool:
            """Check whether the file contents are up to date."""
            if not opath.exists():
                return False

            try:
                return opath.read_text(encoding="UTF-8") == contents
            except ValueError:
                return False

        if check:
            if not force:
                self._generate_file_check_only(
                    contents=contents,
                    output=output,
                    opath=opath,
                    diff=diff,
                    is_up_to_date=is_up_to_date,
                )
                return
        elif is_up_to_date():
            self.cfg.log.info("The %(output)s file is up to date", {"output": output})
            return

        self.cfg.log.info(
            "Writing %(count)d characters to the %(output)s file",
            {"count": len(contents), "output": output},
        )
        if noop:
            self.cfg.log.info("Would write to %(output)s", {"output": output})
        else:
            opath.write_text(contents, encoding="UTF-8")

    def generate(
        self,
        *,
        check: bool,
        diff: bool,
        force: bool,
        noop: bool = False,
        output: str | None = None,
    ) -> None:
        """Generate the test configuration if necessary."""
        raise NotImplementedError(repr(self))

    def run(self, *, envs: list[str], noop: bool = False) -> None:
        """Generate and run commands."""
        raise NotImplementedError(repr(self))

    def run_command(
        self,
        cmd: list[str],
        *,
        env: dict[str, str] | None = None,
        noop: bool = False,
    ) -> None:
        """Run a single command or display it in noop mode."""
        cmdstr: Final = shlex.join(cmd)
        if noop:
            self.cfg.log.info("Would run `%(cmdstr)s`", {"cmdstr": cmdstr})
            print(cmdstr)  # noqa: T201
            return

        self.cfg.log.info("About to run `%(cmdstr)s`", {"cmdstr": cmdstr})
        if env is not None:
            self.cfg.log.info("- environment: %(env)r", {"env": env})
        try:
            subprocess.check_call(cmd, env=env, shell=False)  # noqa: S603
        except OSError as err:
            raise CommandRunError(cmd, err) from err
        except subprocess.CalledProcessError as err:
            raise CommandFailedError(cmd, err.returncode) from err
