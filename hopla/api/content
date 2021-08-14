#!/usr/bin/env bash

source "${library_dir}/api_proxy.sh"
source "${library_dir}/logging.sh"

set -o errexit
set -o nounset
set -o pipefail


_get_all_api_content() {
  debug "get_api_content"
  get_curl "content"
}

get_api_content_with_filter(){
  declare -r jq_filter="$1"
  debug "get_api_content_with_filter filter=${jq_filter}"

  _get_all_api_content | jq "${jq_filter}"
}



parse_cmdline_args() {
  declare -i cur_arg=0
  declare -ra commandline_args=("$@")
  while (( cur_arg < $# )) ; do
    case "${commandline_args[${cur_arg}]}" in
     -j|--jq-filter)
        cur_arg+=1
        jq_filter=${commandline_args[${cur_arg}]:?"missing a FILTER for '-j/--jq-filter {FILTER}'"}
        get_api_content_with_filter "${jq_filter}"
        ;;
      *)
        echo "did not recognize argument: '${commandline_args[${cur_arg}]}'"
        exit 1
      esac
      cur_arg+=1
    done
}


main () {
  if (( $# == 0 )) ; then
    get_api_content_with_filter "."
  else
    parse_cmdline_args "$@"
  fi
}
main "$@"
