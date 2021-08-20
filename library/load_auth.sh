#!/usr/bin/env bash


set_credentials_if_not_found() {
  if [[ -z "${user_id:-}" || -z "${api_token}" ]]; then
    echo "no credentials found:"
    "${script_dirname}/hopla/set-hopla/credentials.sh"
  fi
}
set_credentials_if_not_found
