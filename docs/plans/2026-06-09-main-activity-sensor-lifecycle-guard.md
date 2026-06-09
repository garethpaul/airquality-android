# Main Activity Sensor Lifecycle Guard

Status: Completed

## Context

`MainActivity` registered accelerometer updates directly in both `onCreate` and
`onResume`. That assumed the Android sensor service and accelerometer were
always available, and it also split registration cleanup away from the lifecycle
guardrail used by the rest of the activity.

## Objectives

- Guard accelerometer registration when the sensor manager is unavailable.
- Guard accelerometer registration when the device has no accelerometer.
- Keep listener cleanup null-safe during `onPause`.
- Preserve the existing accelerometer-driven air-quality display behavior when
  the sensor is present.
- Extend the SDK-free static checker and maintenance docs for the lifecycle
  contract.

## Work Completed

- Moved accelerometer registration behind `registerAccelerometerListener()`.
- Added non-fatal warnings for unavailable sensor service or accelerometer
  hardware.
- Added `unregisterAccelerometerListener()` to keep pause cleanup null-safe.
- Extended `scripts/check_airquality_android_contracts.py` to require the guard.
- Updated README, VISION, CHANGES, and this completed plan.

## Verification

- `python3 -m py_compile scripts/check_airquality_android_contracts.py`
- `python3 scripts/check_airquality_android_contracts.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`

On hosts without `ANDROID_HOME` or `local.properties`, `make build` skips the
legacy Gradle build and leaves the SDK-free contract checker as the baseline
verification.
