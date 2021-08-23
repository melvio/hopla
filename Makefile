

## installing hopla ##
install:
	sudo ./install.sh


## first time hopla usage ##
## note: On some machines, this command might require a restart of your terminal
##       to load the commands on your $PATH
configure:
	hopla set-hopla credentials


# iso-date for tomorrow: YYYY-MM-DD
tomorrow="$$(date --iso-8601 --date=tomorrow)"
hopla_add_todo_checklist_tomorrow:
	hopla add todo --difficulty medium --due-date $(tomorrow) --checklist-file ~/todo/todo_list/checklist.md "$(tomorrow) checklist"

hopla_add_todo_checklist_studroll:
	hopla add todo --difficulty medium --due-date $(tomorrow) --checklist-file ~/todo/todo_list/roll.md "$(tomorrow) stud"


today="$$(date --iso-8601)"
hopla_add_todo_checklist_today:
	hopla add todo --difficulty medium --due-date $(today) --checklist-file ~/todo/todo_list/today.md "$(today) checklist"

hopla_add_todo_no_checklist:
	hopla add todo --difficulty hard --due-date $$(date --iso-8601)  "my todo thingy here"


hopla_enable_debug:
	hopla set-hopla config debug_enabled 1

hopla_disable_debug:
	hopla set-hopla config debug_enabled 0

hopla_buy_armoire:
	hopla buy enchanted-armoire

hopla_buy_armoire10:
	hopla buy enchanted-armoire --times 10


hopla_version:
	hopla version

hopla_api_status:
	hopla api status

hopla_api_version:
	hopla api version


# hopla get-user auth
hopla_get_user_auth:
	hopla get user-auth \
	&& hopla get user-auth all \
	&& hopla get-user-auth email \
	&& hopla get user-auth username \
	&& hopla get user-auth profile \
	&& hopla get user-auth --jq-filter '.timestamps.created'

# hopla get-user stats
hopla_get_user_stats:
	hopla get user-stats \
	&& hopla get user-stats all  \
    && hopla get user-stats --help \
    && hopla get user-stats \
    && hopla get user-stats manapoints \
    && hopla get user-stats experience \
    && hopla get user-stats gold \
    && hopla get user-stats -j '.class'


hopla_get_user_items:
	hopla get user-items \
	&& hopla get user-items --help \
	&& hopla get user-items all \
	&& hopla get user-items pets \
	&& hopla get user-items mounts \
	&& hopla get user-items food \
	&& hopla get user-items -j '.lastDrop'
