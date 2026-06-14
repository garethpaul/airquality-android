# Canonical Coordinate Serialization

Status: Completed

## Context

`NetworkRequest` validates coordinates with `Double.parseDouble` but returns
the original trimmed token to the backend. Java accepts forms such as a `d`
suffix and hexadecimal floating-point notation that the Python backend rejects,
so a value can pass client validation and still produce an invalid request.

## Scope

- Preserve the existing finite and latitude/longitude range validation.
- Serialize every accepted value with Java's canonical decimal representation
  before URL encoding.
- Prove Java-only suffix and hexadecimal syntax no longer crosses the backend
  request boundary unchanged.
- Add mutation-sensitive portable contracts and maintenance documentation.

## Verification Plan

- Run focused `NetworkRequestTest` coverage under Java 8 and Android API 22.
- Run the full SDK-backed and external-working-directory `make check` gates.
- Reject isolated mutations that restore the original token, remove regression
  coverage, weaken documentation, or reopen the completed plan.
- Audit the exact diff, generated artifacts, conflict markers, whitespace, and
  credential-shaped additions before commit and push.

## Risks

- Equivalent inputs may use a different textual representation in the request,
  but the numeric coordinate and supported range remain unchanged.
- This change does not alter the fixed endpoint, lifecycle, timeout, response,
  logging, or privacy behavior.

## Verification

Completed on 2026-06-14:

- The Java 8 runtime confirmed `37.7d` and `0x1.2p5` parse successfully while
  Python rejects both original tokens.
- The SDK-backed Gradle `test` task passed all 11 `NetworkRequestTest` cases on
  debug and release variants. Gradle 2.2.1 does not support the modern
  `--tests` filter, so the repository-supported complete task was used.
- Removing canonical serialization made
  `buildUrlCanonicalizesJavaOnlyCoordinateSyntax` fail on the debug variant.
- Full SDK-backed and external-working-directory `make check` passed.
- Five isolated hostile mutations were rejected across runtime behavior,
  source and test contracts, documentation, and completed-plan status.
