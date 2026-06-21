#!/bin/sh
set -eu

ROOT=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)

if [ "$#" -ne 1 ]; then
  printf '%s\n' 'usage: scripts/run-make.sh check|lint' >&2
  exit 64
fi

case $1 in
  check|lint)
    target=$1
    ;;
  *)
    printf 'unsupported repository verification target: %s\n' "$1" >&2
    exit 64
    ;;
esac

exec /usr/bin/env \
  -u MAKEFILES \
  -u MAKEFLAGS \
  -u MFLAGS \
  -u MAKEOVERRIDES \
  -u GNUMAKEFLAGS \
  /usr/bin/make --no-print-directory -f "$ROOT/Makefile" "$target"
