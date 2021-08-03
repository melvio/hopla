#!/usr/bin/env bash


print_hopla_config_file() {
  local file_path=
  if [[ -n "${HOPLA_CONFIG_FILE:-}" && -f "${HOPLA_CONFIG_FILE:-}" ]] ; then
    file_path="${HOPLA_CONFIG_FILE}"
  elif [[ -n "${XDG_CONFIG_HOME:-}" && -d "${XDG_CONFIG_HOME:-}" ]] ; then
    file_path="${XDG_CONFIG_HOME}/hopla/hopla.conf"
  else
    file_path="${HOME}/.config/hopla/hopla.conf"
  fi
  echo "${file_path}"
}

read_configs() {
  debug "read_configs"
  if [[ -f ${config_file_path} ]]; then
    while read -r config_setting ; do
      # we want to export every line of the config file
      # shellcheck disable=SC2163
      export "${config_setting}"
    done < "${config_file_path}"
  else
    debug "config file ${config_file_path} is not a file"
  fi
}

main (){
  declare -xgr config_file_path=$(print_hopla_config_file)
  debug "config_file_path: ${config_file_path}"
  read_configs
}
main


