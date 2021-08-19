#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

source "${library_dir}/logging.sh"


create_auth_file() {
  debug "create_auth_file"
  local auth_dir_name=${auth_file_path%/*}
  mkdir --parents "${auth_dir_name}"
  touch "${auth_file_path}"
  # section header for auth file
  echo "[credentials]" > "${auth_file_path}"

  echo "created an authentication file called '${auth_file_path}'"
  echo "If you want to use another file, set an environment variable called HOPLA_AUTH_FILE."
}

write_credential_file() {
  debug "write_credential_file"

  read -r -p "Please enter your habitica 'User ID': "   new_user_id
  read -r -p "Please enter your habitica 'API Token': " new_api_token
  # TODO: new_user_id and new_api_token not empty
  # TODO: validate UUID

  local -r user_id_auth_key="user_id"
  local -r api_token_auth_key="api_token"

  local -r user_id_auth_line="${user_id_auth_key}=${new_user_id}"
  local -r api_token_auth_line="${api_token_auth_key}=${new_api_token}"

  # TODO: extract duplicate logic (also look into config handling bash scripts)
  if grep --silent "^${user_id_auth_key}=" "${auth_file_path}" ; then
    sed --in-place "s/^${user_id_auth_key}.*/${user_id_auth_line}/" "${auth_file_path}"
  else
    echo "${user_id_auth_line}"    >>  "${auth_file_path}"
  fi

  if grep --silent "^${api_token_auth_key}=" "${auth_file_path}" ; then
    sed --in-place "s/^${api_token_auth_key}.*/${api_token_auth_line}/" "${auth_file_path}"
  else
    echo "${api_token_auth_line}" >> "${auth_file_path}"
  fi
}

main() {
  if [[ ! -f ${auth_file_path} ]] ; then
    create_auth_file
  fi

  write_credential_file
}
main


