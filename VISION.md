## AirQuality Android Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

AirQuality Android is a legacy Android app that signs in with Twitter, reads the
device location, and shows nearby air quality state from the backend service.

This repository is useful as a preserved Android/Fabric-era sample and as a
small client for the air-quality API flow. Project setup and verification notes
live in [`README.md`](README.md).

The goal is to keep the app understandable and buildable while creating a clear
path toward a safer modern Android baseline.

The current focus is:

Priority:

- Preserve the documented legacy Gradle and Android plugin toolchain
- Keep the location-to-air-quality flow easy to inspect
- Avoid committing local SDK paths, signing material, or Fabric/Twitter secrets
- Keep Android app-data backup disabled by default for the legacy sample
- Skip Fabric/Twitter initialization while public credential placeholders are blank
- Keep CircleCI and local Gradle verification aligned where the old stack allows
- Keep background request inputs validated before network calls are attempted
- Keep backend request timeouts wired into the HTTP client that actually executes
  the request
- Bound backend response bytes and reject non-2xx responses before JSON parsing
- Strict backend Content-Length validation before response body access
- Reject automatic backend redirects away from the fixed HTTPS endpoint
- Require JSON application media types before reading backend response bodies
- Backend responses must contain exactly one Content-Type header before body access.
- Response Content-Type parsing accepts only space and tab as optional HTTP whitespace; CR, LF, and other controls fail before body access.
- Response charset metadata must be absent or unambiguous UTF-8 before body
  decoding
- Quoted Content-Type parameter values may contain commas while unquoted or
  combined comma values remain invalid
- Reject malformed UTF-8 backend responses before JSON parsing
- Backend response reads fail when a stream reports zero progress instead of spinning indefinitely.
- Cancel activity-owned backend requests during teardown and ignore stale
  completion callbacks
- Keep location-gated backend requests from using default coordinates and stop
  location updates once a usable position is acquired
- Send validated locations as canonical decimal coordinates across the backend request boundary; signed-zero coordinates normalize to `0.0`
- Invalidate in-flight backend work while paused and restart only interrupted
  requests from the retained location on resume
- Preserve failed-request retry intent across pause and retry once on resume
  without an automatic retry loop
- Keep location service availability checked before provider state reads
- Keep malformed or missing air-quality responses from crashing sensor-driven
  rendering
- MainActivity accepts air_quality only when its JSON value is a nonblank string.
- MainActivity trims surrounding whitespace from nonblank air_quality strings.
- Keep accelerometer registration guarded for devices or layouts without an
  available sensor service
- Keep sensor events and display views guarded before accelerometer rendering
- Keep Twitter login activity-result handling guarded when a session already
  exists
- Keep Twitter login callback setup guarded when layouts are stale
- Keep the credential-free launcher from accessing an uninitialized TwitterKit
  session manager, and expose the unavailable login configuration to users
- Keep IDE workspace metadata out of the shared Android project baseline
- Keep GitHub Actions aligned with the SDK-free Python `make check` baseline
- Keep the legacy Gradle runtime behind a checksum-verified generated wrapper
- Keep a separate hosted Java 8/API 22 job for complete Android verification
- Keep exact-commit emulator and physical-device evidence separate from static
  contracts, with unexecuted lifecycle and permission scenarios recorded

Next priorities:

- Evaluate Gradle runtime, Android plugin, and SDK modernization together in a
  dedicated compatibility pass; wrapper hardening is separate
- Replace deprecated Fabric/Twitter login dependencies with maintained options
- TwitterKit's Retrofit transport intentionally receives pinned direct OkHttp,
  URLConnection adapter, and Okio dependencies; do not remove them without
  authenticated runtime migration evidence.
- Move synchronous networking and Apache HTTP usage to modern Android APIs
- Add tests around URL construction, location handling, and failure states
- Execute the device verification matrix on an authorized emulator and
  physical device with sanitized evidence

Contribution rules:

- One PR = one topic. Keep modernization, dependency updates, and behavior
  changes separate unless they must move together.
- Run `./gradlew tasks --no-daemon`, `./gradlew assembleDebug --no-daemon`, and
  `./gradlew test --no-daemon` with a compatible SDK before pushing code changes.
- Document any required local SDK or credential setup in `README.md`.
- Preserve Android backup opt-out when changing the manifest.
- Do not remove legacy compatibility accidentally while updating dependencies.
- Keep `.github/workflows/check.yml` in sync with the local static and Gradle
  verification gates.

## Security And Privacy

LoginActivity is the only exported launcher; MainActivity is explicitly non-exported and reached with an explicit in-app intent.

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Location and account identity are sensitive. Changes that touch location,
Twitter/Fabric auth, or backend requests need to make data flow explicit and
avoid logging personal information.

Secrets belong in local Gradle properties, environment configuration, or the
platform credential store. They must not be committed.

## What We Will Not Merge (For Now)

- Broad rewrites that mix build-system migration with user-facing behavior
- New analytics, tracking, or identity integrations without a clear privacy case
- Hardcoded API keys, tokens, endpoints, or local SDK paths
- Dependency bumps that only work on one developer machine

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
