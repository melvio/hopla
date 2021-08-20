#!/usr/bin/env bash

source "${library_dir}/logging.sh"

set -o errexit
set -o nounset
set -o pipefail

declare -r config_key="${1:?"missing config_key and config_value"}"
declare -r config_value="${2:?"missing config_value"}"

create_config_file() {
  debug "create_config_file"
  local config_dir_name=${config_file_path%/*}
  mkdir --parents "${config_dir_name}"
  touch "${config_file_path}"

  echo "created an configuration file called '${config_file_path}'"
  echo "If you want to use another file, set an environment variable called HOPLA_CONFIG_FILE."
}

config_key_is_in_file() {
  # return 0 on match (or error), 1 no match
  grep --silent "^${config_key}=" "${config_file_path}"
  return $?
}

update_configuration() {
  debug "update_configuration"
  if [[ ! -f ${config_file_path} ]] ; then
      create_config_file
  fi

  declare -r config_line="${config_key}=${config_value}"
  if config_key_is_in_file ; then
    # replace current value
    sed --in-place "s/^${config_key}.*/${config_line}/" "${config_file_path}"
  else
    # append the new configuration
    echo "${config_line}" >> "${config_file_path}"
  fi
}


main() {
  update_configuration
}
main



