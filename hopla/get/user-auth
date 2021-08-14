#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

source "${library_dir}/logging.sh"
source "${library_dir}/user_data.sh"


get_all_auth(){
  get_curl_user_with_filter ".data.auth"
}

# these .data.auth.local filters probably only work
# if you use email-based authentication. Logging
# in with e.g. google probably breaks down. (not sure though)
get_local_auth_info(){
  # username, lowerCaseUserName, and email
  get_curl_user_with_filter ".data.auth.local"
}

get_email(){
  get_curl_user_with_filter ".data.auth.local.email"
}

get_username(){
  get_curl_user_with_filter ".data.auth.local.username"
}


get_profile(){
  # profile is not really auth data according to the API, but
  # it fits better here, imho.
  get_curl_user_with_filter ".data.profile"
}



main () {
  debug "hopla get user-auth $*"

  if (( $# == 0 )) ; then
    get_local_auth_info
  else
    case $1 in
      -j|--jq-filter)
        local jq_filter=${2:?"missing a FILTER for '-j/--jq-filter [FILTER]'"}
        get_curl_user_with_filter ".data.auth${jq_filter}"
        ;;
      all)
        get_all_auth
        ;;
      email|e-mail|mail)
        get_email
        ;;
      username|name)
        get_username
        ;;
      profilename|profile)
        get_profile
        ;;
      *) echo "did not recognize argument: '$1'"
    esac
  fi
}
main "$@"
