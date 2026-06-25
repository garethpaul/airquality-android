# MainActivity Location Log Redaction

Status: Completed

## Context

`MainActivity.getLocation()` catches provider, permission, and platform
failures and passes the caught exception to Android's three-argument `Log.w`
overload. The throwable can expose provider state, permission details, device
configuration, and a stack trace in logcat even though the activity already
recovers by returning the current location value.

The adjacent `NetworkRequest` failure path is redacted, but the portable
checker does not enforce the same boundary for location acquisition.

## Requirements

- **R1:** Keep the stable location failure category without passing caught
  exceptions or exception-derived text to Android logs.
- **R2:** Preserve `getLocation()` provider checks, update registration,
  last-known-location behavior, fallback return value, and activity startup.
- **R3:** Strengthen the SDK-free checker to reject throwable logging,
  exception messages, stringified exceptions, or raw stack traces in
  `MainActivity`.
- **R4:** Record the location privacy boundary and truthful local, mutation,
  hosted, and platform verification evidence.

## Implementation Units

### U1: Redact Location Failure Logs

**File:** `app/src/main/java/twitterdev/airquality/MainActivity.java`

Replace the throwable-bearing warning with the existing stable two-argument
message. Do not change catch scope, return behavior, provider selection, or
location update registration.

### U2: Enforce The Location Log Contract

**File:** `scripts/check_airquality_android_contracts.py`

Require the exact generic warning and reject throwable or exception-derived
logging in `MainActivity`. Add this plan to the canonical plan inventory.

### U3: Document And Verify The Boundary

**Files:** `README.md`, `SECURITY.md`, `CHANGES.md`,
`docs/plans/2026-06-13-location-log-redaction.md`

Document the privacy behavior and record actual focused, full, external,
mutation, and hosted evidence after execution.

## Test Scenarios

- Restoring the caught exception argument to the location warning fails the
  checker.
- Logging `e.getMessage()`, `e.toString()`, or `printStackTrace()` in
  `MainActivity` fails the checker.
- Removing the generic location failure category fails the checker.
- Existing location-manager, lifecycle, sensor, network, build, lint, and
  wrapper contracts remain green.

## Scope Boundaries

- Do not change Android permissions, provider choice, update intervals,
  location precision, or network requests.
- Do not remove the location failure category or add location values to logs.
- Do not claim emulator/device logcat behavior without an Android runtime.

## Verification

- The focused source contract passed with exactly one generic location warning
  and no throwable, exception-message, stringified-exception, or raw-stack
  logging in `MainActivity`.
- Isolated `make check` passed Python compilation and all SDK-free repository
  contracts. Gradle truthfully skipped because no Android SDK is configured.
- Six hostile mutations were rejected: restoring the throwable overload,
  logging `getMessage`, restoring `printStackTrace`, removing the failure
  category, removing security guidance, and reverting plan completion.
- Device/emulator logcat, Android compilation, lint, unit tests, and APK
  assembly remain hosted or platform validation boundaries.

## Sources

- Android `Log` API reference:
  https://developer.android.com/reference/android/util/Log
- Android log information disclosure guidance:
  https://developer.android.com/privacy-and-security/risks/log-info-disclosure
