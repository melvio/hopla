#!/usr/bin/env bash

cd -- "$(dirname "$0")" || exit 1
entry_command="$(realpath ./hopla/hopla)"
target_dir="/usr/local/bin/"


if [[ -f "${entry_command}" && -d "${target_dir}" ]] ; then
  if [[ -h "${target_dir}/hopla" ]] ; then
    echo "symbolic link already exists in ${target_dir}"
  else
    sudo ln -s "${entry_command}" "${target_dir}"
  fi
  exit 0
else
  echo "Could not find the hopla command here: ${entry_command}"
  exit 1
fi



