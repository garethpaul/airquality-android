# Strict Response UTF-8 Decoding

Status: Completed

## Problem

The bounded backend response is decoded with
`ByteArrayOutputStream.toString("UTF-8")`. Java replaces malformed byte
sequences with U+FFFD by default, so corrupted provider bytes are altered and
passed to JSON parsing instead of failing at the response boundary.

## Requirements

1. Decode the already-bounded response bytes with a UTF-8 decoder configured
   to report malformed and unmappable input.
2. Preserve HTTP status checks, declared and streamed size limits, input-stream
   closure, connection-manager shutdown, and generic request logging.
3. Add focused unit coverage for valid UTF-8 and malformed-byte rejection.
4. Require the strict decoder, regression names, documentation, and completed
   plan evidence in the portable checker.
5. Pass bounded local and external portable gates plus hosted Android checks.

## Implementation Units

### 1. Characterize the decode boundary

Add direct package-level tests proving valid JSON bytes decode unchanged and
an invalid UTF-8 sequence raises `IOException` rather than being replaced.

### 2. Decode strictly after size enforcement

Move byte-to-text conversion into a small package-visible helper backed by a
UTF-8 `CharsetDecoder` with malformed and unmappable input set to `REPORT`.
Keep stream ownership and all request behavior unchanged.

### 3. Protect and document the contract

Extend the portable checker with source, unit-test, documentation, required
plan, and completed-status contracts. Document strict provider response
decoding in the maintenance, security, project-priority, and change guidance.

## Verification

Completed on 2026-06-14:

- The two focused JUnit calls first failed compilation because `decodeUtf8`
  did not exist, then the complete Gradle unit-test task passed after the
  strict decoder was implemented.
- The portable checker passed against an unmodified disposable copy with this
  plan marked complete.
- Eight focused mutations were rejected: malformed-input action,
  unmappable-input action, strict-helper use, regression name, documentation,
  changelog documentation, completed plan status, and plan presence.
- Python compilation and `git diff --check` passed before the full repository
  gates.
- Bounded SDK-backed `make check` passed from the repository root and from
  `/tmp` through the absolute Makefile path. Both runs passed portable
  contracts, Android lint, debug and release unit tests, and debug assembly;
  Android lint retained one existing non-fatal issue in each variant.

## Scope Boundaries

- Do not change response byte limits, timeouts, endpoints, JSON semantics,
  dependencies, Android UI behavior, or workflow coverage.
- Do not merge or close any pull request without explicit owner authorization.
