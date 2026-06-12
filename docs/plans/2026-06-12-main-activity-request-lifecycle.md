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

- `make lint`
- `make test`
- `make build`
- `make check`
- Static mutation checks for callback guards and `onDestroy` cancellation
- `git diff --check`
