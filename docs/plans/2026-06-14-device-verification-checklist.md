# Android Device Verification Checklist

Status: Completed

## Problem

Portable contracts cover the request and activity lifecycle, but the repository
does not define the emulator or physical-device evidence needed before claiming
that the legacy application works under Android lifecycle and permission events.

## Requirements

1. Add a repeatable device checklist for launch, credentials, permissions,
   location, backend responses, pause/resume, rotation, and process recreation.
2. Require captured toolchain, device, build, result, and log-redaction evidence.
3. Separate repository validation from unexecuted device scenarios.
4. Add mutation-sensitive contracts for the checklist and completion evidence.

## Scope Boundaries

- Do not modernize Gradle, Android APIs, Fabric, TwitterKit, or dependencies.
- Do not add real credentials, backend URLs, emulator images, APKs, or captured
  device data to git.
- Do not claim emulator or physical-device execution from Linux static checks.
- Do not merge or close stacked pull requests without explicit authorization.

## Verification

- `python3 -m py_compile scripts/check_airquality_android_contracts.py` and the
  focused contract checker passed.
- Repository-root and external-working-directory `make check` passed the
  portable contract gate and retained the existing bounded SDK behavior.
- Twelve hostile mutations were rejected for removing the checklist, exact
  commit evidence, build command, permission, lifecycle, backend, privacy,
  unexecuted-result, documentation, or completed-plan contracts.
- No emulator or physical-device scenario was executed; every runtime matrix
  row remains truthfully marked `not run`.
