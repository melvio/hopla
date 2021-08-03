#!/usr/bin/env bash

debug_enabled="${debug_enabled:-0}"

debug () {
  message="$1"
  if [[ "${debug_enabled}" != 0 ]] ; then
    echo "[DEBUG] ${message}" >&2
  fi
}
