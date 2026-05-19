# v0.2.0 - May 2026
Update to use onyx analysis tables 0.5.1.

## Changed
- Updated onyx query function to include the versions from onyx using the onyx analysis helper
function.
- thresholds are now embedded in a dict with key "thresholds" in the methods.
- updated precommit config file.
- made versioning dynamic in the pyproject.toml and removed ruff version dependency.
- added version dependency for onyx analysis helper.

## Added
- Tool versions - just the package version is added.
- Added onyx versions and tool versions to the analysis table using the onnyx analysis helper
methods.
- unit tests, including end-to-end.
- CL option to print version of QC metrics tool.
- gitignore

## Fixed:
- typehints
