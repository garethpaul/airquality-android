# AirQuality Android Application Credential Initialization Guard

Date: 2026-06-09
Status: Completed

## Problem

The public source intentionally keeps the Twitter consumer key, Twitter
consumer secret, and Fabric manifest API key empty. `AirQualityApplication`
still attempted to initialize Fabric/Twitter with those empty values at
startup, which made the checked-in app path depend on placeholder credentials.

## Scope

- Add a startup guard in `AirQualityApplication` that skips Fabric/Twitter
  initialization when either credential is blank.
- Keep checked-in credential constants and manifest API-key metadata empty.
- Add static contract coverage for the guard so future auth edits preserve the
  public-source startup behavior.

## Verification

- Red: `make test` failed with
  `AirQualityApplication must skip Fabric initialization when credentials are blank`.
- Green: `make test` passes after adding the guard.
- Full gate: `make check`.
