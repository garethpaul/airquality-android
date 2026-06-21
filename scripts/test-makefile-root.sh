#!/bin/sh
set -eu

ROOT=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
MAKEFILE=$ROOT/Makefile
TEMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/airquality-android-make-authority.XXXXXX")
TEST_ENTRYPOINT="$ROOT/scripts/.run-make-test.$$"
trap 'rm -rf "$TEMP_ROOT"; rm -f "$TEST_ENTRYPOINT"' EXIT HUP INT TERM

CONTROL_DIR="$TEMP_ROOT/control dir"
mkdir -p "$CONTROL_DIR"
LOG="$TEMP_ROOT/commands.log"
FAKE_PYTHON="$TEMP_ROOT/python tool"
FAKE_GRADLE="$TEMP_ROOT/gradle tool"
AUTHORITY_FAILURES=0

cat > "$FAKE_PYTHON" <<'EOF'
#!/bin/sh
printf 'python:%s\n' "$*" >> "$AIRQUALITY_ANDROID_COMMAND_LOG"
EOF
cat > "$FAKE_GRADLE" <<'EOF'
#!/bin/sh
printf 'gradle:%s\n' "$*" >> "$AIRQUALITY_ANDROID_COMMAND_LOG"
EOF
chmod +x "$FAKE_PYTHON" "$FAKE_GRADLE"

make_test_entrypoint() {
  make_command=$1
  /usr/bin/awk -v make_command="$make_command" '
    { sub("/usr/bin/make", make_command); print }
  ' "$ROOT/scripts/run-make.sh" > "$TEST_ENTRYPOINT"
  chmod +x "$TEST_ENTRYPOINT"
}

expect_entrypoint_rejection() {
  label=$1
  output=$2
  marker=$3
  shift 3
  rm -f "$marker"
  if (cd "$CONTROL_DIR" && /bin/sh "$TEST_ENTRYPOINT" "$@") > "$output" 2>&1; then
    printf 'RED: canonical entrypoint accepted %s\n' "$label" >&2
    AUTHORITY_FAILURES=$((AUTHORITY_FAILURES + 1))
  fi
  if [ -e "$marker" ]; then
    printf 'RED: canonical entrypoint allowed %s to execute\n' "$label" >&2
    AUTHORITY_FAILURES=$((AUTHORITY_FAILURES + 1))
  fi
}

run_make() {
  (export ANDROID_HOME; cd "$CONTROL_DIR" && AIRQUALITY_ANDROID_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "GRADLE=$FAKE_GRADLE" "$@")
}

run_entrypoint_with_zero() {
  synthetic_zero=$1
  shift
  /bin/sh -c 'entrypoint=$1; shift; . "$entrypoint"' "$synthetic_zero" "$ROOT/scripts/run-make.sh" "$@"
}

: > "$LOG"
ANDROID_HOME='' run_make lint test > "$TEMP_ROOT/check.out"
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
STARTUP_MARKER="$TEMP_ROOT/startup-executed"
cat > "$STARTUP" <<EOF
\$(shell /usr/bin/touch '$STARTUP_MARKER')
MAKEFILES :=
MAKEFLAGS :=
MFLAGS :=
MAKEOVERRIDES :=
EOF
(cd "$CONTROL_DIR" && MAKEFILES="$STARTUP" /usr/bin/make --no-print-directory -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "GRADLE=$FAKE_GRADLE" lint) > "$TEMP_ROOT/startup.out" 2>&1 || :
test -f "$STARTUP_MARKER"

rm -f "$STARTUP_MARKER"
if ! (cd "$CONTROL_DIR" && AIRQUALITY_ANDROID_COMMAND_LOG="$LOG" PYTHON="$FAKE_PYTHON" GRADLE="$FAKE_GRADLE" MAKEFILES="$STARTUP" MAKEFLAGS=-s MFLAGS=-s MAKEOVERRIDES=hostile GNUMAKEFLAGS=-s /bin/sh "$ROOT/scripts/run-make.sh" lint) > "$TEMP_ROOT/sanitized-startup.out" 2>&1; then
  exit 1
fi
test ! -e "$STARTUP_MARKER"

PATH_REDIRECT_ROOT="$TEMP_ROOT/path-redirect"
PATH_REDIRECT_BIN="$TEMP_ROOT/path-bin"
PATH_REDIRECT_MARKER="$TEMP_ROOT/path-redirect-executed"
mkdir -p "$PATH_REDIRECT_ROOT/scripts" "$PATH_REDIRECT_BIN"
cat > "$PATH_REDIRECT_ROOT/Makefile" <<EOF
lint:
	@/usr/bin/touch '$PATH_REDIRECT_MARKER'
EOF
cat > "$PATH_REDIRECT_BIN/dirname" <<'EOF'
#!/bin/sh
printf '%s\n' "$AIRQUALITY_ANDROID_PATH_REDIRECT_ROOT/scripts"
EOF
chmod +x "$PATH_REDIRECT_BIN/dirname"
if ! (cd "$CONTROL_DIR" && AIRQUALITY_ANDROID_PATH_REDIRECT_ROOT="$PATH_REDIRECT_ROOT" PATH="$PATH_REDIRECT_BIN:$PATH" /bin/sh "$ROOT/scripts/run-make.sh" lint) > "$TEMP_ROOT/path-redirect.out" 2>&1; then
  printf '%s\n' 'canonical entrypoint failed with an untrusted PATH' >&2
  AUTHORITY_FAILURES=$((AUTHORITY_FAILURES + 1))
fi
if [ -e "$PATH_REDIRECT_MARKER" ]; then
  printf '%s\n' 'RED: PATH-substituted dirname redirected the repository root' >&2
  AUTHORITY_FAILURES=$((AUTHORITY_FAILURES + 1))
fi

SYMLINK_ROOT="$TEMP_ROOT/symlink-checkout"
SYMLINK_MARKER="$TEMP_ROOT/symlink-root-executed"
mkdir -p "$SYMLINK_ROOT/scripts"
cat > "$SYMLINK_ROOT/Makefile" <<EOF
lint:
	@/usr/bin/touch '$SYMLINK_MARKER'
EOF
ln -s "$ROOT/scripts/run-make.sh" "$SYMLINK_ROOT/scripts/run-make.sh"
if ! (cd "$CONTROL_DIR" && /bin/sh "$SYMLINK_ROOT/scripts/run-make.sh" lint) > "$TEMP_ROOT/symlink-root.out" 2>&1; then
  printf '%s\n' 'canonical entrypoint failed through an external symlink' >&2
  AUTHORITY_FAILURES=$((AUTHORITY_FAILURES + 1))
fi
if [ -e "$SYMLINK_MARKER" ]; then
  printf '%s\n' 'RED: external symlink invocation selected the symlink directory' >&2
  AUTHORITY_FAILURES=$((AUTHORITY_FAILURES + 1))
fi

LF_SYMLINK_ROOT="$TEMP_ROOT/lf-symlink-checkout"
LF_SYMLINK_MARKER="$TEMP_ROOT/lf-symlink-root-executed"
LF_TARGET_NAME='physical
'
mkdir -p "$LF_SYMLINK_ROOT/scripts"
cat > "$LF_SYMLINK_ROOT/Makefile" <<EOF
lint:
	@/usr/bin/touch '$LF_SYMLINK_MARKER'
EOF
ln -s "$ROOT/scripts/run-make.sh" "$LF_SYMLINK_ROOT/scripts/$LF_TARGET_NAME"
ln -s "$LF_TARGET_NAME" "$LF_SYMLINK_ROOT/scripts/run-make.sh"
if ! (cd "$CONTROL_DIR" && /bin/sh "$LF_SYMLINK_ROOT/scripts/run-make.sh" lint) > "$TEMP_ROOT/lf-symlink-root.out" 2>&1; then
  printf '%s\n' 'canonical entrypoint failed through a trailing-LF symlink target' >&2
  AUTHORITY_FAILURES=$((AUTHORITY_FAILURES + 1))
fi
if [ -e "$LF_SYMLINK_MARKER" ]; then
  printf '%s\n' 'RED: trailing-LF symlink target redirected the repository root' >&2
  AUTHORITY_FAILURES=$((AUTHORITY_FAILURES + 1))
fi

MIXED_SYMLINK_ROOT="$TEMP_ROOT/mixed-symlink-checkout"
MIXED_SYMLINK_MARKER="$TEMP_ROOT/mixed-symlink-root-executed"
MIXED_TARGET_NAME="physical target's
middle"
mkdir -p "$MIXED_SYMLINK_ROOT/scripts"
cat > "$MIXED_SYMLINK_ROOT/Makefile" <<EOF
lint:
	@/usr/bin/touch '$MIXED_SYMLINK_MARKER'
EOF
ln -s "$ROOT/scripts/run-make.sh" "$MIXED_SYMLINK_ROOT/scripts/$MIXED_TARGET_NAME"
ln -s "$MIXED_TARGET_NAME" "$MIXED_SYMLINK_ROOT/scripts/run-make.sh"
if ! (cd "$CONTROL_DIR" && /bin/sh "$MIXED_SYMLINK_ROOT/scripts/run-make.sh" lint) > "$TEMP_ROOT/mixed-symlink-root.out" 2>&1; then
  printf '%s\n' 'canonical entrypoint failed through a space, quote, and internal-newline symlink chain' >&2
  AUTHORITY_FAILURES=$((AUTHORITY_FAILURES + 1))
fi
if [ -e "$MIXED_SYMLINK_MARKER" ]; then
  printf '%s\n' 'RED: mixed-byte symlink target redirected the repository root' >&2
  AUTHORITY_FAILURES=$((AUTHORITY_FAILURES + 1))
fi

BROKEN_SYMLINK_ROOT="$TEMP_ROOT/broken-symlink-checkout"
BROKEN_SYMLINK_MARKER="$TEMP_ROOT/broken-symlink-root-executed"
mkdir -p "$BROKEN_SYMLINK_ROOT/scripts"
cat > "$BROKEN_SYMLINK_ROOT/Makefile" <<EOF
lint:
	@/usr/bin/touch '$BROKEN_SYMLINK_MARKER'
EOF
ln -s missing-target "$BROKEN_SYMLINK_ROOT/scripts/run-make.sh"
if (cd "$CONTROL_DIR" && run_entrypoint_with_zero "$BROKEN_SYMLINK_ROOT/scripts/run-make.sh" lint) > "$TEMP_ROOT/broken-symlink.out" 2>&1; then
  printf '%s\n' 'RED: broken symlink invocation unexpectedly succeeded' >&2
  AUTHORITY_FAILURES=$((AUTHORITY_FAILURES + 1))
fi
if [ -e "$BROKEN_SYMLINK_MARKER" ]; then
  printf '%s\n' 'RED: broken symlink invocation executed an external Makefile' >&2
  AUTHORITY_FAILURES=$((AUTHORITY_FAILURES + 1))
fi

OVERLONG_SYMLINK_ROOT="$TEMP_ROOT/overlong-symlink-checkout"
OVERLONG_SYMLINK_MARKER="$TEMP_ROOT/overlong-symlink-root-executed"
mkdir -p "$OVERLONG_SYMLINK_ROOT/scripts"
cat > "$OVERLONG_SYMLINK_ROOT/Makefile" <<EOF
lint:
	@/usr/bin/touch '$OVERLONG_SYMLINK_MARKER'
EOF
ln -s "$ROOT/scripts/run-make.sh" "$OVERLONG_SYMLINK_ROOT/scripts/link-41"
link_number=40
while [ "$link_number" -ge 1 ]; do
  next_link=$((link_number + 1))
  ln -s "link-$next_link" "$OVERLONG_SYMLINK_ROOT/scripts/link-$link_number"
  link_number=$((link_number - 1))
done
ln -s link-1 "$OVERLONG_SYMLINK_ROOT/scripts/run-make.sh"
if (cd "$CONTROL_DIR" && run_entrypoint_with_zero "$OVERLONG_SYMLINK_ROOT/scripts/run-make.sh" lint) > "$TEMP_ROOT/overlong-symlink.out" 2>&1; then
  printf '%s\n' 'RED: overlong symlink invocation unexpectedly succeeded' >&2
  AUTHORITY_FAILURES=$((AUTHORITY_FAILURES + 1))
fi
if [ -e "$OVERLONG_SYMLINK_MARKER" ]; then
  printf '%s\n' 'RED: overlong symlink invocation executed an external Makefile' >&2
  AUTHORITY_FAILURES=$((AUTHORITY_FAILURES + 1))
fi

make_test_entrypoint /usr/bin/make

EXTRA_MAKEFILE="$TEMP_ROOT/extra.mk"
EXTRA_MAKEFILE_MARKER="$TEMP_ROOT/extra-makefile-executed"
cat > "$EXTRA_MAKEFILE" <<EOF
attack:
	@/usr/bin/touch '$EXTRA_MAKEFILE_MARKER'
EOF
expect_entrypoint_rejection \
  'an extra -f makefile' \
  "$TEMP_ROOT/extra-makefile.out" \
  "$EXTRA_MAKEFILE_MARKER" \
  -f "$EXTRA_MAKEFILE" attack

ASSIGNMENT_MARKER="$TEMP_ROOT/assignment-executed"
expect_entrypoint_rejection \
  'a Make-control variable assignment' \
  "$TEMP_ROOT/assignment.out" \
  "$ASSIGNMENT_MARKER" \
  -f "$MAKEFILE" \
  "MAKEFILES=\$(shell /usr/bin/touch '$ASSIGNMENT_MARKER')" \
  lint

GNU_MAKE=
for candidate in /opt/homebrew/bin/gmake /usr/local/bin/gmake "$(command -v gmake 2>/dev/null || true)"; do
  if [ -n "$candidate" ] && [ -x "$candidate" ] && "$candidate" --version 2>/dev/null | grep -Eq '^GNU Make 4\.'; then
    GNU_MAKE=$candidate
    break
  fi
done

if [ -n "$GNU_MAKE" ]; then
  make_test_entrypoint "$GNU_MAKE"

  EVAL_MARKER="$TEMP_ROOT/eval-executed"
  expect_entrypoint_rejection \
    'GNU Make 4.x --eval' \
    "$TEMP_ROOT/eval.out" \
    "$EVAL_MARKER" \
    "--eval=\$(shell /usr/bin/touch '$EVAL_MARKER')" \
    lint

  if "$GNU_MAKE" --help 2>/dev/null | grep -Fq -- '-E STRING'; then
    SHORT_EVAL_MARKER="$TEMP_ROOT/short-eval-executed"
    expect_entrypoint_rejection \
      'GNU Make 4.x -E' \
      "$TEMP_ROOT/short-eval.out" \
      "$SHORT_EVAL_MARKER" \
      -E \
      "\$(shell /usr/bin/touch '$SHORT_EVAL_MARKER')" \
      lint
  fi

  GNUMAKEFLAGS_MARKER="$TEMP_ROOT/gnumakeflags-executed"
  rm -f "$GNUMAKEFLAGS_MARKER"
  if ! (cd "$CONTROL_DIR" && GNUMAKEFLAGS="--eval=\$(shell /usr/bin/touch '$GNUMAKEFLAGS_MARKER')" /bin/sh "$TEST_ENTRYPOINT" lint) > "$TEMP_ROOT/gnumakeflags.out" 2>&1; then
    printf '%s\n' 'canonical entrypoint rejected a valid target after clearing GNUMAKEFLAGS' >&2
    AUTHORITY_FAILURES=$((AUTHORITY_FAILURES + 1))
  fi
  if [ -e "$GNUMAKEFLAGS_MARKER" ]; then
    printf '%s\n' 'RED: canonical entrypoint allowed inherited GNUMAKEFLAGS=--eval to execute' >&2
    AUTHORITY_FAILURES=$((AUTHORITY_FAILURES + 1))
  fi
fi

test "$AUTHORITY_FAILURES" -eq 0

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

printf '%s\n' 'Make authority tests passed: external root, SDK-free and SDK-backed tool selection, 2 raw Make-syntax controls, startup caller-authority proof, sanitized canonical entrypoint, PATH and byte-safe symlink root resistance including trailing and internal newlines, broken and overlong symlink failure, strict target-only entrypoint, GNU Make 4.x eval controls when available, later recipe rejection, caller MAKEFLAGS rejection, and 10 unsafe mode rejections'
