# Canonicalize Signed-Zero Coordinates

Status: Completed

## Problem

`NetworkRequest.normalizeCoordinate` validates and serializes coordinates with
`Double.toString`. Java preserves the sign bit of zero, so accepted inputs such
as `-0`, `-0.0`, and negative hexadecimal zero cross the backend boundary as
`-0.0`. Positive and negative zero identify the same location but currently
produce different request URLs and downstream cache keys.

## Priority

This is a narrow correctness and cache-consistency follow-up to canonical
coordinate serialization. It is higher value than another broad modernization
step because it closes a demonstrated normalization gap without changing the
legacy Android, Gradle, HTTP, or lifecycle boundaries.

## Scope

- Normalize every accepted signed-zero latitude or longitude to `0.0` before
  URL encoding.
- Preserve finite-value checks, latitude/longitude ranges, and canonical
  serialization for every nonzero coordinate.
- Add focused JVM cases for decimal, exponent, suffix, and hexadecimal signed
  zero on both coordinate axes.
- Add mutation-sensitive portable contracts and synchronized maintenance
  guidance.

## Out Of Scope

- Endpoint, timeout, redirect, response parsing, activity lifecycle, location
  acquisition, dependency, Gradle, Android plugin, or SDK changes.
- Emulator, physical-device, live backend, or provider verification.

## Implementation

1. Reproduce the current `-0.0` URL output with a focused regression.
2. Canonicalize a parsed coordinate when it compares equal to zero, then use
   the existing decimal serializer.
3. Protect both axes and multiple accepted Java spellings with JVM tests.
4. Extend the SDK-free checker, README, security guidance, vision, changelog,
   and canonical plan inventory.

## Verification

- Run the focused `NetworkRequestTest`, then all supported Gradle tests.
- Run repository-root and external-directory `make check` with explicit
  timeouts.
- Reject isolated hostile mutations that remove zero canonicalization, restore
  signed output, weaken axis or syntax coverage, remove guidance, or falsify
  plan completion.
- Audit the exact diff, generated artifacts, credential-shaped additions,
  conflict markers, file modes, dependency/workflow drift, and whitespace.

## Residual Risk

- Java 8/API 22 JVM and build verification cannot substitute for an authorized
  emulator, physical device, location provider, or live backend request.

## Completed Verification

- The focused JVM regression failed before implementation because both decimal
  signed-zero inputs produced `-0.0` in the backend URL.
- Debug and release JVM tests passed after canonicalization, including decimal,
  exponent, suffix, and hexadecimal signed-zero spellings on both axes.
- Android lint retained one pre-existing non-fatal issue, all unit tests passed,
  and debug APK assembly completed under Java 8 and Android API 22.
- Repository-root and external-directory `make check` both passed the complete
  SDK-free and SDK-backed gate.
- All seven isolated hostile mutations were rejected: removed canonicalization,
  restored negative-zero output, renamed coverage, removed decimal or
  hexadecimal spellings, removed guidance, and reopened plan status.
