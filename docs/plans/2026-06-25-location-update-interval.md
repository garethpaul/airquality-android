# Location Update Interval Correction

Status: Completed

## Problem

`MainActivity` declared a ten-second minimum location update interval but did
not use it. Network and GPS listeners were registered with literal values of 10
and 3 milliseconds, respectively. When no last-known location was available,
that could request near-continuous callbacks until the activity paused or a
usable location arrived.

## Scope

- Require both provider registrations to use `MIN_TIME_BETWEEN_UPDATES`.
- Preserve the existing ten-metre distance threshold, provider selection,
  last-known-location behavior, request gating, and lifecycle cleanup.
- Add a portable contract that fails if either provider returns to a literal
  interval.

## Verification

- Run the contract before the source correction and confirm it fails for both
  literal provider intervals.
- Run `python scripts/check_airquality_android_contracts.py` after the fix.
- Run `/bin/sh scripts/run-make.sh check` for the complete SDK-free gate.
- Mutate each provider registration independently and confirm the contract
  rejects both regressions.
- Require the hosted Android and CodeQL checks on the exact pull-request head.

## Boundary

This change does not alter permissions, provider choice, accepted coordinates,
backend requests, authentication, dependencies, or the ten-metre distance
threshold. Device-level callback cadence and power impact remain part of the
authorized device verification matrix.
