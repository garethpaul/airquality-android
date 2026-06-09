# MainActivity Location Manager Guard

## Status: Completed

## Context

`MainActivity.getLocation()` requested the Android location service and then
immediately read GPS and network provider state. On devices, shells, or tests
where `getSystemService(LOCATION_SERVICE)` returns null, the method would rely
on the broad catch block instead of failing closed before provider access.

## Objectives

- Preserve the existing last-known-location lookup behavior when a location
  manager is available.
- Return without provider checks when the location manager is unavailable.
- Log a non-sensitive warning for the unavailable location service path.
- Cover the guard in the SDK-free static checker.

## Work Completed

- Added a null guard after the `LocationManager` lookup in `getLocation()`.
- Returned the existing `location` value when the service is unavailable.
- Added static checker coverage for the guard ordering before provider reads.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_airquality_android_contracts.py`
- `make check`
- `git diff --check`
