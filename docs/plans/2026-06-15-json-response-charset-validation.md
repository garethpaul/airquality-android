# JSON Response Charset Validation

status: planned

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
3. Extend `scripts/check-baseline.rb` and maintained documentation with the
   charset-to-decoder consistency contract and completed evidence.

## Verification Plan

- Run focused network-request tests, then the canonical Gradle and Make gates.
- Run the portable checker from the repository root and an external working
  directory.
- Run isolated hostile mutations against parser decisions, tests,
  documentation, and completed plan evidence.
- Audit the exact diff, generated artifacts, credential patterns, and
  whitespace before committing.
