#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

source "${library_dir}/api_proxy.sh"
source "${library_dir}/logging.sh"

get_curl_user_with_filter () {
  local -r jq_filter="$1"
  debug "_get_curl_user ${jq_filter}"
  get_curl "user" | jq "${jq_filter}"
}
