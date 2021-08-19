#!/usr/bin/env bash

set -o errexit
set -o pipefail

source "${library_dir}/api_proxy.sh"
source "${library_dir}/logging.sh"

# data that we want to send to the API for this
declare habitica_task_priority="1.0" # 1.0 is the default
declare habitica_text=""
declare habitica_date=""
declare checklist_file=""

parse_cmdline() {
  declare -i cur_arg=0
  declare -r commandline_args=("$@")
  for _ in "$@"; do
    case "${commandline_args[${cur_arg}]}" in
      --hard) habitica_task_priority="2" ;;
      --medium) habitica_task_priority="1.5" ;;
      --easy) habitica_task_priority="1" ;;
      --trivial) habitica_task_priority="0.1" ;;
      --due-date|--deadline)
        cur_arg+=1
        habitica_date=${commandline_args[${cur_arg}]}
        ;;
      --checklist)
        cur_arg+=1
        checklist_file=${commandline_args[${cur_arg}]}
        ;;
      *)
        habitica_text+=${commandline_args[${cur_arg}]}
        ;;
    esac
    cur_arg+=1
  done
}

print_task_id() {
  declare -r http_response_from_add_tasks_api_call="$1"
  echo "${http_response_from_add_tasks_api_call}" | jq --raw-output '.data.id'
}


turn_checklist_file_into_json(){
  debug "turn_checklist_file_into_json"
  # <https://habitica.fandom.com/wiki/Application_Programming_Interface#Version_3_of_the_API>
  declare -l checklist_json=" \"checklist\": ["

  while read -r task; do
    checklist_json+=" { \"text\":"
    checklist_json+=" \"${task}\" "
    checklist_json+=" },"
  done < "${checklist_file}"
  checklist_json="${checklist_json::-1}" # remove last ','
  checklist_json+="]"

  echo "${checklist_json}"
}

post_todo() {
  debug "post_todo"
  # <https://habitica.com/apidoc/#api-Task-CreateUserTasks>

  post_data="{"
  post_data+="\"text\":\"${habitica_text}\", "
  post_data+="\"priority\":\"${habitica_task_priority}\", "
  if [[ -n "${habitica_date}" ]]; then
    post_data+="\"date\":\"${habitica_date}\", "
  fi
  if [[ -s "${checklist_file}" ]] ; then
    post_data+="$(turn_checklist_file_into_json), "
  fi

  declare -r habitica_type="todo"
  post_data+="\"type\":\"${habitica_type}\" "
  post_data+="}"

  declare -r path="tasks/user"
  http_response=$(post_curl "${path}" "${post_data}")
}


add_tasks_to_todo_checklist() {
  debug "add_tasks_to_todo_checklist"
  # <https://habitica.com/apidoc/#api-Task-AddChecklistItem>
  declare -r task_id="$1"
  declare -r post_json="$2"

  declare -r path="tasks/${task_id}/checklist"
  post_curl "${path}" "${post_json}"
}


validate_checklist_file_exists(){
  # validate checklist file if any
  if [[ -d "${checklist_file}" ]]; then
    echo "${checklist_file} is a directory"
    exit 1
  elif [[ ! -e "${checklist_file}" ]]; then
    echo "cannot find ${checklist_file}: try an absolute paths instead"
    exit 1
  elif [[ ! -s "${checklist_file}" ]]; then
    echo "${checklist_file}: seems to be empty, please try adding a checklist"
    exit 1
  fi
}

main() {
  parse_cmdline "$@"
  if [[ -n "${checklist_file}" ]]; then
    validate_checklist_file_exists
  fi
  post_todo
}

main "$@"
