---
title: Document TwitterKit OkHttp Transport Ownership
type: fix
date: 2026-06-17
---

# Document TwitterKit OkHttp Transport Ownership

Status: Completed

## Problem

`app/build.gradle` directly declares Retrofit 1.6.1, OkHttp URLConnection 2.0.0,
OkHttp 2.0.0, and Okio 1.0.1 even though application source does not import
them. A source-only review therefore makes the set look redundant. Artifact
inspection shows Retrofit 1.6 contains `OkClient` and classpath detection for
`OkHttpClient` and `OkUrlFactory`; removing the direct set changes TwitterKit's
HTTP transport to URLConnection rather than preserving behavior.

## Priority

1. Make the existing TwitterKit transport ownership explicit so future cleanup
   does not silently change authenticated network behavior.
2. Pin and statically protect the exact compatibility set already proven by the
   legacy Java 8/API 22 build.
3. Defer dependency upgrades and Fabric/TwitterKit replacement to an
   authenticated runtime migration with login and API verification.

## Requirements

- R1. Retain exactly one direct declaration for Retrofit 1.6.1, OkHttp
  URLConnection 2.0.0, OkHttp 2.0.0, and Okio 1.0.1.
- R2. Explain in the build file that Retrofit auto-detects this set and uses it
  as TwitterKit's OkHttp transport.
- R3. Add a portable contract that rejects removal, version drift, duplication,
  or loss of the ownership explanation.
- R4. Prove the `compile` graph and configured Java 8/API 22 lint, tests, and
  debug assembly remain unchanged.
- R5. Update maintained dependency guidance without changing application Java,
  credentials, SDK levels, workflows, signing, or runtime behavior.

## Key Technical Decisions

- **Retain the direct dependencies:** artifact evidence contradicts the initial
  unused-dependency hypothesis because Retrofit selects OkHttp by classpath.
- **Do not upgrade in this task:** version changes require authenticated Twitter
  login and API runtime evidence that is unavailable on this host.
- **Protect exact coordinates:** the compatibility set is legacy but deliberate;
  broad version ranges would make transport behavior non-reproducible.

## Implementation Units

### U1. Make transport ownership executable

- **Files:** `app/build.gradle`, `scripts/check_airquality_android_contracts.py`
- **Goal:** explain and enforce the exact direct compatibility set.
- **Verification:** the post-change `compile` graph must show the same direct
  Square roots and TwitterKit graph as the baseline.

### U2. Record the migration boundary

- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`, this plan
- **Goal:** prevent future source-only cleanup from changing TwitterKit's
  authenticated transport without runtime evidence.
- **Verification:** repository-root and external-directory `make check`, hostile
  mutations, diff, artifact, secret, and whitespace audits must pass.

## Scope Boundaries

- Do not change dependency versions, application Java, resources, manifest,
  SDK levels, Gradle wrapper, Android plugin, repositories, or workflows.
- Do not remove or replace TwitterKit, Fabric, login behavior, or the direct
  Retrofit/OkHttp compatibility set.
- No emulator, physical-device, Twitter authentication, or live backend
  scenario is claimed by build-only evidence.

## Work Completed

- Added an explanatory build comment beside the retained compatibility set.
- Added exact-count portable contracts for all four coordinates and the comment.
- Updated maintained transport ownership and migration-boundary guidance.

## Completed Verification

- Initial source and graph review suggested the direct dependencies were
  redundant, but artifact inspection found Retrofit's `OkClient`,
  `OkHttpClient`, `OkUrlFactory`, and classpath-selection messages. The proposed
  removal was stopped before commit.
- The restored post-change `compile` graph retains the same direct Retrofit,
  OkHttp URLConnection, OkHttp, and Okio roots plus TwitterKit transitive graph.
- Corretto 8 and Android API 22 debug/release unit tests passed with 23 tests per
  variant. Android lint retained one pre-existing non-fatal issue and debug APK
  assembly completed successfully.
- Repository-root and external-directory `make check` each passed the complete
  portable contract and configured Android lint, test, and assembly gate.
- Ten isolated hostile mutations were rejected for coordinate removal, version
  drift, duplication, TwitterKit removal, loss of the ownership explanation,
  maintained-guidance drift, and reopened plan status.
- No emulator, physical-device, Twitter authentication, or live backend
  scenario was executed or claimed.
