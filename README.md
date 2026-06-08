# AirQuality Android

Legacy Android app that signs in with Twitter, reads the device location, and
shows nearby air quality state from the backend service.

## Toolchain

This project currently uses the original Android build stack:

- Gradle wrapper 2.2.1
- Android Gradle Plugin 1.2.3
- compile SDK 22 / target SDK 22
- Android build-tools 24.0.3
- Fabric Twitter SDK 1.x

Use a JDK and Android SDK compatible with that toolchain before attempting a
larger migration. The Android SDK path must be configured with either:

```sh
export ANDROID_HOME=/path/to/android-sdk
```

or a local, untracked `local.properties` file:

```properties
sdk.dir=/path/to/android-sdk
```

## Verify

Check that Gradle can configure the project:

```sh
./gradlew tasks --no-daemon
```

Build a debug APK:

```sh
./gradlew assembleDebug --no-daemon
```

Run local JVM unit tests:

```sh
./gradlew test --no-daemon
```

CircleCI runs the same gate on push: lint, JVM tests, then `assembleDebug`.

If the SDK path is missing, Gradle fails during Android plugin configuration
with `SDK location not found`; configure `ANDROID_HOME` or `local.properties`
and rerun the command.

The Fabric Gradle plugin is applied only when a `fabricApiKey` Gradle property
is present. Set that property in an untracked local Gradle properties file when
you need Fabric-specific build behavior.

Android Gradle Plugin 1.2.3 expects an obsolete lint API database path that is
not present in current SDK command-line installs. `lint.xml` ignores only that
tooling error while keeping project lint checks active.

## Modernization Notes

The current baseline pins the Fabric Gradle plugin instead of resolving
`1.+` dynamically, and adds a small unit-test seam for air-quality URL
construction. A future modernization pass should migrate Gradle, the Android
Gradle Plugin, SDK levels, Fabric/Twitter login, deprecated Apache HTTP usage,
and synchronous network handling together with emulator or device verification.
