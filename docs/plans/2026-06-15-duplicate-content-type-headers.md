# Reject Duplicate Content-Type Headers

status: completed

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

**Approach:** Read the response header array, pass its values through a pure
single-header validator, and delegate the sole value to the existing media-type
parser. Add JVM string-array fixtures proving a valid single JSON header
succeeds while missing, duplicate JSON, and mixed JSON/HTML headers fail. Keep
the response-header integration fail closed through a static source contract;
the legacy Android mockable jar stubs Apache entity mutation in local JVM tests.

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

## Work Completed

- Added a pure single-header validator that rejects missing or duplicate
  Content-Type values before delegating to the existing JSON media-type parser.
- Wired response processing to enumerate `response.getHeaders("Content-Type")`
  before Content-Length validation or body access.
- Added `requireSingleJsonMediaTypeRejectsAmbiguousHeaders` with focused
  missing, duplicate JSON, and mixed JSON/HTML header fixtures, portable
  contracts, and synchronized maintained guidance.

## Verification Completed

- The focused test first failed because the validator was absent, then passed
  after implementation. An initial in-memory entity fixture also documented
  that the legacy Android mockable jar stubs Apache entity mutation, so the
  executable seam was narrowed to pure header strings.
- Android lint, unit tests, and debug assembly passed under Java 8 and API 22;
  all 17 tests passed on both debug and release variants, and lint retained its
  single pre-existing warning with no errors.
- `make lint`, `make test`, `make verify`, repository-root `make check`, and
  the external absolute-Makefile `make check` all passed; the full checks used
  Java 8 and Android API 22.
- Six isolated hostile mutations covering the exact-count guard, response
  integration, focused test identity, duplicate fixture, maintained guidance,
  and completed plan status were rejected.
- Exact eight-path, structured-file, file-mode, whitespace, conflict-marker,
  credential-shaped addition, secret and generated-artifact scan passed after
  removing only the explicitly listed Gradle, Android build, Python bytecode,
  and mutation-snapshot paths.
