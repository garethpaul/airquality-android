# airquality-android

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

- `./gradlew test` or Android Studio's test runner when the SDK is configured

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- Detected references to Twitter. Keep API keys, OAuth credentials, tokens, and account-specific values in local configuration only.

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

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.

## Existing Project Notes

Prior README summary:

> AirQuality Android <!-- README-OVERVIEW-IMAGE --> Legacy Android app that signs in with Twitter, reads the device location, and shows nearby air quality state from the backend service. Toolchain This project currently uses the original Android build stack: - Gradle wrapper 2.2.1 - Android Gradle Plugin 1.2.3 - compile SDK 22 / target SDK 22 - Android build-tools 24.0.3 - Fabric Twitter SDK 1.x Use a JDK and Android SDK compatible with that toolchain before attempting a

