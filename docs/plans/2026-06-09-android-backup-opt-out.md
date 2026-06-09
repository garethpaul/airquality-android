# Android Backup Opt Out

## Status: Completed

## Context

The AirQuality Android sample manifest opted into platform app-data backup by
default. The app handles location and Twitter/Fabric app state, so the
checked-in manifest should fail closed unless a maintainer deliberately changes
that privacy boundary.

## Objectives

- Set the application manifest to `android:allowBackup="false"`.
- Preserve existing permission and credential placeholder behavior.
- Extend the SDK-free static checker so backup opt-in cannot return silently.
- Document the guard in README, SECURITY, VISION, and CHANGES.

## Work Completed

- Disabled app-data backup in `app/src/main/AndroidManifest.xml`.
- Added static checker coverage for the manifest opt-out.
- Added this completed plan and top-level documentation notes.

## Verification

- `python3 -m py_compile scripts/check_airquality_android_contracts.py`
- `python3 scripts/check_airquality_android_contracts.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
