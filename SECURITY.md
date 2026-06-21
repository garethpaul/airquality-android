# Security Policy

## Supported Versions

The supported security scope for `airquality-android` is the current default branch, `master`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained.

Project summary: AirQuality App for Android

The public credential-free build must keep TwitterKit initialization, launcher
session access, and login activity-result forwarding behind the same
configuration predicate. The launcher disables login and reports the unavailable
configuration instead of invoking an uninitialized authentication SDK.

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/airquality-android` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

LoginActivity is the only exported launcher; MainActivity is explicitly non-exported and reached with an explicit in-app intent.

- This repository appears to be an Android mobile application or sample. The active security scope is the code and documentation on the default branch.
- Review found authentication, token, or session-related code paths; changes in those areas should receive security-focused review before merge.
- Review found external API integrations or credential-adjacent configuration; changes in those areas should receive security-focused review before merge.
- Review found network clients, sockets, web APIs, or service endpoints; changes in those areas should receive security-focused review before merge.
- Review found mobile permission or privacy-sensitive data handling; changes in those areas should receive security-focused review before merge.
- Review found file, document, data, or media parsing flows; changes in those areas should receive security-focused review before merge.
- Review found database, model, query, or persistence-related code; changes in those areas should receive security-focused review before merge.
- Review found infrastructure, deployment, proxy, or cloud configuration; changes in those areas should receive security-focused review before merge.
- Dependency manifests detected: build.gradle, gradle.properties. Dependency updates should preserve lockfiles when present and avoid introducing packages without a clear maintenance reason.
- Fabric/Twitter initialization should stay disabled when checked-in credential
  placeholders are blank.
- Android app-data backup should stay disabled by default because this sample
  handles location and Twitter/Fabric app state.
- IDE workspace metadata should stay untracked so local SDK paths, launch
  settings, and editor preferences are not committed.
- Pinned, read-only GitHub Actions jobs run `/usr/bin/make check` across Python 3.10,
  3.12, and 3.14 so Android manifest, credential, location, sensor, and network
  guardrails stay enforced before merge.
- A separate hosted Java 8/API 22 job runs the complete Android gate, and the
  baseline pins and verifies the wrapper JAR and Gradle distribution checksums.
  An uncached bootstrap still depends on Gradle's HTTPS service.
- Backend responses must reject malformed UTF-8, return 2xx, use strict Content-Length
  syntax when supplied, and remain no larger than 1 MiB before
  JSON parsing; response streams and the legacy HTTP connection manager must be
  closed.
- Backend response reads fail when a stream reports zero progress instead of spinning indefinitely.
- Backend requests reject automatic redirects so intermediaries cannot move the
  fixed HTTPS request to another transport target.
- Validated location values are serialized as canonical decimal coordinates so
  Java-only numeric syntax is not forwarded to the backend parser; signed-zero coordinates normalize to `0.0`.
- Backend responses require JSON application media types before length checks
  or body access; missing, ambiguous, malformed, and non-JSON values fail
  closed without content sniffing.
- Backend responses must contain exactly one Content-Type header before body access.
- Response Content-Type parsing accepts only space and tab as optional HTTP whitespace; CR, LF, and other controls fail before body access.
- Response charset metadata must be absent or unambiguous UTF-8; malformed,
  duplicate, empty, and non-UTF-8 declarations fail before body access.
- Quoted Content-Type parameter values may contain commas; unquoted or combined
  comma values remain invalid.
- MainActivity accepts air_quality only when its JSON value is a nonblank string.
- MainActivity trims surrounding whitespace from nonblank air_quality strings.
- Generic NetworkRequest failure logs retain only stable protocol, JSON, and
  parameter categories. They do not pass dependency throwables to logcat,
  where stack traces or messages could expose coordinates, request URLs, or
  provider response details.
- Generic location acquisition failure logs do not pass platform throwables to
  logcat, where provider state, permission details, or device configuration
  could be exposed.
- `MainActivity` must clear and cancel its active backend request before pause
  and destruction, then ignore callbacks from stale, cancelled, finishing, or
  destroyed activity instances.
- Failed backend requests retain only an in-memory resume-time retry marker;
  pause must not discard it, and no coordinates or provider details are logged.
- `MainActivity` starts backend requests only after a non-null device location
  is available and stops location updates after acquisition, on pause, and
  during destruction.

## Mobile Privacy Notes

If this project requests device permissions such as location, camera, microphone, contacts, Bluetooth, health data, or local storage access, reports should describe the permission involved and whether sensitive data can be accessed, persisted, or transmitted unexpectedly. Please avoid testing against real third-party user data or accounts you do not control.

## Dependency and Supply Chain Security

Repository verification enters through `/bin/sh scripts/run-make.sh check`,
which clears inherited `MAKEFILES`, `MAKEFLAGS`, `MFLAGS`, and `MAKEOVERRIDES`
before fixed `/usr/bin/make`. GNU Make startup programs execute before the
repository Makefile can inspect them, so direct startup programs are caller
authority rather than repository-validated input. The Makefile freezes the
canonical checkout root, `/bin/sh`, and literal Python and Gradle selections,
and rejects later visible overrides and unsafe modes. Explicit extra makefiles
and literal Python and Gradle paths remain supported caller authority.

The generated Gradle 8.14.5 bootstrap retains the legacy Gradle 2.2.1 runtime
required by Android Gradle Plugin 1.2.3. Review all four wrapper files together;
the SDK-free baseline rejects drift from Gradle's published wrapper JAR and
distribution SHA-256 values.

TwitterKit's Retrofit transport intentionally receives pinned direct OkHttp,
URLConnection adapter, and Okio dependencies; do not remove them without
authenticated runtime migration evidence.

Dependency updates should come from trusted package managers and should keep lockfiles in sync when lockfiles exist. Do not commit credentials, private keys, tokens, generated secrets, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.
