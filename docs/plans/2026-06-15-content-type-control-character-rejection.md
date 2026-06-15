# Content-Type Control Character Rejection

Status: Planned

## Problem

The Android response media-type parser distinguishes valid HTTP whitespace
(space and tab) with `skipHttpWhitespace`, but then calls Java `String.trim()`
on the media type, parameter names, and unquoted parameter values. `trim()`
also removes carriage returns, line feeds, and other ASCII control characters,
so malformed `Content-Type` syntax can be normalized into an accepted JSON
media type instead of failing closed.

## Priorities

1. P0: Reject carriage return, line feed, and other non-OWS controls anywhere
   they currently survive through `trim()` normalization.
2. P1: Preserve valid space/tab formatting, quoted parameters, UTF-8 charset
   enforcement, and JSON structured-suffix media types.
3. P1: Add executable and static mutation-sensitive contracts for each parser
   boundary changed.

## Requirements

1. Leading or trailing CR/LF/control characters around the media type must be
   rejected.
2. Control characters around parameter names or unquoted values must be
   rejected rather than trimmed away.
3. Space and horizontal tab must remain the only accepted optional HTTP
   whitespace around delimiters.
4. Existing quoted-value validation, escaped-character handling, duplicate
   charset rejection, UTF-8-only charset policy, and duplicate header rejection
   must remain unchanged.
5. The response body must not be consumed when media-type validation fails.
6. Tests, documentation, the SDK-free checker, and this plan must preserve the
   completed behavior and truthful verification evidence.

## Implementation Units

### U1: Replace Broad Trimming

**File:** `app/src/main/java/twitterdev/airquality/NetworkRequest.java`

Use the existing HTTP-whitespace semantics to normalize only space and tab.
Keep media-type/token validation explicit and reject every other control
character before response body reads.

### U2: Add Parser Regressions

**File:** `app/src/test/java/twitterdev/airquality/NetworkRequestTest.java`

Cover CR, LF, vertical tab, form feed, and other control characters around the
media type, parameter names, and unquoted values. Retain positive controls for
space/tab formatting and quoted parameters.

### U3: Preserve Durable Contracts

**Files:** `scripts/check_airquality_android_contracts.py`, `AGENTS.md`,
`README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`, and this plan.

Require the narrow whitespace helper, parser integration, focused tests,
maintained guidance, completed plan status, and verification evidence.

## Test Scenarios

- `application/json` with valid space/tab delimiter formatting remains valid.
- Leading and trailing CR or LF are rejected.
- CR, LF, vertical tab, and form feed adjacent to parameter names are rejected.
- The same controls adjacent to unquoted parameter values are rejected.
- Quoted parameters retain their existing control-character and escape rules.
- Duplicate headers and duplicate/non-UTF-8 charsets remain rejected.
- Full repository validation passes from repository and external directories.

## Scope Boundaries

- Do not replace Apache HTTP, `AsyncTask`, Gradle, Fabric, TwitterKit, or the
  application endpoint.
- Do not change response size, timeout, redirect, UTF-8, JSON parsing, location,
  or lifecycle behavior.
- Do not broaden accepted media types or parameter syntax.
- Emulator, physical-device, and live provider behavior remain outside local
  validation.

## Verification

- Run focused `NetworkRequestTest` coverage before the complete gate.
- Run repository and external-directory `make check` with the configured JDK
  and Android SDK environment.
- Reject isolated mutations that restore broad `trim()` behavior, remove
  control-character cases, weaken guidance, or falsify plan completion.
- Audit generated Gradle/build artifacts, exact diff, credentials, dependency
  and workflow drift, conflict markers, and whitespace before commit.
