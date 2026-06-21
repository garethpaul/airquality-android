# AirQuality Android System Make Boundary

Status: Completed

## Problem

Hosted and documented verification invoked `make` through `PATH`. The Makefile
also treated startup files as rejectable repository input even though GNU Make
loads `MAKEFILES` before the repository Makefile can inspect it. Unsafe
execution modes, later recipes, shell changes, and target-specific Python or
Gradle replacement could also redirect or suppress the repository checks.

## Work Completed

- Bound both GitHub Actions jobs and contributor verification to
  `/bin/sh scripts/run-make.sh check`, which clears inherited `MAKEFILES`,
  `MAKEFLAGS`, `MFLAGS`, `MAKEOVERRIDES`, and `GNUMAKEFLAGS` before fixed
  `/usr/bin/make --no-print-directory -f <checkout>/Makefile`.
- Allowed only the workflow `check` target and harness-only `lint` target;
  options, assignments, extra makefiles, extra arguments, and unknown targets
  fail before Make starts.
- Resolved the actual entrypoint through at most 40 relative or absolute
  symbolic links with fixed `/usr/bin/readlink`, `/usr/bin/dirname`, and
  `/bin/pwd`, preventing `PATH` substitution and external symlink directories
  from selecting a different repository root.
- Froze `/bin/sh`, the canonical repository root, and literal Python and Gradle
  selections across every public target.
- Defined pre-parse startup programs as caller authority. The canonical entry
  point excludes inherited Make startup and option channels before parsing;
  the Makefile retains fail-closed checks for values still visible afterward.
- Rejected replaced Makefile lists, raw Make-syntax executable values, later
  single-colon recipes, and non-executing or error-ignoring modes.
- Added `scripts/test-makefile-root.sh` to the default verification gate.
- Extended the existing exact workflow and repository static contracts.

## Verification

- Run `/bin/sh scripts/run-make.sh check` from the repository root.
- Run `/bin/sh <checkout>/scripts/run-make.sh check` from an unrelated directory.
- Run the entrypoint with a hostile `dirname` earlier on `PATH` and through an
  external symbolic link; both must still select the physical checkout.
- Run `scripts/test-makefile-root.sh` without an Android SDK.
- Let the hosted Android job exercise the same boundary with API 22 and Java 8.

## Scope Boundary

This change does not alter application behavior, Android dependencies,
permissions, credentials, backend requests, or device-data handling. Direct
Make startup programs, extra makefiles, option strings, and assignments remain
caller authority only when a caller bypasses the canonical entrypoint. The
hosted command uses the canonical entrypoint and supplies none of them.
