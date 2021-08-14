#!/usr/bin/env bash

print_dir_of_this_script(){
  local this_script=$(perl -e 'use Cwd "abs_path"; print abs_path(shift)' "$0")
  local this_script_dir=$(dirname "${this_script}")
  echo "${this_script_dir}"
}

main () {
  cat "$(print_dir_of_this_script)/hopla.bash-completion"
}
main
