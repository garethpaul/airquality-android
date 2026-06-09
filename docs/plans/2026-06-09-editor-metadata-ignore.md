# AirQuality Editor Metadata Ignore

## Status: Completed

## Context

The legacy Android project still tracked IntelliJ `.idea` workspace files and
`.iml` module files. Those files are local editor metadata and can drift with
developer SDK paths or IDE preferences rather than AirQuality source behavior.

## Objectives

- Remove tracked `.idea` and `.iml` files.
- Ignore Android Studio, IntelliJ, and VS Code workspace metadata.
- Extend the SDK-free static checker so editor metadata cannot return
  unnoticed.
- Document the guardrail in README, SECURITY, VISION, and CHANGES.

## Work Completed

- Added `.idea/`, `.vscode/`, and `*.iml` ignore rules.
- Removed tracked AirQuality IDE metadata files.
- Added static checker coverage for ignore rules and tracked-file absence.

## Verification

- `python3 scripts/check_airquality_android_contracts.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
