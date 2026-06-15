# JSON Response Charset Validation

status: completed

## Context

The backend client decodes every accepted JSON response with a strict UTF-8
decoder, but its media-type validation ignores `Content-Type` parameters. A
response declaring `charset=ISO-8859-1`, an empty charset, or conflicting
duplicate charsets is accepted before the body is interpreted as UTF-8. That
creates a contradiction between trusted metadata and actual decoding.

## Priorities

1. Require response charset metadata to agree with strict UTF-8 decoding.
2. Reject ambiguous or malformed charset declarations before reading the body.
3. Preserve valid bare and vendor JSON media types, response-size limits,
   redirect rejection, request lifecycle behavior, and legacy build support.

## Requirements

- Accept JSON media types with no charset parameter.
- Accept one case-insensitive `charset=utf-8` parameter with optional HTTP
  whitespace and quoted or unquoted value forms.
- Reject empty, non-UTF-8, malformed, or duplicate charset declarations.
- Reject malformed media-type parameters instead of silently ignoring them.
- Add focused JUnit coverage and mutation-sensitive portable checker contracts.
- Keep all validation local and credential-free.

## Scope Boundaries

- Do not replace the legacy Apache HTTP client, AsyncTask lifecycle, Gradle
  wrapper, Android SDK levels, or dependency graph.
- Do not change URL construction, timeouts, redirect policy, response-size
  limits, JSON parsing, UI behavior, or device-verification requirements.

## Implementation Units

1. Extend `NetworkRequest.requireJsonMediaType` with a small parameter parser
   that validates syntax and enforces at most one UTF-8 charset.
2. Add direct tests in `NetworkRequestTest` for accepted UTF-8 forms and
   rejected conflicting, malformed, empty, and non-UTF-8 forms.
3. Extend `scripts/check_airquality_android_contracts.py` and maintained
   documentation with the charset-to-decoder consistency contract and
   completed evidence.

## Verification Plan

- Run focused network-request tests, then the canonical Gradle and Make gates.
- Run the portable checker from the repository root and an external working
  directory.
- Run isolated hostile mutations against parser decisions, tests,
  documentation, and completed plan evidence.
- Audit the exact diff, generated artifacts, credential patterns, and
  whitespace before committing.

## Work Completed

- Added quote-aware parameter parsing that preserves syntactically valid
  token and quoted values while rejecting malformed delimiters.
- Required at most one charset declaration and accepted only case-insensitive
  UTF-8 metadata before response body access.
- Added JUnit coverage for quoted/unquoted UTF-8, optional whitespace, quoted
  delimiters, malformed parameters, empty values, duplicate charsets, and
  non-UTF-8 declarations.
- Extended the portable checker and maintained guidance with the
  charset-to-decoder consistency contract.

## Verification Completed

- Java 8 with the local API 22 Android SDK passed `./gradlew lint test
  assembleDebug --no-daemon`; all 13 network-request tests passed for debug and
  release, and the debug APK assembled successfully.
- `make lint`, `make test`, `make verify`, and `make check` passed from the
  repository root with SDK-free validation.
- The complete `make check` gate passed from an external working directory
  through the absolute Makefile path.
- Focused hostile mutations to charset semantics, quote handling, tests,
  documentation, and completed plan evidence were rejected.
- `git diff --check` and the intended-path secret and generated-artifact scan
  passed after explicit removal of local Gradle build outputs.
