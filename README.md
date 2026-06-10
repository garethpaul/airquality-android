# airquality-android

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/airquality-android` is an Android application or sample. AirQuality App for Android

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: Java (6).

## Repository Contents

- `README.md` - project overview and local usage notes
- `build.gradle` - Android or Gradle build configuration
- `.circleci` - source or example code
- `app` - source or example code
- `docs` - source or example code
- `gradle` - source or example code
- `gradlew` - Android or Gradle build configuration
- `SECURITY.md` - security reporting and disclosure guidance
- `VISION.md` - project direction and maintenance guardrails

Additional scan context:

- Source directories: .circleci, app, docs, gradle
- Dependency and build manifests: build.gradle, gradlew
- Entry points or build surfaces: Gradle build files
- Test-looking files: app/src/androidTest/java/twitterdev/airquality/ApplicationTest.java, app/src/test/java/twitterdev/airquality/NetworkRequestTest.java

## Getting Started

### Prerequisites

- Git
- Android Studio or a compatible Android SDK
- Gradle or the checked-in Gradle wrapper when present

### Setup

```bash
git clone https://github.com/garethpaul/airquality-android.git
cd airquality-android
```

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- Use Android Studio to open the project or run `./gradlew assembleDebug` when the Android SDK is configured.

## Testing and Verification

- `make check` - run SDK-free static contracts and skip Gradle when no Android SDK is configured
- `./gradlew test` or Android Studio's test runner when the SDK is configured
- GitHub Actions runs the SDK-free `make check` baseline on Python 3.10, 3.12,
  and 3.14 for pushes, pull requests, and manual maintenance runs. The workflow
  remains separate from the legacy Gradle/Fabric toolchain migration.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- Detected references to Twitter. Keep API keys, OAuth credentials, tokens, and account-specific values in local configuration only.
- `AirQualityApplication` skips Fabric/Twitter initialization while checked-in
  credential placeholders are blank.
- `NetworkRequest.buildUrl` trims, validates, and URL-encodes latitude and longitude before constructing the backend request.
- `NetworkRequest.buildUrlFromParams` validates the `AsyncTask` parameter array before the background request path creates an HTTP request.
- `NetworkRequest` applies bounded connection and socket timeouts to the HTTP client used for the backend request.
- `MainActivity` treats missing or malformed `air_quality` JSON as an explicit unknown state before accelerometer rendering.
- `MainActivity` checks that the location service is available before reading
  GPS or network provider state.
- `MainActivity` registers accelerometer updates only after confirming the sensor
  manager and accelerometer are available.
- `MainActivity` ignores malformed sensor events and missing display views
  before accelerometer-driven rendering.
- `LoginActivity` forwards Twitter activity results only when a login button
  was initialized for an unauthenticated session.
- `LoginActivity` sets Twitter login callbacks only after confirming the login
  button exists in the active layout.
- Local IDE metadata stays ignored so Android Studio, IntelliJ, and VS Code
  workspace files do not become part of the shared AirQuality baseline.

## Security and Privacy Notes

- Review changes touching authentication or token handling; examples from the scan include app/src/main/java/twitterdev/airquality/LoginActivity.java, docs/plans/2026-06-08-android-build-reproducibility.md.
- Review changes touching external API calls or credential-adjacent configuration; examples from the scan include app/build.gradle, app/src/main/AndroidManifest.xml, app/src/main/java/twitterdev/airquality/AirQualityApplication.java, app/src/main/java/twitterdev/airquality/LoginActivity.java, and 4 more.
- Review changes touching network requests, sockets, or service endpoints; examples from the scan include .circleci/config.yml, app/build.gradle, app/src/androidTest/java/twitterdev/airquality/ApplicationTest.java, app/src/main/AndroidManifest.xml, and 6 more.
- Review changes touching mobile permissions or privacy-sensitive device data; examples from the scan include CHANGES.md, app/src/main/AndroidManifest.xml, app/src/main/java/twitterdev/airquality/MainActivity.java, docs/plans/2026-06-08-android-build-reproducibility.md, and 1 more.
- Review changes touching file, media, JSON, XML, CSV, OCR, or data parsing; examples from the scan include .circleci/config.yml, CHANGES.md, app/lint.xml, app/src/main/AndroidManifest.xml, and 6 more.
- Review changes touching database, model, or persistence code; examples from the scan include docs/plans/2026-06-08-android-build-reproducibility.md.
- Review changes touching infrastructure, proxy, cloud, or deployment configuration; examples from the scan include .circleci/config.yml.

## Maintenance Notes

- This looks like a legacy Android project or sample. Expect Android SDK, Gradle, and support-library versions to matter.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-09-network-request-async-parameter-contracts.md` for the background request parameter-validation pass.
- See `docs/plans/2026-06-09-network-request-timeout-contracts.md` for the HTTP timeout wiring pass.
- See `docs/plans/2026-06-09-main-activity-air-quality-state-contracts.md` for the activity fallback-state pass.
- See `docs/plans/2026-06-09-main-activity-location-manager-guard.md` for the
  location service availability guard.
- See `docs/plans/2026-06-09-main-activity-sensor-lifecycle-guard.md` for the
  accelerometer listener lifecycle guard.
- See `docs/plans/2026-06-09-main-activity-sensor-event-guard.md` for malformed
  sensor event and missing display-view guards.
- See `docs/plans/2026-06-09-login-activity-result-guard.md` for the Twitter
  login button lifecycle guard.
- See `docs/plans/2026-06-09-login-button-lookup-guard.md` for guarded Twitter
  login button callback setup.
- See `docs/plans/2026-06-09-application-credential-initialization-guard.md`
  for the blank credential startup guard.
- See `docs/plans/2026-06-09-editor-metadata-ignore.md` for the local editor
  metadata ignore baseline.
- See `docs/plans/2026-06-09-android-backup-opt-out.md` for the app-data
  backup opt-out baseline.
- See `docs/plans/2026-06-10-ci-baseline.md` for the hosted GitHub Actions
  baseline.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
