# Reject Duplicate Content-Type Headers

status: planned

## Context

`NetworkRequest.readResponseBody()` rejects ambiguous comma-combined media
types but validates only `HttpEntity.getContentType()`. A response carrying
two separate `Content-Type` headers can therefore expose only one value through
the entity and bypass the intended single JSON media-type boundary.

## Requirements

- Reject responses with zero or multiple `Content-Type` headers before body
  streaming.
- Validate the single response header with the existing quote-aware JSON and
  UTF-8 media-type parser.
- Preserve valid JSON media types, strict UTF-8 decoding, response-size limits,
  Content-Length handling, redirect rejection, and connection cleanup.
- Add focused JVM coverage and mutation-sensitive portable contracts.

## Scope Boundaries

- Do not change accepted JSON media types or parameter syntax.
- Do not change dependencies, endpoint construction, request timeouts,
  lifecycle behavior, target SDK, or backend schema.
- Do not contact a live backend, emulator, device, location provider, or
  sensor during tests.

## Implementation Units

### U1: Require one response Content-Type header

**Files:** `app/src/main/java/twitterdev/airquality/NetworkRequest.java`,
`app/src/test/java/twitterdev/airquality/NetworkRequestTest.java`

**Approach:** Read the response header array, require exactly one value, and
pass that value to the existing media-type validator. Add in-memory HTTP
response fixtures proving a valid single JSON header succeeds while duplicate
JSON and mixed JSON/HTML headers fail before body acceptance.

**Execution note:** Test-first with the existing JVM NetworkRequest suite.

**Verification:** The duplicate-header fixtures fail before the source change
and pass after the exact-count guard is installed.

### U2: Preserve the fail-closed repository contract

**Files:** `scripts/check_airquality_android_contracts.py`, `README.md`,
`SECURITY.md`, `CHANGES.md`,
`docs/plans/2026-06-15-duplicate-content-type-headers.md`

**Approach:** Require the response-header count guard, focused fixtures,
maintained guidance, and completed verification evidence.

**Verification:** Isolated mutations to the guard, fixtures, guidance, or plan
completion are rejected.

## Verification Plan

- Run the focused JVM response test, then Android lint, unit tests, and debug
  assembly with Java 8 and API 22.
- Run every portable Make alias and the absolute-Makefile check externally.
- Run isolated hostile mutations for the guard, fixtures, documentation, and
  completed-plan evidence.
- Audit the exact diff, generated artifacts, suspicious secret patterns,
  structured files, file modes, and whitespace before committing.

## Risks

- A nonconforming backend that emits no or duplicate Content-Type headers will
  now fail closed instead of relying on entity-header selection.
- Live backend, device, location-provider, and sensor behavior remain outside
  this deterministic transport-boundary change.
