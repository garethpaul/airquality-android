---
title: Gradle Wrapper Verification
date: 2026-06-12
status: completed
execution: code
---

# Gradle Wrapper Verification

## Summary

Add a checksum-capable generated Gradle Wrapper bootstrap while preserving the
air-quality sample's Gradle 2.2.1, Java 8, API 22, network, location, sensor,
and request-lifecycle behavior. Keep the existing SDK-free Python matrix and
add a distinct hosted Android compatibility job.

## Problem Frame

The repository's local Android gate is characterized, but its legacy wrapper
downloads Gradle 2.2.1 without archive verification and the static contracts
do not authenticate the checked-in wrapper JAR or launchers. Canonical CI
deliberately clears Android SDK variables, so a wrapper-only change could pass
hosted checks without executing the Android build.

## Requirements

- **R1:** Continue executing `gradle-2.2.1-all.zip` under Java 8 without
  changing Android Gradle Plugin 1.2.3, compile/target SDK 22, build-tools
  24.0.3, dependencies, permissions, credentials, or app behavior.
- **R2:** Pin Gradle's official Gradle 2.2.1 all-distribution SHA-256,
  `1d7c28b3731906fd1b2955946c1d052303881585fc14baedd675e4cf2bc1ecab`.
- **R3:** Regenerate `gradlew`, `gradlew.bat`, and `gradle-wrapper.jar` with
  official Gradle 8.14.5 tooling and verify its published wrapper JAR SHA-256,
  `7d3a4ac4de1c32b59bc6a4eb8ecb8e612ccd0cf1ae1e99f66902da64df296172`.
- **R4:** Extend the SDK-free Python contracts to reject wrapper URL,
  checksum, JAR, launcher, documentation, workflow, and completion-evidence
  drift.
- **R5:** Preserve all three SDK-free Python matrix jobs and add a bounded,
  read-only Java 8/API 22 job that runs the complete `make check` gate.
- **R6:** Pass the complete local and final exact-head hosted gates before
  tracker reconciliation.

## Key Technical Decisions

- Use Gradle 8.14.5 only to generate the bootstrap; retain the legacy Gradle
  runtime required by Android Gradle Plugin 1.2.3.
- Authenticate the downloaded distribution and exact checked-in wrapper
  artifacts as separate trust boundaries.
- Keep the existing Python matrix unchanged and add one Android job rather
  than multiplying SDK installation across three Python versions.
- State the online boundary explicitly: checksums authenticate expected bytes
  but do not make an uncached build offline-reproducible.

## Scope Boundaries

In scope: the four wrapper files, static contracts, canonical workflow,
repository guidance, and local/hosted evidence. Deferred: Gradle/Android
runtime modernization, dependencies, credentials, application code, UI,
network behavior, location behavior, sensors, and emulator/device testing.

## Implementation Units

### U1. Verified Wrapper Bootstrap

Generate the wrapper with official Gradle 8.14.5 tooling, retain Gradle 2.2.1,
and prove a fresh Java 8 bootstrap accepts the official archive and rejects an
incorrect checksum.

### U2. Static Contracts And Documentation

Add exact wrapper properties, JAR, launcher, documentation, workflow, and
completed-plan contracts to the existing Python checker.

### U3. Local And Hosted Compatibility

Run `make check` from the repository and an external working directory,
exercise focused hostile mutations, preserve the Python matrix, and require
the new hosted Android job plus CodeQL to pass on the final exact head.

## Risks And Mitigations

- Use a fresh temporary Gradle user home so cached archives cannot hide
  checksum behavior.
- Verify `./gradlew --version` under Java 8 before project tasks.
- Keep the Android job independent from the existing Python matrix so current
  branch-protection contexts remain available.
- Reject application and build-file changes in this unit.

## Sources

- [Gradle Wrapper documentation](https://docs.gradle.org/current/userguide/gradle_wrapper.html)
- [Gradle security best practices](https://docs.gradle.org/current/userguide/best_practices_security.html)
- [Gradle 2.2.1 all-distribution checksum](https://services.gradle.org/distributions/gradle-2.2.1-all.zip.sha256)
- [Gradle 8.14.5 wrapper JAR checksum](https://services.gradle.org/distributions/gradle-8.14.5-wrapper.jar.sha256)

## Work Completed

- Regenerated all four wrapper files with official Gradle 8.14.5 tooling while
  retaining the Gradle 2.2.1 all distribution and existing Android runtime.
- Added exact wrapper properties, JAR, launcher, workflow, documentation, and
  completed-plan contracts to the dependency-free Python checker.
- Preserved the three-version SDK-free matrix and added one bounded Java 8/API
  22 Android job with credential-free checkout.

## Verification Completed

- A fresh temporary Gradle user home downloaded the official distribution and
  reported Gradle 2.2.1 on Corretto Java 8 (`1.8.0_482`).
- A disposable wrapper with an incorrect checksum was rejected before Gradle
  execution and reported the official archive checksum.
- SDK-backed `make check` passed with the documented target-SDK lint warning,
  six tests on each build variant, and debug assembly under Java 8/API 22 from
  the repository and an external working directory.
- Focused hostile mutations rejected wrapper properties, JAR, launcher,
  workflow, documentation, and incomplete plan evidence.
- Python compilation, `git diff --check`, and workflow structure checks passed.

## Hosted Verification

- On implementation head `6b5a6fbca8bdbd1455a5763bc468c91d3b28729b`,
  pull-request `Check` run `27440457696` passed the Python 3.10, 3.12, and
  3.14 matrix plus the Java 8/API 22 Android job.
- CodeQL run `27440455310` passed the actions, Python, and java-kotlin analyzers
  on the same implementation head.
- PR #5 was open and mergeable at that head, with branch protection correctly
  requiring review. The final evidence-only commit must rerun all seven jobs
  before tracker reconciliation.
