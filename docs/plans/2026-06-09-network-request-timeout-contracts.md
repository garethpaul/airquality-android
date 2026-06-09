---
title: Network Request Timeout Contracts
type: reliability
status: completed
date: 2026-06-09
---

# Network Request Timeout Contracts

## Problem Frame

`NetworkRequest.doInBackground` configures connection and socket timeouts on an
`HttpParams` instance, but the `DefaultHttpClient` is built with a different
parameter object. The backend request can therefore ignore the intended timeout
settings and wait longer than the legacy UI flow expects.

## Scope Boundaries

- Keep the legacy `AsyncTask`, Apache HTTP, and backend endpoint in place.
- Do not change location lookup, Twitter/Fabric login, Gradle, or Android SDK
  versions in this pass.
- Avoid broad networking modernization; this pass only ensures the existing
  timeout settings are applied to the executing client.

## Implementation Units

### U1: Apply Timeouts To The Executing Client

Files:

- Modify `app/src/main/java/twitterdev/airquality/NetworkRequest.java`

Approach:

- Keep a named timeout constant for the request path.
- Configure connection and socket timeouts on one `HttpParams` instance.
- Construct `DefaultHttpClient` with that same timeout-configured instance.
- Remove the unused request parameter object that previously hid the timeout
  wiring bug.

### U2: Preserve SDK-Free Guardrails

Files:

- Modify `scripts/check_airquality_android_contracts.py`

Approach:

- Assert that `NetworkRequest` keeps a named timeout constant.
- Assert that both timeout setters use the `httpParams` object.
- Assert that `DefaultHttpClient` is constructed with `httpParams`, not the old
  unused parameter object.

### U3: Document The Operational Contract

Files:

- Modify `README.md`
- Modify `VISION.md`
- Modify `CHANGES.md`

Approach:

- Make the bounded backend request behavior visible in maintenance docs.
- Keep future networking modernization scoped separately from this guardrail.

## Verification

- `make check`
- `git diff --check`

Gradle execution still requires a compatible Android SDK through `ANDROID_HOME`
or `local.properties`; the static contract remains the baseline verification on
hosts without that SDK.
