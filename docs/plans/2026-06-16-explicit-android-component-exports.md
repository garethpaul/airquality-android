# Explicit Android Component Exports

Status: Planned

## Problem

Both activities declare intent filters without explicit `android:exported`
ownership. `LoginActivity` is the public MAIN/LAUNCHER entry point, while
`MainActivity` is reached only through an explicit in-app intent. The latter's
legacy custom action therefore exposes an internal activity implicitly and is
reported by CodeQL as high-severity
`java/android/implicitly-exported-component` alert 1.

## Priorities

1. P0: Make the launcher activity explicitly exported and the internal main
   activity explicitly non-exported.
2. P0: Preserve app launch and the explicit Login-to-Main transition.
3. P1: Enforce source and merged-manifest ownership with parsed, mutation-
   sensitive contracts.

## Requirements

1. `.LoginActivity` must declare `android:exported="true"` and retain exactly
   one MAIN/LAUNCHER filter.
2. `.MainActivity` must declare `android:exported="false"` and remain reachable
   through the existing explicit Java intent.
3. No unrelated activity or component may satisfy either ownership contract.
4. Source and available merged manifests must preserve the same export policy.
5. Android unit tests, lint, assembly, SDK-free checks, maintained guidance,
   and this plan must record truthful completed evidence.

## Implementation Units

### U1: Declare Component Ownership

**File:** `app/src/main/AndroidManifest.xml`

Set explicit exports on both activities. Keep launcher routing and the existing
internal explicit transition unchanged.

### U2: Add Parsed Manifest Contracts

**Files:** `scripts/check_airquality_android_contracts.py` and focused test
fixtures or helpers as needed.

Parse activity declarations by fully qualified name, bind export values to the
correct activities, require the launcher filter only on `LoginActivity`, and
validate merged manifests when Android build outputs are available.

### U3: Preserve Guidance And Evidence

**Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`, and this plan.

Document public launcher ownership, internal activity isolation, CodeQL alert
intent, completed validation, and device-testing limits.

## Test Scenarios

- The source manifest has exactly one exported launcher activity.
- `LoginActivity` owns MAIN and LAUNCHER and is exported `true`.
- `MainActivity` is exported `false` and the Java transition remains explicit.
- Missing, false launcher, true internal, unrelated, duplicate, or detached
  declarations fail the portable contract.
- Debug and release merged manifests preserve the same policy when built.
- Repository and external-directory `make check` remain green.

## Scope Boundaries

- Do not change login, TwitterKit, Fabric, location, sensor, network, or UI
  behavior.
- Do not add deep links or new external entry points.
- Do not change Gradle dependencies, SDK levels, workflows, or signing.
- Emulator, physical-device, live backend, location-provider, and sensor
  behavior remain outside local validation.

## Verification

- Run the SDK-free parsed source-manifest contract first.
- Run repository and external-directory `make check` with the configured JDK
  and Android SDK.
- Reject isolated hostile mutations covering missing, reversed, unrelated,
  duplicate, detached-filter, guidance, and plan-status cases.
- Audit exact paths, generated Gradle/build artifacts, credentials, dependency
  and workflow drift, conflict markers, and whitespace before commit.
