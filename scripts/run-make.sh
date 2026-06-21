#!/bin/sh
set -eu

case $0 in
  /*) script_path=$0 ;;
  *) script_path=$(/bin/pwd -P)/$0 ;;
esac

link_count=0
while [ -L "$script_path" ]; do
  link_count=$((link_count + 1))
  if [ "$link_count" -gt 40 ]; then
    printf '%s\n' 'repository verification entrypoint has too many symbolic links' >&2
    exit 66
  fi

  link_target=$(/usr/bin/readlink "$script_path")
  case $link_target in
    /*) script_path=$link_target ;;
    *) script_path=$(/usr/bin/dirname "$script_path")/$link_target ;;
  esac
done

script_dir=$(CDPATH='' cd -P "$(/usr/bin/dirname "$script_path")" && /bin/pwd -P)
ROOT=$(CDPATH='' cd -P "$script_dir/.." && /bin/pwd -P)

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
