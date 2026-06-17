---
title: Remove Unused Direct Square Network Dependencies
type: fix
date: 2026-06-17
---

# Remove Unused Direct Square Network Dependencies

Status: Planned

## Problem

`app/build.gradle` directly declares Retrofit 1.6.1, OkHttp URLConnection 2.0.0,
OkHttp 2.0.0, and Okio 1.0.1 even though application and test source import none
of them. The resolved graph shows TwitterKit already owns the Retrofit version it
requires transitively, while the direct OkHttp and Okio declarations add unused
runtime artifacts and make legacy dependency ownership harder to review.

## Priority

1. Remove unused direct network libraries that expand the application classpath
   without owning any source behavior.
2. Preserve TwitterKit's transitive Retrofit contract and prove the legacy API
   22 build still resolves, tests, lints, and assembles.
3. Defer Fabric/TwitterKit replacement and Gradle/Android plugin modernization to
   a dedicated migration with login and device-runtime coverage.

## Requirements

- R1. Remove all four direct Square networking declarations from
  `app/build.gradle`.
- R2. Preserve the TwitterKit dependency and its transitive Retrofit ownership;
  do not add replacement libraries or change application behavior.
- R3. Add a portable static contract that rejects reintroduction of direct
  Retrofit, OkHttp, URLConnection adapter, or Okio declarations.
- R4. Prove the configured Java 8 and Android API 22 build still passes unit
  tests, lint, and debug assembly with the reduced direct dependency set.
- R5. Update maintained dependency guidance and record actual verification
  without changing credentials, SDK levels, workflows, signing, or source code.

## Key Technical Decisions

- **Remove declarations instead of upgrading them:** no source owns these direct
  libraries, and TwitterKit's legacy Retrofit contract remains transitive.
- **Keep TwitterKit unchanged:** replacing the discontinued login stack requires
  authenticated runtime and migration work outside this dependency cleanup.
- **Verify the resolved graph:** source search alone cannot prove transitive
  ownership, so validation must inspect the post-change `compile` graph.

## Implementation Units

### U1. Reduce the direct dependency surface

- **Files:** `app/build.gradle`, `scripts/check_airquality_android_contracts.py`
- **Goal:** remove redundant declarations and enforce the intended dependency
  ownership statically.
- **Verification:** the resolved graph must retain Retrofit only beneath
  TwitterKit and omit direct OkHttp, URLConnection adapter, and Okio roots.

### U2. Record compatibility and maintenance evidence

- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`, this plan
- **Goal:** document the smaller direct classpath and the remaining legacy
  migration boundary.
- **Verification:** root and external gates, hostile mutations, diff, artifact,
  dependency, secret, and whitespace audits must pass.

## Scope Boundaries

- Do not change application Java, resources, manifest behavior, SDK levels,
  Gradle wrapper, Android plugin, repositories, workflows, or credentials.
- Do not remove or replace TwitterKit, Fabric, login behavior, or its required
  transitive Retrofit dependency.
- Do not claim emulator, physical-device, Twitter authentication, or live
  backend validation from build-only evidence.

## Verification Plan

- Capture the before/after `:app:dependencies --configuration compile` graph.
- Run the complete configured Android build under Corretto 8 and API 22.
- Run repository-root and external-directory `make check` with explicit
  toolchain configuration and timeouts.
- Reject mutations that restore each direct dependency, remove the static
  contract, remove guidance, or falsify completed plan evidence.
- Remove only explicit generated build paths, then audit the exact staged files,
  untracked artifacts, credentials, dependency intent, and whitespace.
