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
  reads, added a five-minute timeout, and enabled manual dispatch.
- Extended the Android contract checker and docs so the hosted CI path stays
  visible.

The workflow intentionally clears Android SDK environment variables. A modern
Android build requires a separate migration from Gradle 2.2.1, Android Gradle
Plugin 1.2.3, JCenter, Fabric, and Twitter Kit before hosted compilation can be
treated as a reliable gate.

## Verification

- `make check`
