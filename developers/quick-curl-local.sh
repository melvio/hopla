#!/usr/bin/env bash

# Note: make sure you have a user_id and api_token in ../localhost.env
this_script=$(perl -e 'use Cwd "abs_path"; print abs_path(shift)' "$0")
this_script_parent_dir=$(realpath "$(dirname "${this_script}")/..")
source "${this_script_parent_dir}/localhost.env"

curl -XGET "http://localhost:8080/api/v3/user?userFields=achievements.streak,purchased.plan" \
  --verbose \
  --header "Content-Type: application/json" \
  --header "x-api-user: ${user_id}" \
  --header "x-api-key: ${api_token}" \
  --header "x-client: Testing" | jq .


curl -XPOST "http://localhost:8080/api/v3/debug/set-cron" \
  --verbose \
  --header "Content-Type: application/json" \
  --header "x-api-user: ${user_id}" \
  --header "x-api-key: ${api_token}" \
  --header "x-client: Testing" | jq .
