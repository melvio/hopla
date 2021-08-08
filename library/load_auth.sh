#!/usr/bin/env bash

print_hopla_auth_file() {
  local file_path=
  if [[ -n "${HOPLA_AUTH_FILE:-}" && -f "${HOPLA_AUTH_FILE:-}" ]] ; then
    file_path="${HOPLA_AUTH_FILE}"
  elif [[ -n "${XDG_CONFIG_HOME:-}" && -d "${XDG_CONFIG_HOME:-}" ]] ; then
    file_path="${XDG_CONFIG_HOME}/hopla/auth.conf"
  else
    file_path="${HOME}/.config/hopla/auth.conf"
  fi
  echo "${file_path}"
}
declare -xr auth_file_path=$(print_hopla_auth_file)
debug "auth_file_path ${auth_file_path}"



read_credentials() {
  debug "read_credentials"
  if [[ -f ${auth_file_path} ]]; then
    source "${auth_file_path}"
    # TODO: syntax checking
    export user_id="${auth_file_user_id:?"user id is not set in the credentials file"}"
    export api_token="${auth_file_api_token:?"api token is not set in the credentials file"}"

    if [[ -z "${user_id}" || -z "${api_token}" ]]; then
      echo "no credentials found:"
      "${script_dirname}/set/credentials"
    fi
  else
    echo "no credential file found"
    "${script_dirname}/set/credentials"
  fi
}
read_credentials
