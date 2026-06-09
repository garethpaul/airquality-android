# Login Button Lookup Guard

## Status: Completed

## Context

`LoginActivity.onActivityResult` already guards `loginButton` before forwarding
Twitter activity results, but `onCreate` still assumed the login button view was
present before setting the Twitter callback. A stale or malformed login layout
could therefore crash before the result guard mattered.

## Objectives

- Preserve successful Twitter login callback setup.
- Guard the login button lookup before setting callbacks.
- Log a clear non-fatal warning when the login button is unavailable.
- Keep existing active-session navigation behavior unchanged.

## Work Completed

- Wrapped `loginButton.setCallback(...)` in an `if (loginButton != null)` guard.
- Added a warning log for missing login button views.
- Extended the static contract checker for callback setup guards.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_airquality_android_contracts.py`
- `python3 -m py_compile scripts/check_airquality_android_contracts.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`

On this workspace, `make build` and `make check` reported
`Android SDK not configured; skipping Gradle build`.

## Follow-Up Candidates

- Add instrumentation coverage for a malformed login layout.
- Move login error strings into resources during a UI-copy pass.
