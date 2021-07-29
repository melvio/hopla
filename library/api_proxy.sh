#!/usr/bin/env bash

readonly x_client_header="79551d98-31e9-42b4-b7fa-9d89b0944319-hopla"
readonly domain="https://habitica.com"
export api_version="v3"
api_base_url="${domain}/api/${api_version}"


get_curl() {
  url_path="$1"

  curl --silent "${api_base_url}/${url_path}" --compressed \
    --header "Content-Type: application/json" \
    --header "x-api-user: ${user_id}" \
    --header "x-api-key: ${api_token}" \
    --header "x-client: ${x_client_header}"
}


post_curl() {
  url_path="$1"
  json_data="$2"

  curl --silent -XPOST "${api_base_url}/${url_path}" \
    --header "Content-Type: application/json" \
    --header "x-api-user: ${user_id}" \
    --header "x-api-key: ${api_token}" \
    --header "x-client: ${x_client_header}" \
    --data "${json_data}"
}
