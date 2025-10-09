# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Generate `requirements/*.txt` files out of the dependency group definitions."""

from __future__ import annotations

import dataclasses
import typing

from uvoxen import parse

from . import base


if typing.TYPE_CHECKING:
    from typing import Final


@dataclasses.dataclass(frozen=True)
class ReqRunner(base.Runner):
    """Generate `requirements/*.txt` files out of the dependency group definitions."""

    group: str
    """The dependency grouop to generate the requirements file for."""

    def generate(
        self,
        *,
        check: bool,
        diff: bool,
        force: bool,
        noop: bool = False,
        output: str | None = None,
    ) -> None:
        """Write the requirements file out if necessary."""

        def single(item: parse.PyDependencyGroupItem) -> str:
            """Output one or more lines corresponding to this dependency group item."""
            match item:
                case parse.PyDependencyGroupItemReq(req):
                    return f"{req}\n"

                case parse.PyDependencyGroupIncluded(group):
                    return all_items(group)

                case other:
                    raise RuntimeError(repr(other))

        def all_items(group: str) -> str:
            """Output one or more lines corresponding to these dependency group items."""
            return "".join(single(item) for item in self.proj.python_dependency_groups[group])

        header: Final = (
            "" if self.proj.req is None or self.proj.req.header is None else self.proj.req.header
        )

        footer: Final = (
            "" if self.proj.req is None or self.proj.req.footer is None else self.proj.req.footer
        )

        items: Final = all_items(self.group)

        res = f"{header}{items}{footer}"

        return self.generate_file(
            check=check,
            diff=diff,
            force=force,
            noop=noop,
            output=f"requirements/{self.group}.txt" if output is None else output,
            contents=res,
        )
