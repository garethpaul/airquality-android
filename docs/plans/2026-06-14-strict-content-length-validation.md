# Strict Backend Content-Length Validation

Status: Completed

## Context

`NetworkRequest.readResponseBody` checks Apache's parsed entity length before
streaming, but it does not validate the raw `Content-Length` response field.
Malformed, signed, whitespace-padded, overflowed, or duplicated values can
therefore bypass the declared-length boundary and rely only on the streamed
1 MiB limit.

## Scope

- Permit an absent `Content-Length` and preserve streamed size enforcement.
- When supplied, require exactly one non-empty ASCII decimal value.
- Reject numeric overflow and values above 1 MiB before opening the body.
- Preserve status, JSON media-type, redirect, strict UTF-8, logging, and
  connection-cleanup behavior.
- Add focused JVM tests, mutation-sensitive portable contracts, and
  maintenance documentation.

## Implementation Units

### 1. Parse the field deterministically

Files:

- `app/src/main/java/twitterdev/airquality/NetworkRequest.java`
- `app/src/test/java/twitterdev/airquality/NetworkRequestTest.java`

Add a package-visible parser that accepts supplied ASCII decimal digits,
detects `long` overflow without permissive Java number syntax, and returns the
parsed length. Cover zero, the exact response limit, `Long.MAX_VALUE`, null,
signs, whitespace, separators, non-ASCII digits, empty values, and overflow.

### 2. Enforce one header before body access

Files:

- `app/src/main/java/twitterdev/airquality/NetworkRequest.java`

Reject duplicate raw fields, validate a supplied field before opening the
entity stream, retain Apache's entity length only when no raw field exists,
and keep unknown length `-1` compatible with streamed enforcement.

### 3. Protect and document the boundary

Files:

- `scripts/check_airquality_android_contracts.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-14-strict-content-length-validation.md`

Require parser syntax, duplicate rejection, validation ordering, focused tests,
documentation, and completed verification in the portable checker.

## Verification

Completed on 2026-06-14:

- The focused `NetworkRequestTest` class passed all 13 tests on both debug and
  release variants under Amazon Corretto 8 and the local Android API 22 SDK.
- Full SDK-backed `make check` passed the portable contracts, legacy Android
  lint baseline, debug and release unit tests, Java compilation, and debug APK
  assembly. Lint retained its one existing `OldTargetApi` warning and no errors.
- External-working-directory `make check` passed the root-independent portable
  gate with Android SDK variables intentionally unset.
- Eight isolated mutations were rejected when they removed ASCII-digit or
  overflow validation, duplicate-header rejection, pre-body ordering, focused
  test coverage, documentation, or completed plan evidence.

## Risks

- Non-compliant backends that previously sent malformed or duplicate lengths
  will now fail through the existing generic request-failure path.
- Responses without a declared length remain supported and bounded while
  streaming.
- The deprecated Apache client remains in place; replacing it is outside this
  narrow response-boundary change.
