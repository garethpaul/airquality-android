#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
MAKEFILE=$ROOT/Makefile
TEMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/airquality-android-make-authority.XXXXXX")
trap 'rm -rf "$TEMP_ROOT"' EXIT HUP INT TERM

CONTROL_DIR="$TEMP_ROOT/control dir"
mkdir -p "$CONTROL_DIR"
LOG="$TEMP_ROOT/commands.log"
FAKE_PYTHON="$TEMP_ROOT/python tool"
FAKE_GRADLE="$TEMP_ROOT/gradle tool"

printf '%s\n' '#!/bin/sh' 'printf "python:%s\\n" "$*" >> "$AIRQUALITY_ANDROID_COMMAND_LOG"' > "$FAKE_PYTHON"
printf '%s\n' '#!/bin/sh' 'printf "gradle:%s\\n" "$*" >> "$AIRQUALITY_ANDROID_COMMAND_LOG"' > "$FAKE_GRADLE"
chmod +x "$FAKE_PYTHON" "$FAKE_GRADLE"

run_make() {
  (export ANDROID_HOME; cd "$CONTROL_DIR" && AIRQUALITY_ANDROID_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "GRADLE=$FAKE_GRADLE" "$@")
}

: > "$LOG"
ANDROID_HOME= run_make lint test > "$TEMP_ROOT/check.out"
grep -Fq "python:-m py_compile $ROOT/scripts/check_airquality_android_contracts.py" "$LOG"
grep -Fq "python:$ROOT/scripts/check_airquality_android_contracts.py" "$LOG"

: > "$LOG"
ANDROID_HOME="$TEMP_ROOT/sdk" run_make build > "$TEMP_ROOT/build.out"
grep -Fq 'gradle:lint test assembleDebug --no-daemon' "$LOG"

for variable in PYTHON GRADLE; do
  if (cd "$CONTROL_DIR" && /usr/bin/make --no-print-directory -f "$MAKEFILE" "$variable=\$(shell false)" lint) > "$TEMP_ROOT/syntax.out" 2>&1; then
    exit 1
  fi
  grep -Fq "$variable must be a literal value, not Make syntax" "$TEMP_ROOT/syntax.out"
done

STARTUP="$TEMP_ROOT/startup.mk"
printf '%s\n' '$(error startup file executed)' > "$STARTUP"
if (cd "$CONTROL_DIR" && MAKEFILES="$STARTUP" /usr/bin/make --no-print-directory -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "GRADLE=$FAKE_GRADLE" lint) > "$TEMP_ROOT/startup.out" 2>&1; then
  exit 1
fi
grep -Eq 'startup file executed|MAKEFILES must be empty' "$TEMP_ROOT/startup.out"

LATER="$TEMP_ROOT/later.mk"
printf '%s\n' 'lint:' '>@printf replaced' > "$LATER"
if (cd "$CONTROL_DIR" && /usr/bin/make --no-print-directory -f "$MAKEFILE" -f "$LATER" "PYTHON=$FAKE_PYTHON" "GRADLE=$FAKE_GRADLE" lint) > "$TEMP_ROOT/later.out" 2>&1; then
  exit 1
fi

if (cd "$CONTROL_DIR" && /usr/bin/make --no-print-directory -f "$MAKEFILE" MAKEFLAGS=-n "PYTHON=$FAKE_PYTHON" "GRADLE=$FAKE_GRADLE" lint) > "$TEMP_ROOT/flags.out" 2>&1; then
  exit 1
fi
grep -Fq 'MAKEFLAGS must not be overridden' "$TEMP_ROOT/flags.out"

for flag in -n --just-print --dry-run --recon -t --touch -q --question -i --ignore-errors; do
  if (cd "$CONTROL_DIR" && /usr/bin/make "$flag" --no-print-directory -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "GRADLE=$FAKE_GRADLE" lint) > "$TEMP_ROOT/mode.out" 2>&1; then
    exit 1
  fi
  grep -Fq 'non-executing or error-ignoring MAKEFLAGS are not supported' "$TEMP_ROOT/mode.out"
done

printf '%s\n' 'Make authority tests passed: external root, SDK-free and SDK-backed tool selection, 2 raw Make-syntax controls, startup-file rejection, later recipe rejection, caller MAKEFLAGS rejection, and 10 unsafe mode rejections'
