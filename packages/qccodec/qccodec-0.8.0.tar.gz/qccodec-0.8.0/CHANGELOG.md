# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

## [0.8.0] - 2025-10-06

### Removed

- 🚨Python 3.9 support. Minimum supported version is now 3.10. [#37](https://github.com/coltonbh/qccodec/pull/37).

### Changed

- 🚨 Updated to `qcio>=0.15.0` which incorporates new `qcio` nomenclature. [#37](https://github.com/coltonbh/qccodec/pull/37)
- Changed TeraChem encoder `Enum` lookups to compare `Enums` directly instead of string value.
- Updated `prog_inp` pytest fixture to have no keywords so that it can be reused in other outside of TeraChem.

### Added

- Test matrix that runs off a "pip" installed version of `qccodec`.

## [0.7.8] - 2025-07-07

### Fixed

- `crest` parsers imported missing `qcio.constants` module. Updated to `qcconst.constants`.

### Changed

- Bumped minimum `qcconst` version from `0.1.2` to `0.2.1` to fix `mypy` issue.

## [0.7.7] - 2025-06-23

### Changed

- TeraChem trajectory parsing now splits the optimization stdout into sections for each gradient call and runs `decode(...)` on each chunk. This fixes the excited state parsing bug mentioned in `Fixed` and setups up parser to be better isolated for their calculation type (e.g., no more `parse_gradients` but rather just `parse_gradient` for all cases of a single point calculation, even within an optimization workflow).
- TeraChem logs for each gradient call in an optimization calculation are now added to each `ProgramOutput` in `OptimizationResults.trajectory`.

### Fixed

- Excited state parsing bug within an optimization calculation that would result in all excited states for the whole optimization calculation being added to each `ProgramOutput` in the `.trajectory`.

### Removed

- `terachem.parse_gradients` function now that that gradient parsing is done gradient call-by-gradient call for optimizations instead of in one batch.

## [0.7.6] - 2025-04-01

### Added

- Logging to `decode` clearly detail what parsing actions are being taken and why on various filetypes.

### Changed

- Renamed package from `qcparse` -> `qccodec`.
- Removed `poetry` in favor of `hatchling` build system and `uv` for project management.
- 🚨 Refactored top-level `parse` function to a new signature `decode(program: str, calctype: CalcType, *, stdout: Optional[str] = None, directory: Optional[Union[str, Path]] = None, input_data: Optional[StructuredInputs] = None) -> StructureResults`.
- Changed parsers to no longer set data on a data collector object but to rather be pure functions returning their parsed data.
- Renamed `@parser` decorator to `@register` and accept `target` kwarg that tells the registry where to place the parsed data on the data collector object.
- `DataCollector` now inherits from `dict` rather than being a `SimpleNamespace`.
- Switched classes from pydantic `BaseModel` to `dataclasses` since I'm not using any advanced validation logic.

### Removed

- 🚨 `get_file_contents` function since we no longer pass filenames to top-level `decode` (formerly `parse`) function.
- 🚨 `parse_results` function previously kept for backwards compatibility.
- `pydantic` dependency.

## [0.7.5] - 2025-03-24

### Added

- TeraChem `parse_excited_states` function.

## [0.7.4] - 2025-02-25

### Changed

- CREST encoder now selects `min(os.cpu_count(), 16)` for `threads` if not set by the user.

## [0.7.3] - 2025-02-08

### Fixed

- Bug in parsing CREST's `g98.out` file for more than three frequencies.

## [0.7.2] - 2025-02-05

### Added

- Parse CREST's `numhess` g98.out file for frequency and normal mode displacement vectors.

## [0.7.1] - 2025-01-15

### Changed

- More flexibly defined `qcio` dependency version from `^0.11.8` to `>=0.12.1` to account for the missing `eval_type_backport` package.

## [0.7.0] - 2024-12-20

### Changed

- 🚨 Dropped Python 3.8 support.

### Removed

- `black` and `isort` in favor of `ruff`.

## [0.6.4] - 2024-10-01

### Added

- Encoders and parsers for CREST to support `energy`, `gradient`, `hessian`, and `optimization` calculations.

## [0.6.3] - 2024-09-12

### Added

- `parse_optimization_dir(...) -> OptimizationResults` for TeraChem.

## [0.6.2] - 2024-08-13

### Added

- `CREST` encoder and directory parser for conformer search output directories.

## [0.6.1] - 2024-08-08

### Added

- Program version parser for `CREST` stdout.

## [0.6.0] - 2024-06-10

### Changed

- Updated to `qcio 0.10.0` to use new `Structure` rather than `Molecule` nomenclature.

## [0.5.3] - 2024-04-04

### Changed

- TeraChem `parse_git_commit` updated to `parse_version_control_details` to accommodate older versions of TeraChem compiled from the `Hg` days.

### Removed

- TeraChem `parse_version` parser. It was unused given the switch to only parsing `SinglePointResults` objects and not `Provenance` objects as well. The `parse_version_string` function is used by `qcop` to get the version of the program. We do not need to set the version of the program at `SinglePointResults.extras.program_version` anymore.

## [0.5.2] - 2023-09-27

### Removed

- All input parsing details from the library.

### Added

- `encode` top level function and encoder for TeraChem input files.

### Changed

- Added `FileType.stdout` as default `filetype` argument to `parse` decorator to reduce boilerplate in parsers.

## [0.5.1] - 2023-09-19

### Changed

- Dropped Python dependency from `^3.8.1` to `^3.8`. Can't remember what older dependency required `3.8.1` but it's not needed anymore.

## [0.5.0] - 2023-08-31

### Changed

- Updated `pydantic` from `v1` -> `v2`.

## [0.4.1] - 2023-07-19

### Changed

- Updated `qcio` from `0.3.0` -> `0.4.0`.

## [0.4.0] - 2023-07-17

### Changed

- Updated to used `qcio>=0.3.0` flattened models and the `SinglePointResults`object.

## [0.3.2] - 2023-06-29

### Fixed

- Updated package description in pyproject.toml from TeraChem specific parsing and MolSSI to all QC packages and qcio.

## [0.3.1] - 2023-06-29

### Added

- Git commit parsing for TeraChem as part of version parsing

### Changed

- `qcio` `>=0.1.0` -> `>=0.2.0`

## [0.3.0] - 2023-06-28

### Changed

- Dropped support for `QCSchema` models and changed to [qcio](https://github.com/coltonbh/qcio) data models.
- `parse` function now raises `NotImplementedError` and the default use case is to use `parse_computed_prop` instead and ignore inputs and provenance data. This is the minimum spec since QC programs can be powered using structured inputs and [qcop](https://github.com/coltonbh/qcop). I may go back to parsing entire `SinglePointSuccess/FailedOutput` objects if use cases arise.

## [0.2.1] - 2023-03-25

### Changed

- Generalized `CUDA error:` regex to catch all CUDA errors.

## [0.2.0] - 2023-03-24

### Added

- `cli` interface for parsing TeraChem outputs from the command line.
- `parse_natoms`, `parse_nmo`, `parse_total_charge`, `parse_spin_multiplicity`

### Removed

- Removed Hessian matrix dimension checking from `parse_hessian`. Dimension validation is already done via `pydantic` on the `AtomicResult` object.

## [0.1.0] - 2023-03-23

### Added

- Basic parsers for energy, gradient, Hessian (frequencies) calculations.
- Can return either `AtomicResult` or `FailedOperation` objects depending on whether calculation succeeded or failed.
- Tests for all parsers and the main `parse` function.

[unreleased]: https://github.com/coltonbh/qccodec/compare/0.8.0...HEAD
[0.8.0]: https://github.com/coltonbh/qccodec/releases/tag/0.8.0
[0.7.8]: https://github.com/coltonbh/qccodec/releases/tag/0.7.8
[0.7.7]: https://github.com/coltonbh/qccodec/releases/tag/0.7.7
[0.7.6]: https://github.com/coltonbh/qccodec/releases/tag/0.7.6
[0.7.5]: https://github.com/coltonbh/qccodec/releases/tag/0.7.5
[0.7.4]: https://github.com/coltonbh/qccodec/releases/tag/0.7.4
[0.7.3]: https://github.com/coltonbh/qccodec/releases/tag/0.7.3
[0.7.2]: https://github.com/coltonbh/qccodec/releases/tag/0.7.2
[0.7.1]: https://github.com/coltonbh/qccodec/releases/tag/0.7.1
[0.7.0]: https://github.com/coltonbh/qccodec/releases/tag/0.7.0
[0.6.4]: https://github.com/coltonbh/qccodec/releases/tag/0.6.4
[0.6.3]: https://github.com/coltonbh/qccodec/releases/tag/0.6.3
[0.6.2]: https://github.com/coltonbh/qccodec/releases/tag/0.6.2
[0.6.1]: https://github.com/coltonbh/qccodec/releases/tag/0.6.1
[0.6.0]: https://github.com/coltonbh/qccodec/releases/tag/0.6.0
[0.5.3]: https://github.com/coltonbh/qccodec/releases/tag/0.5.3
[0.5.2]: https://github.com/coltonbh/qccodec/releases/tag/0.5.2
[0.5.1]: https://github.com/coltonbh/qccodec/releases/tag/0.5.1
[0.5.0]: https://github.com/coltonbh/qccodec/releases/tag/0.5.0
[0.4.1]: https://github.com/coltonbh/qccodec/releases/tag/0.4.1
[0.4.0]: https://github.com/coltonbh/qccodec/releases/tag/0.4.0
[0.3.2]: https://github.com/coltonbh/qccodec/releases/tag/0.3.2
[0.3.1]: https://github.com/coltonbh/qccodec/releases/tag/0.3.1
[0.3.0]: https://github.com/coltonbh/qccodec/releases/tag/0.3.0
[0.2.1]: https://github.com/coltonbh/qccodec/releases/tag/0.2.1
[0.2.0]: https://github.com/coltonbh/qccodec/releases/tag/0.2.0
[0.1.0]: https://github.com/coltonbh/qccodec/releases/tag/0.1.0
