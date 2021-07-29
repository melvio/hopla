#!/usr/bin/env bash

readonly x_client_header="79551d98-31e9-42b4-b7fa-9d89b0944319-hopla"
readonly domain="https://habitica.com"
export api_version="v3"
api_base_url="${domain}/api/${api_version}"



# Prevent overloading the habitica API by using an exponential backoff algorithm.
# Specifically, retry on failure at respectively 1, 2, 4, 8, 16, 32, 64, 128, and 256 seconds
readonly curl_retry=9
readonly curl_retry_max_time=260

get_curl() {
  url_path="$1"

  http_response=$(curl --silent --show-error "${api_base_url}/${url_path}" --compressed \
    --retry "${curl_retry}" \
    --retry-max-time "${curl_retry_max_time}" \
    --header "Content-Type: application/json" \
    --header "x-api-user: ${user_id}" \
    --header "x-api-key: ${api_token}" \
    --header "x-client: ${x_client_header}")
  echo "${http_response}"
}

post_curl() {
  url_path="$1"
  json_data="$2"

  http_response=$(curl --silent --show-error -XPOST "${api_base_url}/${url_path}" \
    --retry "${curl_retry}" \
    --retry-max-time "${curl_retry_max_time}" \
    --header "Content-Type: application/json" \
    --header "x-api-user: ${user_id}" \
    --header "x-api-key: ${api_token}" \
    --header "x-client: ${x_client_header}" \
    --data "${json_data}")
  echo "${http_response}"
}
