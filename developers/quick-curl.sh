#!/usr/bin/env bash

# Note: make sure you have a user_id and api_token in ../developer.env
this_script=$(perl -e 'use Cwd "abs_path"; print abs_path(shift)' "$0")
this_script_parent_dir=$(realpath "$(dirname "${this_script}")/..")
source "${this_script_parent_dir}/developer.env"


curl -XGET "https://habitica.com/api/v3/user?userFields=achievements,items.mounts" \
  --verbose \
  --header "Content-Type: application/json" \
  --header "x-api-user: ${user_id}" \
  --header "x-api-key: ${api_token}" \
  --header "x-client: Testing" | jq .


