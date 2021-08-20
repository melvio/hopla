#!/usr/bin/env bash

source "${library_dir}/logging.sh"
source "${library_dir}/api_proxy.sh"


set -o errexit
set -o nounset
set -o pipefail

declare -i option_until_poor_enabled=0
declare -i option_times_value=1  # call buy enchanted-armoire once by default

_parse_options() {
  declare -ra args=("$@")
  for i in "${!args[@]}" ; do
    case "${args[i]}" in
    --until-poor|-u)
        option_until_poor_enabled=1 ;;
    --times|-t)
        option_times_value=${args[$(( i + 1 ))]}
        ;;
    esac
  done
}

_validate_options() {
  if (( option_times_value < 1 )) ; then
    echo "cannot set buy from the armoire less than 1 times"
    exit 1
  fi
}

handle_options() {
  debug "handle_options"
  _parse_options "$@"
  _validate_options
}


display_buy_attempt_result() {
  debug "display_buy_attempt_result"
  declare -r http_response="$1"

  declare -r success=$( echo "${http_response}" | jq '.success')
  if [[ "${success}" == "true" ]] ; then
     echo "${http_response}" | jq --raw-output .data.armoire
  else
     echo "${http_response}" | jq --raw-output .message
  fi

}

_buy_from_armoire() {
  debug "_buy_from_armoire"
  declare -r path="user/buy-armoire"
  declare -r http_response=$( post_curl "${path}" )

  display_buy_attempt_result "${http_response}"
}

buy_from_armoire_n_times() {
  declare -ri n_times="$1"
  debug "buy_from_armoire_n_times n=${n_times}"

  for ((i=0 ; i < n_times ; i++ )) ; do
    _buy_from_armoire
    if (( n_times > 25 )) ; then
      sleep 2s # self throttle slightly: you can only do 30 requests/minute
    fi
  done
}

buy_from_armoire_until_poor() {
  debug "buy_from_armoire_until_poor"
  gold=$(hopla get user-stats gold)
  declare -i gold=$(python3 -c "print(round(float(${gold})))")
  debug "user gold rounded down=${gold}"
  declare -ri buy_times=gold/100
  buy_from_armoire_n_times "${buy_times}"
}

main() {
  handle_options "$@"
  debug "buy enchanted-armoire: poor_enabled=${option_until_poor_enabled}, times=${option_times_value}"

  if (( option_until_poor_enabled == 0 )) ; then
    buy_from_armoire_n_times "${option_times_value}"
  else
    buy_from_armoire_until_poor
  fi
}
main "$@"



