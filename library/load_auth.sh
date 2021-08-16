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
debug "auth_file=${auth_file_path}"



read_credentials() {
  debug "read_credentials auth_file=${auth_file_path:-}"

  if [[ -f ${auth_file_path} ]]; then
    while read -r line ; do
      if echo "${line}" | grep --silent ".*=.*" ; then
    # TODO: UUID syntax checking
        export "${line}"
      fi
    done < "${auth_file_path}"


    if [[ -z "${user_id:-}" || -z "${api_token}" ]]; then
      echo "no credentials found:"
      "${script_dirname}/set/credentials"
    fi
  else
    echo "no credential file found"
    "${script_dirname}/set/credentials"
  fi
}
read_credentials
