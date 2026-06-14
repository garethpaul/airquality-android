# Android Device Verification

Use this checklist on the exact reviewed commit with a compatible Android SDK,
Java 8, and the repository's checksum-verified Gradle wrapper. Repository and
hosted static checks do not substitute for this runtime evidence.

## Evidence Header

Record these values without credentials, precise user location, account data,
or private backend payloads:

- commit SHA and pull request
- tester and UTC timestamp
- Android Studio, SDK, build tools, Java, and Gradle versions
- emulator image or physical-device model and Android version
- clean-install or upgrade path
- `./gradlew lint test assembleDebug --no-daemon` result

Mark every scenario `pass`, `fail`, `blocked`, or `not run`. Attach sanitized
screenshots or log excerpts for failures and explain every blocked or unexecuted
row. Do not convert `not run` into a passing result.

## Launch And Authentication

1. Install the exact debug artifact and launch from a stopped state.
2. Verify blank checked-in Twitter/Fabric credentials fail closed without a
   crash or credential value in logs.
3. With authorized test credentials supplied outside git, verify login success,
   cancellation, and provider failure return to a usable screen.

## Permission And Location Matrix

Run each case from a clean app state:

| Scenario | Expected result | Result | Evidence |
| --- | --- | --- | --- |
| Location permission granted | A real accepted location starts one backend request. | not run | |
| Location permission denied | The app remains usable and does not send default coordinates. | not run | |
| Location services disabled | Provider checks fail closed without a crash. | not run | |
| Last-known location absent | The app waits for a callback before requesting air quality. | not run | |
| GPS and network providers unavailable | No backend request starts and logs remain generic. | not run | |

Use only coarse, synthetic, or otherwise authorized test locations. Sanitized
logs must not contain latitude, longitude, request URLs, provider exception
details, Twitter credentials, or access tokens.

## Lifecycle Matrix

| Scenario | Expected result | Result | Evidence |
| --- | --- | --- | --- |
| Pause before location | Location updates stop and no request starts in background. | not run | |
| Pause during request | Active work is cancelled or invalidated; late callbacks are ignored. | not run | |
| Resume after cancelled request | One retained-location retry starts without a loop. | not run | |
| Resume after failed request | One retry starts; success clears retry intent. | not run | |
| Rotate during location acquisition | Recreated activity does not use stale listeners or callbacks. | not run | |
| Rotate during backend request | Recreated activity does not render a stale response. | not run | |
| Process recreation | Missing in-memory state fails closed without default coordinates. | not run | |

## Backend Matrix

Exercise an authorized test endpoint or network fixture for each response:

- valid 2xx JSON over the fixed HTTPS endpoint;
- offline, timeout, and connection failure;
- redirect response;
- non-2xx status;
- missing or non-JSON media type;
- oversized body;
- malformed UTF-8 and malformed JSON.

The UI must remain usable, response resources must close, and logs must retain
only generic failure categories. Do not point a test build at an untrusted or
production endpoint without authorization.

## Completion

Record the final result, unresolved failures, and links to protected evidence.
Keep screenshots, logs, APKs, credentials, and device exports outside git. A
release claim requires all applicable rows to pass on the exact commit; this
repository currently records the matrix as unexecuted.
