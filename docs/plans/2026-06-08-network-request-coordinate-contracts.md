---
title: Android Network Request Coordinate Contracts
type: test
status: completed
date: 2026-06-08
---

# Android Network Request Coordinate Contracts

## Problem Frame

The first Android pass introduced a pure `NetworkRequest.buildUrl` seam, but it
only verifies happy-path concatenation. The helper still accepts missing,
non-numeric, non-finite, or out-of-range coordinates before constructing the
backend request URL.

## Scope Boundaries

- Preserve the existing backend endpoint and query parameter order.
- Keep this pass limited to the pure URL-construction seam.
- Do not migrate Apache HTTP, AsyncTask, Fabric, Twitter, Gradle, or Android SDK
  versions here.

## Implementation Units

### U1: Expand URL Tests

Files:

- Modify `app/src/test/java/twitterdev/airquality/NetworkRequestTest.java`

Approach:

- Cover trimming, missing inputs, non-numeric values, non-finite values, and
  out-of-range latitude/longitude values.

### U2: Validate Coordinates In The URL Builder

Files:

- Modify `app/src/main/java/twitterdev/airquality/NetworkRequest.java`

Approach:

- Normalize coordinate strings before URL construction.
- Reject invalid coordinates with `IllegalArgumentException`.
- URL-encode validated coordinate query values.

### U3: SDK-Free Static Contracts

Files:

- Create `scripts/check_airquality_android_contracts.py`
- Create `Makefile`

Approach:

- Verify coordinate validation, URL encoding, manifest permission uniqueness,
  empty checked-in credentials, and pinned Fabric tooling without requiring an
  Android SDK.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`

Gradle verification still requires an Android SDK through `ANDROID_HOME` or
`local.properties`; `make check` skips Gradle on hosts where the SDK is not
configured.
