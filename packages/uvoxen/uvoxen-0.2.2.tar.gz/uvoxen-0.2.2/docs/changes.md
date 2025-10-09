<!--
SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
SPDX-License-Identifier: BSD-2-Clause
-->

# Changelog

All notable changes to the uvoxen project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.2] - 2025-10-08

### Fixes

- Bump some lower dependency constraints to satisfy `uv --resolution=lowest`.

### Other changes

- Allow `media-type-version` 0.2.x with no changes; necessary for the lockstep
  upgrade of the `cappa` dependency here and in `media-type-version`.
- Allow `cappa` up to 0.30.x with no changes for the same lockstep upgrade.
- Allow `uv` 0.8.x with no changes.
- Documentation:
    - switch to a `mediaType` declaration for the `publync` configuration

## [0.2.1] - 2025-06-08

### Other changes

- Allow `cappa` 0.28.x with no changes; necessary for the lockstep upgrade of
  the `cappa` dependency here and in `media-type-version`.
- Testing framework:
    - use `ruff` 0.11.13 with no changes

## [0.2.0] - 2025-05-23

### INCOMPATIBLE CHANGES

- Use the `tool.uvoxen.mediaType` TOML string field instead of
  the `tool.uvoxen.format.version.major/minor` integer fields.
  The media type string must be of the form
  `vnd.ringlet.devel.uvoxen.config/uvoxen.v0.3+toml`;
  the only currently supported version is 0.3.

### Additions

- Add Python 3.14 as a supported version now that we use `typedload` instead of
  `mashumaro`.
- Documentation:
    - add a forgotten description of the `tool.uvoxen.build-project` boolean field
      (the whole reason for version 0.2 of the configuration file format)

### Other changes

- Switch from `mashumaro` to `typedload` for parsing the configuration file.
- Switch from `click` to `cappa` for command-line argument processing.
- Build infrastructure:
    - allow `packaging` 25.x with no changes
    - allow `uv` 0.7.x with no changes
    - add a dependency on the new `media-type-version` library
- Testing framework:
    - drop the pytest 7.x test environment, only use pytest 8
    - use Ruff 0.11.11 with no changes
- Documentation:
    - allow `mkdocstrings` 0.29.x with no changes

## [0.1.1] - 2025-03-12

### Additions

- Define configuration format 0.2:
    - add the `tool.uvoxen.build-project` boolean field for projects that are
      not really Python libraries and `uv --install-project` is irrelevant
- Add the `--diff` option to `req generate` and `tox generate` in check-only mode.
- Belatedly declare the `req-generate` feature at version 0.1.

### Fixes

- Add the version 0.1.0 changelog entry to this file.

## [0.1.0] - 2025-03-08

### Started

- First public release.

[Unreleased]: https://gitlab.com/ppentchev/uvoxen/-/compare/release%2F0.2.2...main
[0.2.2]: https://gitlab.com/ppentchev/uvoxen/-/compare/release%2F0.2.1...release%2F0.2.2
[0.2.1]: https://gitlab.com/ppentchev/uvoxen/-/compare/release%2F0.2.0...release%2F0.2.1
[0.2.0]: https://gitlab.com/ppentchev/uvoxen/-/compare/release%2F0.1.1...release%2F0.2.0
[0.1.1]: https://gitlab.com/ppentchev/uvoxen/-/compare/release%2F0.1.0...release%2F0.1.1
[0.1.0]: https://gitlab.com/ppentchev/uvoxen/-/tags/release%2F0.1.0
