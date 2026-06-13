# Changes

## 2026-06-13

1. Replaced throwable-bearing warnings with generic NetworkRequest failure logs
   for protocol, I/O, JSON, and invalid-parameter paths.
2. Strengthened SDK-free contracts and documentation against stack-trace,
   exception-message, coordinate, and provider-detail logging regressions.
3. Removed the caught platform exception from `MainActivity` location failure
   logs while retaining the stable failure category and fallback behavior.
4. Added portable contracts and privacy guidance for the location log boundary.

## 2026-06-12

1. Regenerated the Gradle wrapper bootstrap with official Gradle 8.14.5
   tooling while retaining the Gradle 2.2.1 Android runtime.
2. Pinned Gradle's official distribution checksum, added exact wrapper
   contracts, and added a separate hosted Java 8/API 22 Android gate.
3. Retained the active `NetworkRequest`, ignored stale or teardown-time
   callbacks, and cancelled the task when `MainActivity` is destroyed.
4. Added SDK-free lifecycle contracts and a completed implementation plan.

## 2026-06-10

1. Added a pinned, read-only GitHub Actions workflow that runs the SDK-free
   `make check` baseline on Python 3.10, 3.12, and 3.14.
2. Extended the Android contract checker and docs to require the hosted CI
   verification path.
3. Replaced unbounded `BasicResponseHandler` usage with explicit 2xx validation,
   a 1 MiB response cap, and response/connection cleanup.
4. Pinned GitHub Actions to Ubuntu 24.04 with superseded-run cancellation and
   made SDK-free and optional Gradle checks root-independent.
5. Removed the UI-thread wait for the air-quality `AsyncTask`; `MainActivity`
   now applies the response when background work completes.

## 2026-06-09

1. Guarded `MainActivity.getLocation` when the Android location service is
   unavailable before reading provider state.
2. Added static checker coverage for the location manager availability guard.

1. Disabled Android app-data backup in the checked-in manifest and added static
   checker coverage for the opt-out.

1. Skipped Fabric/Twitter initialization when the checked-in Android
   application credentials are blank.
2. Added static checker coverage for the application credential guard.

1. Removed tracked IDE workspace metadata and added static checker coverage for
   `.idea/`, `.vscode/`, and `*.iml` ignore rules.

1. Guarded malformed accelerometer events and missing display views before
   sensor-driven rendering.
2. Added static checker coverage for sensor event and display-view guards.

1. Guarded `MainActivity` accelerometer listener registration and cleanup when
   the sensor service or accelerometer is unavailable.
2. Added static checker coverage for the accelerometer lifecycle guard.

1. Guarded the Twitter login button lookup before setting login callbacks.
2. Added static checker coverage for login button callback setup.

1. Guarded `LoginActivity.onActivityResult` so already-authenticated sessions
   do not dereference an uninitialized Twitter login button.
2. Added static checker coverage for the login button lifecycle guard.

1. Wired the existing connection and socket timeout settings into the actual
   Apache HTTP client used by `NetworkRequest`, and added an SDK-free static
   contract to keep the backend request bounded on hosts without Android SDK
   verification.
2. Defaulted missing or malformed `MainActivity` air-quality responses to an
   explicit unknown state, preserved request interruption, and guarded the
   accelerometer display path against null `state` crashes.

## 2026-06-08

1. Stabilized the legacy Android build by pinning Fabric Gradle tooling and
   moving the project to Android build-tools 24.0.3, which provides a 64-bit
   `aapt` binary on the current Linux build host.
2. Kept Fabric build behavior opt-in through a local `fabricApiKey` property so
   public builds do not require a checked-in private Fabric API key.
3. Added a local JVM unit test around air-quality request URL construction so
   request composition can be verified without an emulator, device, network, or
   Android runtime.
4. Cleaned lint findings by removing a duplicate permission, moving status
   bitmaps to `drawable-nodpi`, extracting UI text into string resources, adding
   an image content description, and explicitly disabling RTL support for this
   legacy layout.
5. Added module-level lint configuration for obsolete SDK-tooling checks that
   Android Gradle Plugin 1.2.3 cannot satisfy with current command-line SDK
   installs, while leaving project lint checks active.
6. Added setup documentation, a modernization plan, and CircleCI that runs lint,
   JVM tests, and a debug APK build.
7. Expanded the `NetworkRequest.buildUrl` contract to cover coordinate
   trimming and invalid coordinate rejection.
8. Added SDK-free static contracts and `make check` for URL construction,
   manifest permission, empty credential, and Fabric tooling guardrails.
9. Routed background air-quality requests through an explicit `AsyncTask`
   parameter contract and replaced silent broad failure swallowing with warning
   logs.
