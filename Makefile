


build:
	# https://setuptools.readthedocs.io/en/latest/userguide/quickstart.html
	python -m build && pip install .

develop:
	pip install --upgrade -e .


## first time hopla usage ##
## note: On some machines, this command might require a restart of your
##       terminal to load the commands on your $PATH
configure:
	hopla auth

enable_autocomplete:
	hopla complete bash --enable

print_autocomplete:
	hopla complete bash  \
	&& hopla complete zsh  \
	&& hopla complete fish

hopla_add_simple_todo:
	hopla add todo "Donate"

hopla_add_todo_hard_now_without_checklist:
	hopla add todo --difficulty hard --due-date $$(date --iso-8601)  "my todo thingy here"

# GNU date: iso-date for tomorrow: YYYY-MM-DD
tomorrow="$$(date --iso-8601 --date=tomorrow)"
hopla_add_todo_use_editor_for_checklist_tomorrow:
	hopla add todo --difficulty medium --due-date $(tomorrow) --editor "$(tomorrow) checklist"

hopla_add_todo_use_file_as_checklist:
	hopla add todo --difficulty medium --due-date $(tomorrow) --checklist ~/todo/todo_list/roll.md "$(tomorrow) studies"


today="$$(date --iso-8601)"
hopla_add_todo_checklist_today:
	hopla add todo --difficulty medium --due-date $(today) --checklist ~/todo/todo_list/today.md "$(today) checklist"



hopla_config_get_loglevel:
	hopla config 'cmd_all.loglevel'

hopla_enable_debug:
	hopla config 'cmd_all.loglevel' debug

hopla_disable_verbosity:
	hopla config 'cmd_all.loglevel' error

hopla_buy_armoire:
	hopla buy enchanted-armoire

hopla_buy_armoire10:
	hopla buy enchanted-armoire --times 10

hopla_buy_armoire_until_poor:
	hopla buy enchanted-armoire --until-poor


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
	&& hopla get user-auth email \
	&& hopla get user-auth username \
	&& hopla get user-auth profilename

# hopla get-user stats
hopla_get_user_stats:
	hopla get user-stats \
	&& hopla get user-stats all  \
    && hopla get user-stats --help \
    && hopla get user-stats \
    && hopla get user-stats manapoints \
    && hopla get user-stats experience \
    && hopla get user-stats gold \
    && hopla get user-stats class


hopla_get_user_inventory:
	hopla get user-inventory \
	&& hopla get user-inventory --help \
	&& hopla get user-inventory all \
	&& hopla get user-inventory pets \
	&& hopla get user-inventory mounts \
	&& hopla get user-inventory food \
	&& hopla get user-inventory lastDrop


hopla_get_user_info:
	hopla get user-info \
	&& hopla get user-info --filter 'profile' \
	&& hopla get user-info -f "achievements.streak,achievements.quests" \
	&& hopla get user-info -f 'flags.lastFreeRebirth, preferences.dayStart, preferences.timezoneOffset, auth.timestamps.created'

