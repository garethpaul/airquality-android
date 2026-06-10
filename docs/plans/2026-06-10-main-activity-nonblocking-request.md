# MainActivity Nonblocking Air-Quality Request

Status: Completed

## Context

`MainActivity.onCreate` started `NetworkRequest` and immediately called
`AsyncTask.get()`. Although the HTTP operation ran on a worker, that wait
blocked the Android UI thread until the request completed or timed out, making
startup unresponsive on slow or unavailable networks.

## Changes

- Apply the air-quality state from `NetworkRequest.onPostExecute` on the main
  thread.
- Remove synchronous `AsyncTask.get()` handling and its unused response field.
- Preserve the existing unknown-state fallback for failed or malformed
  responses.
- Add an SDK-free contract that rejects a reintroduced blocking wait and
  requires the completion callback.

## Verification

- `make check`
- Static mutation check for reintroduced `request.get()`
- `git diff --check`
