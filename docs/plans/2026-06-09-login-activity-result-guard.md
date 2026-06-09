# Login Activity Result Guard

## Status: Completed

## Context

`LoginActivity` only initializes `loginButton` when no Twitter session is
active. If the activity later receives an activity-result callback while an
existing session skipped login-button setup, the callback could dereference a
null button.

## Objectives

- Preserve Twitter login callback forwarding for unauthenticated sessions.
- Avoid dereferencing `loginButton` when the active-session path skipped setup.
- Keep the lifecycle guard covered by SDK-free static checks.

## Work Completed

- Guarded `loginButton.onActivityResult(...)` with a null check.
- Added static checker coverage for the guarded activity-result path.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_airquality_android_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add an instrumentation test for the active-session login path.
- Replace legacy Fabric/Twitter login dependencies in a dedicated migration.
