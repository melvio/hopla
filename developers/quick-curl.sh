#!/usr/bin/env bash

# Note: make sure you have a user_id and api_token in ../developer.env
this_script=$(perl -e 'use Cwd "abs_path"; print abs_path(shift)' "$0")
this_script_parent_dir=$(realpath "$(dirname "${this_script}")/..")
source "${this_script_parent_dir}/developer.env"


# get all user info
#curl -XGET "https://habitica.com/api/v3/user" \
#  --verbose \
#  --header "Content-Type: application/json" \
#  --header "x-api-user: ${user_id}" \
#  --header "x-api-key: ${api_token}" \
#  --header "x-client: Testing" | jq .

# get user info by userFields
#curl -XGET "https://habitica.com/api/v3/user?userFields=achievements.streak,purchased.plan" \
#  --verbose \
#  --header "Content-Type: application/json" \
#  --header "x-api-user: ${user_id}" \
#  --header "x-api-key: ${api_token}" \
#  --header "x-client: Testing" | jq .

#curl -XGET "https://habitica.com/api/v3/content" \
#  --verbose \
#  --header "Content-Type: application/json" | jq .

#curl -XGET "https://habitica.com/api/v3/status" \
#  --verbose \
#  --header "Content-Type: application/json" | jq .



# [docs](https://habitica.com/apidoc/#api-User-UserFeed)
# [API PATH](https://habitica.com/api/v3/user/feed/:pet/:food)
# feed Beetle-Skeleton Fish x2
#curl -XPOST "https://habitica.com/api/v3/user/feed/Beetle-Skeleton/Fish?amount=2" \
#  --verbose \
#  --header "Content-Type: application/json" \
#  --header "x-api-user: ${user_id}" \
#  --header "x-api-key: ${api_token}" \
#  --header "x-client: Testing" | jq .

  # note: body is ignored:
#  --data '{ "amount" : 3 }' \  # --data is ignored

# response:
#{
#  "success": true,
#  "data": 15,                                                  <- feeding status after feeding
#  "message": "Skeleton Beetle really likes the Fish!",


# add TODO
curl -XPOST "https://habitica.com/api/v3/tasks/user" \
  --verbose \
  --header "Content-Type: application/json" \
  --header "x-api-user: ${user_id}" \
  --header "x-api-key: ${api_token}" \
  --header "x-client: Testing" \
  --data '{ "text":"Update Habitica API Documentation - Tasks", "type":"todo", "alias":"hab-api-tasks", "notes":"Update the tasks api on GitHub", "tags":["ed427623-9a69-4aac-9852-13deb9c190c3"], "checklist":[{"text":"read wiki","completed":true},{"text":"write code"}], "priority":2 }' | jq .
#  --data '{"text" :"My todo", "notes":"#### subheader", "checklist" : [ { "text": "gather tools", "completed": true }, { "text": "build shed", "completed": false} ], "type":"todo" }' | jq .

