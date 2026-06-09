---
title: Network Request Async Parameter Contracts
type: reliability
status: completed
date: 2026-06-09
---

# Network Request Async Parameter Contracts

## Problem Frame

`NetworkRequest.doInBackground` reads the `AsyncTask` parameter array directly,
then catches every `Throwable` and returns `null`. Missing, short, or malformed
request parameters are therefore indistinguishable from network or JSON failures,
and they can fail before the already-tested URL builder contract is used.

## Scope Boundaries

- Keep the backend endpoint and query format unchanged.
- Keep the legacy `AsyncTask` and Apache HTTP implementation in place.
- Do not change activity lifecycle, location lookup, Fabric/Twitter login, or
  Gradle/SDK versions in this pass.

## Implementation Units

### U1: Add A Pure Async Parameter Helper

Files:

- Modify `app/src/main/java/twitterdev/airquality/NetworkRequest.java`
- Modify `app/src/test/java/twitterdev/airquality/NetworkRequestTest.java`

Approach:

- Add `NetworkRequest.buildUrlFromParams(String... params)`.
- Reject missing or short parameter arrays before URL construction.
- Delegate coordinate validation to `buildUrl`.
- Cover the helper with local JVM tests.

### U2: Route Background Requests Through The Helper

Files:

- Modify `app/src/main/java/twitterdev/airquality/NetworkRequest.java`

Approach:

- Build the request URL through the pure helper.
- Replace the empty broad `Throwable` catch with explicit failure categories and
  non-PII warning logs.

### U3: Preserve SDK-Free Guardrails

Files:

- Modify `scripts/check_airquality_android_contracts.py`

Approach:

- Assert that the helper exists, is covered by tests, and is used by
  `doInBackground`.
- Assert that the empty `Throwable` catch does not return.

## Verification

- `make check`
- `git diff --check`

Gradle test execution remains dependent on a configured Android SDK via
`ANDROID_HOME` or `local.properties`; the SDK-free contract check is the
baseline verification on hosts without that configuration.
