#!/usr/bin/env bash


set -o errexit
set -o nounset
set -o pipefail

source "${library_dir}/logging.sh"
source "${library_dir}/user_data.sh"


get_all_items(){
  get_curl_user_with_filter ".data.items"
}
get_pet(){
  get_curl_user_with_filter ".data.items.pets"
}

get_mount(){
  get_curl_user_with_filter ".data.items.mounts"
}
get_food(){
  get_curl_user_with_filter ".data.items.food"
}


main () {
  if (( $# == 0 )) ; then
    get_all_items
  else
    case "$1" in
      -j|--jq-filter)
        jq_filter=${2:?"missing a FILTER for '-j/--jq-filter [FILTER]'"}
        get_curl_user_with_filter ".data.items${jq_filter}" ;;
      pets)
        get_pet
        ;;
      mounts)
        get_mount
        ;;
      food)
        get_food
        ;;
      all)
        # same behavior as passing no arguments
        get_all_items
        ;;
      *) echo "did not recognize argument: '$1'"
    esac
  fi
}
main "$@"






