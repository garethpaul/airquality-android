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
- Keep CircleCI and local Gradle verification aligned where the old stack allows
- Keep background request inputs validated before network calls are attempted
- Keep backend request timeouts wired into the HTTP client that actually executes
  the request
- Keep malformed or missing air-quality responses from crashing sensor-driven
  rendering
- Keep Twitter login activity-result handling guarded when a session already
  exists

Next priorities:

- Migrate Gradle, the Android Gradle Plugin, and SDK levels in a dedicated pass
- Replace deprecated Fabric/Twitter login dependencies with maintained options
- Move synchronous networking and Apache HTTP usage to modern Android APIs
- Add tests around URL construction, location handling, and failure states

Contribution rules:

- One PR = one topic. Keep modernization, dependency updates, and behavior
  changes separate unless they must move together.
- Run `./gradlew tasks --no-daemon`, `./gradlew assembleDebug --no-daemon`, and
  `./gradlew test --no-daemon` with a compatible SDK before pushing code changes.
- Document any required local SDK or credential setup in `README.md`.
- Do not remove legacy compatibility accidentally while updating dependencies.

## Security And Privacy

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
