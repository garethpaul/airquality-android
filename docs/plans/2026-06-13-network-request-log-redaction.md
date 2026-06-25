# NetworkRequest Log Redaction

Status: Completed

## Context

`NetworkRequest` currently calls the three-argument `Log.w` overload with each
caught HTTP, I/O, JSON, and parameter exception. Android documents that this
overload logs the exception. Those dependency exceptions can include the
coordinate-bearing request URL, provider status text, response details, and a
stack trace in logcat even though the user-facing state is already generic.

The portable checker claims request failures are logged without raw stack
traces, but it only checks the message prefix and therefore accepts the
throwable overload that produces them.

## Requirements

- **R1:** Log stable warning messages without passing caught throwables for
  request protocol, I/O, JSON, and invalid-parameter failures.
- **R2:** Keep latitude, longitude, request URLs, provider response details,
  exception messages, and stack traces out of NetworkRequest logs.
- **R3:** Preserve null failure results, timeouts, response-size limits,
  connection shutdown, URL validation, JSON parsing, and activity state behavior.
- **R4:** Strengthen the SDK-free checker to reject throwable logging,
  `printStackTrace`, exception-message concatenation, or removal of any generic
  failure message.
- **R5:** Record the privacy boundary and completed verification in repository
  guidance and the canonical plan inventory.

## Implementation Units

### U1: Remove Throwable Logging

**Files:** `app/src/main/java/twitterdev/airquality/NetworkRequest.java`

Replace each warning call that includes a caught exception with the existing
stable two-argument warning message. Do not add exception-derived text or
change catch, cleanup, or return behavior.

### U2: Enforce Redacted Failure Logs

**Files:** `scripts/check_airquality_android_contracts.py`

Require the exact generic warning calls and reject any NetworkRequest log call
that includes a throwable, `getMessage`, `toString`, URL, coordinates, or raw
stack trace. Add the completed plan to the canonical inventory.

### U3: Document And Verify The Boundary

**Files:** `README.md`, `SECURITY.md`, `CHANGES.md`,
`docs/plans/2026-06-13-network-request-log-redaction.md`

Document that network failures retain diagnostic categories without logging
dependency exceptions or location-bearing request details. Record focused,
full, mutation, and hosted verification after execution.

## Test Scenarios

- Restoring a throwable argument to a request-failure warning fails the checker.
- Logging `e.getMessage()`, `e.toString()`, or `printStackTrace()` fails the checker.
- Removing the protocol/I/O, invalid-JSON, or invalid-parameter generic message
  fails the checker.
- Existing URL, timeout, response-size, lifecycle, sensor, build, lint, and
  wrapper verification remain green.

## Scope Boundaries

- Do not remove failure categories or make successful requests less observable.
- Do not change the endpoint, coordinates, response parsing, retries,
  dependencies, target SDK, or legacy Apache HTTP implementation in this task.
- Do not claim device logcat behavior was exercised without an emulator or device.

## Verification

- The focused source assertion passed with exactly four generic warning calls
  and no throwable overloads or exception-derived log text.
- Seven focused hostile mutations were rejected: restoring a throwable
  argument, logging `getMessage`, restoring `printStackTrace`, adding a request
  URL log, removing the parameter category, removing security guidance, and
  removing the canonical plan.
- Local `make check` passed Python compilation and the SDK-free checker. It
  truthfully skipped Gradle because `ANDROID_HOME` is not configured.
- External-directory checker execution, Python compilation, workflow YAML
  parsing, secret scanning, and `git diff --check` passed.
- Android unit, lint, debug/release compilation, APK assembly, and device logcat
  behavior remain hosted or platform validation boundaries.

## Sources

- Android `Log` API reference:
  https://developer.android.com/reference/android/util/Log
- Android log information disclosure guidance:
  https://developer.android.com/privacy-and-security/risks/log-info-disclosure
