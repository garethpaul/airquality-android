# Require JSON Air Quality Media Types

Status: Planned

## Context

`NetworkRequest` rejects redirects, non-success status codes, oversized bodies,
and malformed UTF-8 before parsing JSON. It does not validate the response
media type, so a successful HTML, text, or ambiguous comma-joined response is
still read and passed to the JSON parser.

## Scope

- Accept case-insensitive `application/json` and nonempty
  `application/*+json` media types with optional parameters.
- Reject missing, malformed, comma-joined, and non-JSON response media types
  before opening or reading the response body.
- Preserve the existing status, redirect, byte-limit, strict UTF-8, logging,
  and connection-cleanup behavior.
- Add focused unit tests, mutation-sensitive portable contracts, and
  maintenance documentation.

## Implementation Units

### U1. Validate the response media type

**Files:**

- `app/src/main/java/twitterdev/airquality/NetworkRequest.java`

Read the entity content type after the successful-status and body-presence
checks. Normalize only the media-type token, reject ambiguous or malformed
values, and require a JSON application type before accessing content bytes.

**Test scenarios:**

- Accept mixed-case `application/json` with parameters.
- Accept a structured `application/*+json` subtype.
- Reject missing, comma-joined, malformed, and non-JSON values.
- Prove rejected types do not open the response body.

### U2. Protect the boundary

**Files:**

- `app/src/test/java/twitterdev/airquality/NetworkRequestTest.java`
- `scripts/check_airquality_android_contracts.py`
- `docs/plans/2026-06-14-air-quality-json-media-type.md`

Add focused executable coverage and require the parser policy, validation
ordering, tests, and completed plan evidence in the portable checker.

### U3. Document the behavior

**Files:**

- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`

Describe the fail-closed JSON media-type boundary and its compatibility with
parameterized and structured-suffix JSON responses.

## Verification

- Run focused `NetworkRequestTest` coverage and the full SDK-backed project
  gate.
- Run the portable gate from the repository root and an external working
  directory.
- Reject isolated mutations that remove validation, weaken the accepted type
  policy, move validation after body access, remove focused tests, or leave
  this plan incomplete.
- Audit the exact diff, generated artifacts, credentials, conflict markers,
  and whitespace before committing implementation.

## Risks

- A backend that incorrectly labels valid JSON as another media type will now
  fail through the existing request-failure path.
- This change does not sniff body content, replace the deprecated Apache
  client, or change the fixed backend URL.
