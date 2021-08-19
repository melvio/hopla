#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

source "${library_dir}/logging.sh"
source "${library_dir}/user_data.sh"


get_all_user_info() {
  get_curl_user_with_filter "."
}



get_convenience_info () {
  local -r default_filter='.data.profile'
  get_curl_user_with_filter "${default_filter}"
}


main () {
  debug "hopla get user-info $*"

  if (( $# == 0 )) ; then
    get_convenience_info
  else
    case $1 in
      -j|--jq-filter)
        jq_filter=${2:?"missing a FILTER for '-j/--jq-filter [FILTER]'"}
        get_curl_user_with_filter "${jq_filter}" ;;
      # get all data
      all) get_all_user_info ;;
      # other
      *) echo "did not recognize argument: '$1'"
    esac
  fi
}
main "$@"


