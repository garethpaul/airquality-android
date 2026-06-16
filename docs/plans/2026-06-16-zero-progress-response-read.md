# Zero-Progress Response Read Guard

Status: Planned

## Problem

`NetworkRequest.readResponseBody()` bounds backend response bytes, but its
stream loop assumes every non-EOF `InputStream.read(byte[])` call returns a
positive byte count. A malformed or adversarial stream that returns zero can
keep the legacy `AsyncTask` spinning indefinitely without consuming the byte
budget or reaching JSON parsing.

## Priorities

1. P0: Fail closed when a response stream reports zero progress.
2. P1: Preserve EOF handling, fragmented positive reads, the 1 MiB limit,
   strict UTF-8 decoding, and guaranteed stream cleanup.
3. P1: Add executable and static mutation-sensitive evidence for the new
   boundary.

## Requirements

1. A zero-byte read before EOF must raise a controlled `IOException` rather
   than retrying indefinitely.
2. Positive fragmented reads must still accumulate in order through EOF.
3. Exact-limit and oversized responses must retain the existing 1 MiB policy.
4. The response stream must close after success, zero progress, oversize, or
   decoding failure.
5. Existing status, media-type, charset, content-length, redirect, timeout,
   request-lifecycle, and JSON behavior must remain unchanged.
6. Tests, documentation, the SDK-free checker, and this plan must preserve the
   completed behavior and truthful verification evidence.

## Implementation Units

### U1: Isolate Bounded Stream Reading

**File:** `app/src/main/java/twitterdev/airquality/NetworkRequest.java`

Move the existing bounded accumulation into a package-visible helper that
rejects zero progress and retains the current byte limit, strict UTF-8 decode,
and caller-owned cleanup semantics. Route `readResponseBody()` through it only
after the existing response metadata checks.

### U2: Add Stream Regressions

**File:** `app/src/test/java/twitterdev/airquality/NetworkRequestTest.java`

Use dependency-free `InputStream` fakes to cover fragmented positive reads,
zero progress, exact-limit success, and oversize rejection without live
network access.

### U3: Preserve Durable Contracts

**Files:** `scripts/check_airquality_android_contracts.py`, `README.md`,
`SECURITY.md`, `VISION.md`, `CHANGES.md`, and this plan.

Require the helper, zero-progress rejection, focused regressions, maintained
guidance, completed plan status, and actual verification evidence.

## Test Scenarios

- A stream returning JSON in multiple positive chunks is decoded completely.
- A stream returning zero before EOF fails immediately with `IOException`.
- A response exactly at 1 MiB remains accepted.
- A response one byte over the limit remains rejected.
- The production response path still closes its stream on every exit.
- Repository and external-directory gates remain green.

## Scope Boundaries

- Do not replace Apache HTTP, `AsyncTask`, Gradle, Fabric, TwitterKit, or the
  application endpoint.
- Do not change timeouts, redirects, media types, charset, content length,
  location, request ownership, or JSON rendering behavior.
- Do not add retries for a non-progressing stream.
- Emulator, physical-device, and live provider behavior remain outside local
  validation.

## Verification

- Run the focused stream tests before the complete Android gate.
- Run repository and external-directory `make check` with the configured JDK
  and Android SDK environment.
- Reject isolated mutations that remove the zero-progress guard, bypass the
  helper, weaken focused tests or guidance, or falsify plan completion.
- Audit generated Gradle/build artifacts, exact diff, credentials, dependency
  and workflow drift, conflict markers, file modes, and whitespace before
  commit.
