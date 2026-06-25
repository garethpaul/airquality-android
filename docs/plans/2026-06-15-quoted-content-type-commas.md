# Quoted Content-Type Commas

status: completed

## Context

`NetworkRequest.requireJsonMediaType()` rejects every comma before parsing the
media type and its parameters. RFC 9110 permits media-type parameter values to
use quoted-string syntax, where a comma is data rather than a combined field
separator. The existing quote-aware parser already rejects commas outside a
quoted value through its token and delimiter checks, so the blanket precheck
incorrectly rejects otherwise valid JSON response metadata.

Reference: https://www.rfc-editor.org/rfc/rfc9110#section-5.6.6

## Requirements

- Accept commas inside a syntactically valid quoted Content-Type parameter.
- Continue rejecting combined or otherwise ambiguous Content-Type values with
  unquoted commas.
- Preserve JSON subtype validation, UTF-8 charset enforcement, quote escaping,
  response-size limits, redirect rejection, and strict UTF-8 body decoding.
- Add focused JVM coverage and mutation-sensitive portable contracts.

## Scope Boundaries

- Do not broaden accepted media types, accept non-UTF-8 charsets, change HTTP
  transport behavior, alter dependencies, or contact a live backend.
- Do not replace the existing parameter parser or introduce a new parser
  abstraction for this single delimiter correction.

## Implementation Units

### U1: Let the quote-aware parser own comma validation

**Files:** `app/src/main/java/twitterdev/airquality/NetworkRequest.java`,
`app/src/test/java/twitterdev/airquality/NetworkRequestTest.java`

**Approach:** Remove the blanket comma rejection and add a valid quoted-comma
fixture alongside the existing combined-value rejection. Rely on the existing
token and post-quoted-value delimiter checks to continue rejecting commas
outside quoted strings.

**Execution note:** Test-first with the existing media-type JVM test.

**Verification:** The new valid fixture fails before the source change and
passes afterward, while the existing ambiguous comma fixture remains rejected.

### U2: Preserve the fail-closed repository contract

**Files:** `scripts/check_airquality_android_contracts.py`, `README.md`,
`SECURITY.md`, `CHANGES.md`, `docs/plans/2026-06-15-quoted-content-type-commas.md`

**Approach:** Require the valid quoted-comma fixture, removal of the blanket
precheck, maintained documentation, and completed verification evidence.

**Verification:** Isolated mutations to the source boundary, positive fixture,
negative fixture, documentation, and plan completion are rejected.

## Verification Plan

- Run the focused JVM media-type test and the full Android lint/test/build gate.
- Run every portable Make alias and the absolute-Makefile check from an
  external working directory.
- Run isolated hostile mutations for quoted and unquoted comma handling,
  documentation, and completed-plan evidence.
- Audit the exact diff, generated artifacts, suspicious secret patterns,
  structured files, and whitespace before committing.

## Work Completed

- Removed the blanket comma rejection from Content-Type validation so the
  existing quote-aware parameter parser owns delimiter decisions.
- Added a valid quoted-comma parameter fixture while preserving the existing
  combined unquoted comma rejection.
- Updated portable contracts to require the source boundary, both fixtures,
  maintained guidance, and completed plan evidence.

## Verification Completed

- The focused JVM media-type test failed at the new fixture before the source
  change, then the positive and negative media-type tests passed together.
- The full Android lint, test, and debug assembly gate passed under Java 8 and
  API 22; all 13 NetworkRequest tests passed on debug and release variants and
  Android lint retained one pre-existing warning with no errors.
- Repository and external working directory `make check` gates passed.
- Five isolated hostile mutations covering the blanket source precheck,
  quoted-comma fixture, combined-value fixture, documentation, and completed
  plan evidence were rejected; the restored checker passed.
- Structured-file, exact-diff, whitespace, suspicious-secret, and
  secret and generated-artifact scan passed.
