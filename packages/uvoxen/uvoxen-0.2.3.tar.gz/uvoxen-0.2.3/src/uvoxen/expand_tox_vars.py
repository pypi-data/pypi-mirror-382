# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Simulate some of Tox's variable expansion."""

from __future__ import annotations

import dataclasses
import os
import os.path
import shlex
import typing

import pyparsing as pyp


if typing.TYPE_CHECKING:
    import pathlib
    from typing import Final

    from . import parse


ENV_PRESERVE_NAMES = (
    "https_proxy",
    "http_proxy",
    "no_proxy",
    "LANG",
    "LANGUAGE",
    "CURL_CA_BUNDLE",
    "SSL_CERT_FILE",
    "CC",
    "CFLAGS",
    "CCSHARED",
    "CXX",
    "CPPFLAGS",
    "LD_LIBRARY_PATH",
    "LDFLAGS",
    "HOME",
    "FORCE_COLOR",
    "NO_COLOR",
    "TMPDIR",
    "TEMP",
    "TMP",
    "USERPROFILE",
    "PATHEXT",
    "MSYSTEM",
    "WINDIR",
    "APPDATA",
    "PROGRAMDATA",
    "PROGRAMFILES(x86)",
    "SYSTEMDRIVE",
    "SYSTEMROOT",
    "COMSPEC",
    "PROCESSOR_ARCHITECTURE",
    "NUMBER_OF_PROCESSORS",
    "NETRC",
    "NIX_LD_LIBRARY_PATH",
    "TERM",
    "LINES",
    "COLUMNS",
)

ENV_PRESERVE_PREFIXES = (
    "PIP_",
    "VIRTUALENV_",
    "NIX_LD",
    "UV_",
)


@dataclasses.dataclass(frozen=True)
class ParsedPart:
    """The base class for parsed parts."""

    raw: str
    """The raw part."""


@dataclasses.dataclass(frozen=True)
class ParsedLiteral(ParsedPart):
    """A literal string."""

    value: str
    """The literal string itself."""


@dataclasses.dataclass(frozen=True)
class ParsedIdent(ParsedPart):
    """An identifier."""

    name: str
    """The identifier name."""


@dataclasses.dataclass(frozen=True)
class ParsedUserVar(ParsedPart):
    """A user variable with a section name."""

    section: str
    """The section name."""

    name: str
    """The variable name within the section."""


@dataclasses.dataclass(frozen=True)
class ParsedToxVar(ParsedPart):
    """A Tox variable without a section name."""

    name: str
    """The variable name."""


@dataclasses.dataclass(frozen=True)
class ParsedEnvVar(ParsedPart):
    """An environment variable."""

    name: str
    """The variable name."""


def raw_parts_to_str(tokens: pyp.ParseResults) -> str:
    """Build the raw string out of the parsed tokens."""

    def single(part: ParsedPart | str) -> str:
        """Get the raw string from a single parsed token."""
        match part:
            case ParsedPart(raw):
                return raw

            case str(raw_str):
                return raw_str

            case other:
                raise RuntimeError(repr(other))

    return "".join(single(part) for part in tokens.as_list())


_p_ident = pyp.Word(pyp.srange("[A-Za-z0-9_]"))


@_p_ident.set_parse_action
def _process_ident(tokens: pyp.ParseResults) -> ParsedIdent:
    """Build an identifier out of its name."""
    raw: Final = raw_parts_to_str(tokens)
    res: Final = tokens.as_list()
    match res:
        case [ident]:
            return ParsedIdent(raw, ident)

        case other:
            raise RuntimeError(repr(other))


_p_literal = pyp.CharsNotIn("{")


@_p_literal.set_parse_action
def _process_literal(tokens: pyp.ParseResults) -> ParsedLiteral:
    """Record the literal string."""
    raw: Final = raw_parts_to_str(tokens)
    res: Final = tokens.as_list()
    match res:
        case [str(literal)]:
            return ParsedLiteral(raw, literal)

        case other:
            raise RuntimeError(repr((tokens, other)))


_p_user_var = pyp.Literal("{[") + _p_ident + pyp.Literal("]") + _p_ident + pyp.Literal("}")


@_p_user_var.set_parse_action
def _process_user_var(tokens: pyp.ParseResults) -> ParsedUserVar:
    """Build a user var out of the identifiers."""
    raw: Final = raw_parts_to_str(tokens)
    res: Final = tokens.as_list()
    match res:
        case [_, ParsedIdent(_, section), _, ParsedIdent(_, name), _]:
            return ParsedUserVar(raw, section, name)

        case other:
            raise RuntimeError(repr(other))


_p_tox_var = pyp.Literal("{") + _p_ident + pyp.Literal("}")


@_p_tox_var.set_parse_action
def _process_tox_var(tokens: pyp.ParseResults) -> ParsedToxVar:
    """Build a Tox var out of the identifier."""
    raw: Final = raw_parts_to_str(tokens)
    res: Final = tokens.as_list()
    match res:
        case [_, ParsedIdent(_, name), _]:
            return ParsedToxVar(raw, name)

        case other:
            raise RuntimeError(repr(other))


_p_env_var = pyp.Literal("{env:") + _p_ident + pyp.Literal("}")


@_p_env_var.set_parse_action
def _process_env_var(tokens: pyp.ParseResults) -> ParsedEnvVar:
    """Build a Tox var out of the identifier."""
    raw: Final = raw_parts_to_str(tokens)
    res: Final = tokens.as_list()
    match res:
        case [_, ParsedIdent(_, name), _]:
            return ParsedEnvVar(raw, name)

        case other:
            raise RuntimeError(repr(other))


_p_part = _p_user_var | _p_tox_var | _p_env_var | _p_literal

_p_full_line = pyp.ZeroOrMore(_p_part)

_p_full_line_complete: Final = _p_full_line.leave_whitespace()


def quote_list(values: list[str]) -> str:
    """Quote the values using `shlex`.

    Break this out into a separate function in case we change our mind in
    the future of whether we want the quoting to happen here or not.
    """
    return " ".join(values)


@dataclasses.dataclass
class Variables:
    """The list of definitions, environment variables, and cached expansions."""

    env: dict[str, str]
    """The environment variables that this environment will see (before `setenv` processing)."""

    setenv: dict[str, str]
    """The `setenv` directives for this environment."""

    tox_globals: dict[str, str | list[str]]
    """The global variables, e.g. `posargs`, `envdir`, etc."""

    user_vars: dict[str, dict[str, str | list[str]]]
    """Variables defined in the `tox.ini` sections."""

    cache: dict[str, str] = dataclasses.field(default_factory=dict)
    """Cached values for variables that have already been expanded."""

    def __post_init__(self) -> None:
        """Expand the `setenv` definitions, cache `tox_globals`."""
        for name, value in self.tox_globals.items():
            exp_name = f"{{{name}}}"
            if exp_name in self.cache:
                raise RuntimeError(repr((self, name, value, exp_name)))

            match value:
                case str(value_str):
                    self.cache[exp_name] = value_str

                case list(value_list):
                    self.cache[exp_name] = quote_list(value_list)

                case value_other:
                    raise RuntimeError(repr((self, name, value, value_other)))

        for name, value in self.setenv.items():
            exp_name = f"{{env:{name}}}"
            if exp_name in self.cache:
                # Already referenced by another `setenv` variable
                continue

            self.env[name] = self.expand(exp_name)
            if exp_name not in self.cache:
                raise RuntimeError(repr((self, name, value, exp_name)))

    def _expand_single(self, part: ParsedPart) -> str:  # noqa: C901  # it is what it is
        """Expand a single part of the input line."""

        def cache_and_return(value: str) -> str:
            """Store the value into the cache and return it."""
            self.cache[part.raw] = value
            return value

        def scalar_or_list(value: str | list[str]) -> str:
            """Expand a value."""
            match value:
                case str(value_str):
                    return cache_and_return(self.expand(value_str))

                case list(value_list):
                    return cache_and_return(
                        " ".join(self.expand(item) for item in value_list),
                    )

                case value_other:
                    raise RuntimeError(repr((self, part, value_other)))

        if part.raw in self.cache:
            return self.cache[part.raw]

        match part:
            case ParsedLiteral(_literal_raw, literal_value):
                return literal_value

            case ParsedUserVar(_var_raw, var_section, var_name):
                return scalar_or_list(self.user_vars[var_section][var_name])

            case ParsedToxVar(_var_raw, var_name):
                return scalar_or_list(self.tox_globals[var_name])

            case ParsedEnvVar(_var_raw, var_name):
                setenv_value: Final = self.setenv.get(var_name)
                if setenv_value is not None:
                    return scalar_or_list(setenv_value)

                env_value: Final = self.env.get(var_name, "")
                return cache_and_return(env_value)

            case other:
                raise RuntimeError(repr((self, other)))

    def expand(self, line: str) -> str:
        """Expand (perhaps recursively) variables within a line."""
        if line in self.cache:
            return self.cache[line]

        parsed_parts: Final = _p_full_line_complete.parse_string(line, parse_all=True).as_list()
        res: Final = "".join(self._expand_single(part) for part in parsed_parts)
        self.cache[line] = res
        return res


def prepare_env(*, env: parse.Environment, envdir: pathlib.Path) -> dict[str, str]:
    """Sanitize the current environment."""
    return {
        name: value
        for name, value in os.environ.items()
        if name in ENV_PRESERVE_NAMES
        or name.startswith(ENV_PRESERVE_PREFIXES)
        or name in env.passenv
    } | {"PATH": f"{envdir}/bin{os.path.pathsep}{os.environ['PATH']}"}


def prepare_tox_vars(
    *,
    toxinidir: pathlib.Path,
    envdir: pathlib.Path,
    posargs: list[str],
) -> dict[str, str | list[str]]:
    """Simulate (to some extent) the way Tox prepares its environment variables."""
    return {
        "envdir": str(envdir),
        "posargs": [shlex.quote(word) for word in posargs],
        "toxinidir": str(toxinidir),
    }
