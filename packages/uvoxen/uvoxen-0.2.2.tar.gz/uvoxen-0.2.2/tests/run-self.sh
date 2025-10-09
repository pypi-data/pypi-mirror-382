#!/bin/sh
# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

set -e
set -x

reinstall_self()
{
	rm -rf .venv
	uv sync --exact
}

reinstall_self
.venv/bin/uvoxen uv run

reinstall_self
.venv/bin/uvoxen -p supported uv run -e mypy,unit-tests

if [ -n "$TEST_SELF_TOX_STAGES" ]; then
	reinstall_self
	"$TEST_SELF_TOX_STAGES" run
fi

reinstall_self
