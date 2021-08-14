#!/usr/bin/env bash
source "${library_dir}/logging.sh"

declare -r x_client_header="79551d98-31e9-42b4-b7fa-9d89b0944319-hopla"
declare -r domain="https://habitica.com"
export api_version="v3"
declare -r api_base_url="${domain}/api/${api_version}"

# Prevent overloading the habitica API by using an exponential backoff algorithm.
# Specifically, retry on failure at respectively 1, 2, 4, 8, 16, 32, 64, 128, and 256 seconds
declare -ir curl_retry=9
declare -ir curl_retry_max_time=260

get_curl() {
  local -r url_path="$1"
  debug "get_curl ${url_path}"

  # Since curl 7.66.0, curl will comply with the Retry-After: response header if one
  # was present to know when to issue the next retry.
  # Ubuntu 20.04 uses curl 7.68 (anno July 2021)
  declare http_response=$(curl --silent --show-error "${api_base_url}/${url_path}" \
    --compressed \
    --retry "${curl_retry}" \
    --retry-max-time "${curl_retry_max_time}" \
    --header "Content-Type: application/json" \
    --header "x-api-user: ${user_id}" \
    --header "x-api-key: ${api_token}" \
    --header "x-client: ${x_client_header}")
  echo "${http_response}"
}

post_curl() {
  local -r url_path="$1"
  debug "post_curl ${url_path}"
  local -r json_data="${2:-}"

  declare http_response=$(curl --silent --show-error -XPOST "${api_base_url}/${url_path}" \
    --retry "${curl_retry}" \
    --retry-max-time "${curl_retry_max_time}" \
    --header "Content-Type: application/json" \
    --header "x-api-user: ${user_id}" \
    --header "x-api-key: ${api_token}" \
    --header "x-client: ${x_client_header}" \
    --data "${json_data}")
  echo "${http_response}"
}
