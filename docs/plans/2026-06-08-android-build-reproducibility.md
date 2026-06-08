---
title: Android Build Reproducibility Baseline
type: chore
status: completed
date: 2026-06-08
---

# Android Build Reproducibility Baseline

## Summary

Raise the baseline for the legacy Android air-quality app by removing dynamic build-tool resolution, adding a small local unit-test seam, and documenting the exact local verification prerequisites. This pass keeps the app on its current Android Gradle Plugin, Gradle wrapper, Fabric, and Twitter SDK stack so it can be reviewed safely before a larger platform modernization.

---

## Problem Frame

The project is pinned to a 2015-era Android toolchain and depends on Fabric/Twitter artifacts that are no longer a modern Android baseline. A broad migration to current Gradle, AndroidX, and maintained SDKs is high risk without first making the existing build reproducible and documenting how to verify it.

---

## Requirements

- R1. Buildscript classpaths must avoid dynamic dependency versions so repeated builds resolve the same tooling.
- R2. The README must identify the legacy Android SDK, build-tools, and Gradle prerequisites needed to run the existing project.
- R3. The README must document the available local verification commands and explain the Android SDK configuration needed before running them.
- R4. A local JVM unit test must cover at least one pure behavior seam without requiring a device or emulator.
- R5. Duplicate manifest permissions should be removed when they are clearly redundant.
- R6. The plan must preserve follow-up work for a broader Android modernization pass instead of silently widening this change.
- R7. Local verification results must distinguish code failures from missing environment prerequisites.
- R8. CI must run lint, local JVM tests, and debug APK assembly on pushes and pull requests.

---

## Key Technical Decisions

- **Pin the Fabric Gradle plugin:** Replace `io.fabric.tools:gradle:1.+` with the currently resolved legacy plugin version to eliminate buildscript drift without changing the app runtime stack.
- **Gate Fabric plugin application behind local configuration:** Apply the Fabric plugin only when a `fabricApiKey` Gradle property exists so baseline Gradle configuration is not tied to an empty checked-in API key.
- **Extract a pure URL builder:** Pull the air-quality endpoint string construction into `NetworkRequest.buildUrl` so local JVM tests can cover request composition without Android runtime dependencies.
- **Document before migrating:** Add a README baseline for setup and verification because the repository currently has no usable project instructions.
- **Avoid toolchain jumps in this pass:** Updating Gradle 2.2.1, Android Gradle Plugin 1.2.3, compile SDK 22, or Fabric/Twitter SDKs belongs in a dedicated migration with emulator or device verification.
- **Keep legacy lint usable:** Suppress only the obsolete lint API database error emitted by Android Gradle Plugin 1.2.3 with current SDK command-line installs; do not disable lint globally.

---

## Scope Boundaries

- This pass does not migrate to AndroidX.
- This pass does not replace Fabric or Twitter login.
- This pass does not update compile SDK, target SDK, Gradle wrapper, or Android Gradle Plugin versions.
- This pass does not change runtime app behavior.

---

## Implementation Units

### U1. Pin Dynamic Build Tooling

- **Goal:** Make Gradle buildscript dependency resolution deterministic for the existing Fabric plugin and avoid applying Fabric when local API-key configuration is absent.
- **Files:** `app/build.gradle`
- **Patterns:** Keep the existing `buildscript` structure; use a property guard around the Fabric plugin application.
- **Test Scenarios:**
  - `app/build.gradle` no longer contains `io.fabric.tools:gradle:1.+`.
  - `app/build.gradle` includes `testCompile 'junit:junit:4.12'` for local JVM tests.
  - The Fabric plugin is applied only when `fabricApiKey` is configured.
  - Gradle configuration starts and fails only if Android SDK configuration is missing.
- **Verification:** `./gradlew tasks --no-daemon`

### U2. Add a Local Unit-Test Seam

- **Goal:** Cover air-quality request URL construction without Android runtime, network, or emulator dependencies.
- **Files:** `app/src/main/java/twitterdev/airquality/NetworkRequest.java`, `app/src/test/java/twitterdev/airquality/NetworkRequestTest.java`
- **Patterns:** Extract a pure static helper and leave `doInBackground` behavior unchanged.
- **Test Scenarios:**
  - `NetworkRequestTest` verifies latitude and longitude are included in the backend URL in the expected query parameter order.
- **Verification:** `./gradlew test --no-daemon`

### U3. Clean Redundant Manifest Configuration

- **Goal:** Remove redundant manifest entries that add noise without changing permissions.
- **Files:** `app/src/main/AndroidManifest.xml`
- **Patterns:** Delete only exact duplicate permission declarations.
- **Test Scenarios:**
  - `AndroidManifest.xml` declares `android.permission.ACCESS_FINE_LOCATION` once.
- **Verification:** Manual manifest review and `./gradlew tasks --no-daemon`

### U4. Document Legacy Setup and Verification

- **Goal:** Make the repository usable to a future maintainer before deeper modernization work.
- **Files:** `README.md`
- **Patterns:** Short setup sections with command blocks; call out legacy prerequisites and current verification limits.
- **Test Scenarios:**
  - README lists `ANDROID_HOME` or `local.properties` as required SDK configuration.
  - README lists `./gradlew tasks --no-daemon`, `./gradlew test --no-daemon`, and `./gradlew assembleDebug --no-daemon` as verification commands.
  - README documents the optional `fabricApiKey` property for Fabric-specific build behavior.
  - README records that broader dependency and platform upgrades are deferred follow-up work.
- **Verification:** Manual README review and `./gradlew tasks --no-daemon`

---

## Risks & Dependencies

- The local environment must provide an Android SDK path through `ANDROID_HOME` or `local.properties`; without it, Gradle fails during Android plugin configuration before task execution.
- JCenter, Fabric, Twitter SDK 1.x, Gradle 2.2.1, and Android Gradle Plugin 1.2.3 are all legacy dependencies and should be handled in a separate migration plan with runtime testing.
- The app uses deprecated Apache HTTP APIs and synchronous `AsyncTask#get()` behavior; those are runtime modernization targets outside this reproducibility baseline.

---

## Sources / Research

- `app/build.gradle` defines Fabric buildscript tooling and app dependencies.
- `build.gradle` defines Android Gradle Plugin 1.2.3 and JCenter repositories.
- `app/build.gradle` now uses Android build-tools 24.0.3 to avoid the 32-bit `aapt` loader failure from older build-tools on the current Linux host.
- `lint.xml` ignores the legacy lint API database error because current SDK command-line installs no longer ship `platform-tools/api/api-versions.xml`.
- `gradle/wrapper/gradle-wrapper.properties` pins Gradle 2.2.1.
- Local verification succeeded after installing the Android SDK command-line tools, platform 22, build-tools 24.0.3, and the Android support repository.
