# MainActivity Air-Quality Request Lifecycle

Status: Completed

## Context

`MainActivity` starts an anonymous `NetworkRequest` that retains the activity
until its bounded HTTP work finishes. The activity does not retain or cancel
that task, and its completion callback can still update activity state while
the screen is finishing or already destroyed.

## Changes

- Retain the active air-quality request as an activity field.
- Ignore completion callbacks when the request is cancelled or the activity is
  finishing or destroyed.
- Cancel and clear the active request during `onDestroy`.
- Preserve nonblocking startup, the unknown-state fallback, timeout handling,
  response limits, and existing sensor lifecycle behavior.
- Extend the SDK-free contract checker and project documentation with the
  request lifecycle requirements.

## Verification

- `make check` passed with Amazon Corretto 8 and the configured Android SDK.
  Gradle compiled debug and release Java sources, ran all six unit tests for
  both variants, ran Android lint, and assembled the debug APK.
- Android lint completed with no errors and one existing `OldTargetApi`
  warning for the intentionally preserved API 22 compatibility baseline.
- The SDK-free contract checker passed on Python 3 and rejected mutations that
  removed the callback identity guard, teardown-state guard, request
  cancellation, or completed-plan evidence.
- `git diff --check` passed.
