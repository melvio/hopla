#!/usr/bin/env bash

development=1
if [[ "${development}" == 1 ]] ; then
  debug_enabled=1
#  set -x
else
  debug_enabled=0
fi

debug () {
  message="$1"
  if [[ "${debug_enabled}" != 0 ]] ; then
    echo "[DEBUG] ${message}" >&2
  fi
}
