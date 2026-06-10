# Network Response Size Limit

Status: Completed

## Context

The legacy Android client used `BasicResponseHandler`, which materialized the
entire backend response before JSON parsing and did not make accepted HTTP
status codes explicit. A compromised or misconfigured endpoint could therefore
consume excessive memory or return an error document to the JSON path.

## Changes

- Accept only HTTP 2xx responses.
- Reject declared or streamed response bodies larger than 1 MiB.
- Close the entity stream and shut down the legacy HTTP connection manager.
- Decode UTF-8 only after the byte limit has been enforced.
- Pin hosted verification to Ubuntu 24.04 with superseded-run cancellation.
- Make SDK-free and optional Gradle verification root-independent.

## Verification

- `make check`
- Root-independent `make test`
- Static mutation checks for status, size, cleanup, CI, and Make paths
- `git diff --check`
