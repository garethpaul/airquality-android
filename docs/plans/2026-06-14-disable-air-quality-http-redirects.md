# Disable Air Quality HTTP Redirects

Status: Completed

## Context

`NetworkRequest` starts from a fixed HTTPS backend URL and validates the final
HTTP status, but the legacy Apache client retains its default redirect behavior.
A provider or intermediary can therefore redirect the request before the
response validator runs, including away from the intended transport boundary.

## Scope

- Disable automatic redirects on the `HttpParams` supplied to the executing
  `DefaultHttpClient`.
- Preserve the fixed HTTPS endpoint, coordinate validation, timeouts, response
  status and size checks, strict UTF-8 decoding, logging, and cleanup behavior.
- Add mutation-sensitive static coverage for configuration order and completed
  plan evidence.
- Document the no-redirect transport boundary.

## Implementation Units

### 1. Configure redirect rejection

Files:

- `app/src/main/java/twitterdev/airquality/NetworkRequest.java`

Disable redirects before constructing the HTTP client so 3xx responses reach
the existing non-success status rejection path.

### 2. Protect the boundary

Files:

- `scripts/check_airquality_android_contracts.py`
- `docs/plans/2026-06-14-disable-air-quality-http-redirects.md`

Require the redirect setting, its ordering before client construction, and
completed plan evidence in the portable contract checker.

### 3. Document the behavior

Files:

- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`

Describe redirects as rejected rather than followed without changing the app’s
public interface.

## Verification

Completed on 2026-06-14:

- The portable checker recognized the new source, ordering, and documentation
  contracts and failed only while this plan was intentionally still planned.
- The focused `NetworkRequestTest` Gradle task compiled the app and passed under
  Amazon Corretto 8 with the local Android SDK.
- Full SDK-backed `make check` passed the portable contracts, legacy Android
  lint baseline, debug and release unit tests, Java compilation, and debug APK
  assembly under Amazon Corretto 8 and the local Android SDK.
- Four focused mutations were rejected when they removed the redirect setting,
  moved it after client construction, removed the security wording, or changed
  this plan back to `Status: Planned`.

## Risks

- Any future legitimate backend redirect will now fail through the existing
  generic request-failure path and must be handled by updating the fixed URL.
- This change does not replace the deprecated Apache client or broaden network
  permissions.
