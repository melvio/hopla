#!/usr/bin/env bash

set -o errexit
set -o nounset


install_dependencies() {
  if ! jq --version >> /dev/null ; then
    sudo apt install jq
  fi
  if ! curl --version >> /dev/null ; then
    sudo apt install curl
  fi
}
install_dependencies


cd -- "$(dirname "$0")" || exit 1
declare -r entry_command="$(realpath ./hopla_python_migration.py)"
declare -r link_name="/usr/local/bin/hopla"


if [[ -f "${entry_command}" ]] ; then
  if [[ -h "${link_name}" ]] ; then
    echo "symbolic link to hopla already exists in ${link_name}"
  else
    sudo ln --symbolic "${entry_command}" "${link_name}"
    echo "created symbolic link from ${link_name} -> ${entry_command}"
  fi
  exit 0
else
  echo "Could not find the hopla command here: ${entry_command}"
  exit 1
fi



