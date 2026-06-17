# Credential-Aware Twitter Login Startup Guard

Status: Completed

## Problem

The public repository intentionally keeps its Twitter consumer credentials
blank. `AirQualityApplication` therefore skips `Fabric.with(...)`, but the
exported launcher immediately calls `Twitter.getSessionManager()` from
`LoginActivity.onCreate()`. TwitterKit 1.5.1 checks Fabric initialization in
that call and throws `IllegalStateException` when the kit was not started, so
the checked-in credential-free application can crash as soon as it launches.

## Priorities

1. P0: Keep the exported launcher alive when TwitterKit was intentionally not
   initialized because credentials are unavailable.
2. P1: Preserve the existing authenticated-session redirect and configured
   Twitter login callback behavior.
3. P1: Add executable static and mutation-sensitive evidence that the
   application and launcher share one initialization boundary.

## Requirements

1. The credential decision must have one package-visible source of truth in
   `AirQualityApplication`; `LoginActivity` must not duplicate blank-string
   credential logic.
2. `LoginActivity` must determine whether TwitterKit is available before any
   call to `Twitter.getSessionManager()` or login-button callback setup.
3. When TwitterKit is unavailable, the launcher must remain open, avoid all
   TwitterKit session APIs, explicitly disable the unusable login control, and
   show a concise configuration-unavailable message.
4. When TwitterKit is available, an active session must still open
   `MainActivity`, while an absent session must still configure the existing
   login callback.
5. The guard must not catch and suppress unrelated runtime failures from an
   initialized TwitterKit path.
6. Checked-in credentials and Fabric metadata must remain blank; dependencies,
   SDK levels, permissions, workflow behavior, and network behavior must not
   change.
7. The SDK-free checker, maintained guidance, changelog, and this plan must
   preserve the completed behavior and truthful verification evidence.

## Implementation Units

### U1: Expose the Initialization Decision

**File:** `app/src/main/java/twitterdev/airquality/AirQualityApplication.java`

Make the existing credential predicate package-visible and name it for the
TwitterKit availability decision. Continue using the same predicate before
`Fabric.with(...)` so application initialization and launcher behavior cannot
drift apart.

### U2: Guard Launcher Authentication Setup

**Files:** `app/src/main/java/twitterdev/airquality/LoginActivity.java`,
`app/src/main/res/values/strings.xml`

Check the shared predicate before touching TwitterKit. In the unavailable
path, leave the activity usable, explicitly disable the login button, and
present a maintained string-resource message. Keep the configured path's
session redirect and callback setup unchanged.

### U3: Add Durable Contracts

**Files:** `scripts/check_airquality_android_contracts.py`, `README.md`,
`SECURITY.md`, `VISION.md`, `CHANGES.md`, and this plan.

Require the shared predicate, guard-before-session ordering, credential-free
UI state, unchanged configured flows, maintained guidance, completed plan
status, and actual verification evidence. Add isolated hostile mutations that
remove, reorder, duplicate, or weaken the guard and its user-visible state.

## Test Scenarios

- Blank checked-in credentials make the application skip Fabric and make the
  launcher avoid `Twitter.getSessionManager()`.
- The unavailable launcher disables the login control and renders the
  configuration message without navigating away.
- Configured credentials with an active session still navigate directly to
  `MainActivity`.
- Configured credentials without a session still attach the success/failure
  callback to the login button.
- Removing the shared predicate, moving the session lookup before the guard,
  or restoring an interactive unusable button fails the maintained gate.
- Repository and external-directory gates remain green.

## Scope Boundaries

- Do not add, generate, log, or commit Twitter/Fabric credentials.
- Do not replace TwitterKit, Fabric, Gradle, Apache HTTP, or the Android
  activity architecture in this change.
- Do not bypass authentication by opening `MainActivity` when TwitterKit is
  unavailable.
- Do not broadly catch `IllegalStateException`; the known unavailable state is
  represented by the shared initialization predicate.
- Emulator, physical-device, live Twitter authentication, and provider
  behavior remain outside local validation.

## Verification

- Run the SDK-free checker first to prove the new contract fails before the
  implementation and passes afterward.
- Run repository and external-directory `make check` with explicit timeouts
  and the configured Java 8/Android SDK environment.
- Reject isolated mutations that remove or reorder the shared guard, duplicate
  credential logic, retain an interactive unavailable login control, remove
  the message, weaken guidance, or falsify plan completion.
- Audit generated Gradle/build artifacts, exact diff, credentials, dependency
  and workflow drift, conflict markers, file modes, and whitespace before
  commit.

## Completed Verification

- The installed TwitterKit 1.5.1 bytecode confirmed that
  `Twitter.getSessionManager()` throws when `Fabric.with(...)` has not started
  the kit, reproducing the checked-in credential boundary without live auth.
- The SDK-free checker failed before implementation on the missing shared
  predicate, guard ordering, unavailable UI, and completed-plan contracts.
- The focused `AirQualityApplicationTest` passed under Java 8 and API 22.
- Android lint, debug and release unit tests, and debug assembly passed; lint
  retained only the documented legacy target-SDK modernization warning.
- Repository and external-directory `make check`, eleven hostile mutations, exact
  diff, generated-artifact, dependency/workflow drift, and credential scan
  results are recorded by the final validation pass.
- No emulator, physical device, live Twitter authentication, or provider
  behavior was exercised or claimed.
