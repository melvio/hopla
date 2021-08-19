#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

source "${library_dir}/logging.sh"
source "${library_dir}/user_data.sh"


get_all_stats() {
  get_curl_user_with_filter ".data.stats"
}

get_gp() {
  get_curl_user_with_filter ".data.stats.gp"
}

get_mp() {
  get_curl_user_with_filter ".data.stats.mp"
}

get_exp() {
  get_curl_user_with_filter ".data.stats.exp"
}

get_lvl() {
  get_curl_user_with_filter ".data.stats.lvl"
}



main () {
  debug "hopla get user-stats $*"

  if (( $# == 0 )) ; then
    get_all_stats
  else
    case $1 in
      -j|--jq-filter)
        local jq_filter=${2:?"missing a FILTER for '-j/--jq-filter [FILTER]'"}
        get_curl_user_with_filter ".data.stats${jq_filter}"
        ;;
      gp|gold)
        get_gp
        ;;
      mana-points|manapoints|mana|mp)
        get_mp
        ;;
      experience|exp|xp)
        get_exp
        ;;
      all)
        # Has the behavior as passing no argument.
        get_all_stats
        ;;
      *)
        echo "did not recognize argument: '$1'"
    esac
  fi
}
main "$@"


