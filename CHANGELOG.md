# Changelog

## v0.2.2
Added devscape and bumped onyx analysis helper version.

### Changed:
- onyx analysis helper version changed to v0.6.5
- added devscape as CL server option.

### Fixed:
- 'v' added to version used in unit test to match updated onyx analysis helper functionality.

---
---

## v0.2.1
Now uses Onyx Analysis Helper version v0.6.0

### Changes:
- onyx analysis helper dependency bumped to 0.6.0 in pyproject.toml.

---
---

## v0.2.0 - May 2026
Update to use onyx analysis tables 0.5.1.

### Changed
- Updated onyx query function to include the versions from onyx using the onyx analysis helper
function.
- thresholds are now embedded in a dict with key "thresholds" in the methods.
- updated precommit config file.
- made versioning dynamic in the pyproject.toml and removed ruff version dependency.
- added version dependency for onyx analysis helper.

### Added
- Tool versions - just the package version is added.
- Added onyx versions and tool versions to the analysis table using the onnyx analysis helper
methods.
- unit tests, including end-to-end.
- CL option to print version of QC metrics tool.
- gitignore

### Fixed:
- typehints
