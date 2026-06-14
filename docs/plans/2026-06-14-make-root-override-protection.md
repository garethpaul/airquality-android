# Make Root Override Protection

Status: Planned

## Problem

The Makefile-derived repository root anchors the portable checker, Gradle
wrapper, and optional Android build, but an ordinary assignment can be
replaced by a command-line `ROOT` value and redirect verification away from
the reviewed checkout.

## Requirements

1. Protect the derived root with GNU Make's `override` directive.
2. Preserve configurable Python and Gradle commands.
3. Require exact protected-root, tool-override, checker, wrapper, and rooted
   Android build contracts in the portable checker.
4. Pass local, external-working-directory, and hostile-root portable gates.
5. Reject focused root, tool, path, and completed-plan mutations.

## Verification

- Compile and run the portable checker first.
- Run bounded local, external-working-directory, and hostile `ROOT` full
  `make check` gates.
- Run the wrapper verification contract and the Android gate when the SDK is
  available; otherwise record the explicit local skip and require hosted proof.
- Run focused mutations plus workflow, Gradle, XML, artifact, whitespace, and
  changed-line credential audits.

## Scope Boundaries

- Do not change Android behavior, Gradle/dependency versions, workflows,
  manifests, resources, or public APIs.
- Do not merge or close any pull request without explicit owner authorization.
