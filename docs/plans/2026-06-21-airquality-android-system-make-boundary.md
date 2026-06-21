# AirQuality Android System Make Boundary

Status: Completed

## Problem

Hosted and documented verification invoked `make` through `PATH`. The Makefile
also allowed startup files, unsafe execution modes, later recipes, shell
changes, and target-specific Python or Gradle replacement to redirect or
suppress the repository checks.

## Work Completed

- Bound both GitHub Actions jobs and contributor verification to
  `/usr/bin/make`.
- Froze `/bin/sh`, the canonical repository root, and literal Python and Gradle
  selections across every public target.
- Rejected startup files, replaced Makefile lists, raw Make-syntax executable
  values, later single-colon recipes, and non-executing or error-ignoring
  modes.
- Added `scripts/test-makefile-root.sh` to the default verification gate.
- Extended the existing exact workflow and repository static contracts.

## Verification

- Run `/usr/bin/make check` from the repository root.
- Run `/usr/bin/make -f <checkout>/Makefile check` from an unrelated directory.
- Run `scripts/test-makefile-root.sh` without an Android SDK.
- Let the hosted Android job exercise the same boundary with API 22 and Java 8.

## Scope Boundary

This change does not alter application behavior, Android dependencies,
permissions, credentials, backend requests, or device-data handling. Explicit
literal Python and Gradle paths remain supported caller authority.
