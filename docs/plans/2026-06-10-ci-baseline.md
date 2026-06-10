# CI Baseline

Status: Completed

## Context

The repository had local static and optional Gradle verification gates for the
legacy Android sample, but no hosted workflow ran them for pushes and pull
requests.

## Changes

- Added a GitHub Actions workflow that runs the SDK-free `make check` baseline
  on Python 3.10, 3.12, and 3.14.
- Pinned actions to immutable revisions, restricted permissions to repository
  reads, disabled persisted checkout credentials, selected Ubuntu 24.04, added
  a five-minute timeout, and enabled manual dispatch.
- Added an explicit `SKIP_GRADLE=1` path so a force-added `local.properties`
  cannot turn hosted static verification into an accidental Android build.
- Required immutable action revisions across every hosted workflow and rejected
  tracked `local.properties`.
- Extended the Android contract checker to enforce workflow structure without
  coupling executable checks to documentation prose.

The workflow explicitly sets `SKIP_GRADLE=1`. A modern Android build requires a
separate migration from Gradle 2.2.1, Android Gradle Plugin 1.2.3, JCenter,
Fabric, and Twitter Kit before hosted compilation can be treated as a reliable
gate.

## Verification

- `make check`
- `SKIP_GRADLE=1 make check` with a fake `local.properties`
- Negative mutations for missing triggers, mutable action tags (including in
  additional workflows), tracked `local.properties`, and removed skip control
