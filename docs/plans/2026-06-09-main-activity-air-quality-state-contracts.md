---
title: Main Activity Air Quality State Contracts
type: reliability
status: completed
date: 2026-06-09
---

# Main Activity Air Quality State Contracts

## Problem Frame

`MainActivity` waited synchronously for `NetworkRequest`, then assumed the
returned JSON was non-null and included an `air_quality` value. A null response,
missing field, interrupted request, or execution failure could leave `state`
null and later crash the accelerometer display path through `state.equals(...)`.

## Scope Boundaries

- Keep the legacy synchronous `AsyncTask#get()` flow in place for this pass.
- Do not change location lookup, sensor rendering, Twitter/Fabric login, or the
  backend API response shape.
- Use the existing SDK-free Python contract checker as the baseline gate on
  hosts without Android SDK configuration.

## Implementation Units

### U1: Default Missing Air-Quality State Safely

Files:

- Modify `app/src/main/java/twitterdev/airquality/MainActivity.java`

Approach:

- Add a named default state for unavailable air-quality responses.
- Read `air_quality` through a helper that handles null JSON, missing fields,
  and blank values.
- Compare the displayed state with a constant using a null-safe equality check.
- Preserve thread interruption and replace raw stack traces with warning logs.

### U2: Preserve SDK-Free Guardrails

Files:

- Modify `scripts/check_airquality_android_contracts.py`

Approach:

- Assert that `MainActivity` keeps the default-state helper.
- Assert that accelerometer rendering uses null-safe state comparison.
- Assert that request failures no longer use `printStackTrace()`.

### U3: Document The Runtime Contract

Files:

- Modify `README.md`
- Modify `VISION.md`
- Modify `CHANGES.md`

Approach:

- Make the malformed-response fallback visible in maintenance docs.
- Keep modern networking and asynchronous UI refactors as separate follow-up
  work.

## Verification

- `make check`
- `git diff --check`

Gradle execution still requires a compatible Android SDK through `ANDROID_HOME`
or `local.properties`; the static contract remains the baseline verification on
hosts without that SDK.
