#!/usr/bin/env bash

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
      "${script_dirname}/hopla/set-hopla/credentials.sh"
    fi
  else
    echo "no credential file found"
    "${script_dirname}/hopla/set-hopla/credentials.sh"
  fi
}
read_credentials
