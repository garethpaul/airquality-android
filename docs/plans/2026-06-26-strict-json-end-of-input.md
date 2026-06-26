# Strict JSON End Of Input

Status: Completed

## Problem

Android documents `JSONTokener` as intentionally lenient, and direct
`JSONObject(String)` construction does not establish that the entire backend
body was consumed. A valid object followed by another value or garbage could
therefore be accepted as the air-quality response.

## Decision

Parse one value with `JSONTokener.nextValue()`, require a `JSONObject`, then
consume the remainder while accepting only JSON's space, tab, carriage-return,
and line-feed whitespace. `nextClean()` is deliberately not used because the
Android parser documents that it skips comments. Trailing comments, values,
arrays, and garbage are rejected.

Official API reference:
<https://developer.android.com/reference/org/json/JSONTokener>

## Verification

- The portable contract failed first for the missing strict parser and transport
  routing.
- Android unit coverage accepts trailing whitespace and rejects another value,
  arbitrary text, and a non-object root.
- Full portable `make check`, hosted Android, CodeQL, and exact-head review
  evidence is recorded before merge.
- Pull request #30 implementation head
  `2c2b85c9e59660531e46d8dc2bd89a44757fa274` passed hosted Android
  verification, Python 3.10/3.12/3.14 checks, all CodeQL analyses, and the
  aggregate gate.
- Required Codex review stopped before analysis because OpenAI WebSocket and
  HTTPS transports returned HTTP 401. Immutable head comparison and manual
  fallback review found no actionable defects.
