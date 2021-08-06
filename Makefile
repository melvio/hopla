

## installing hopla ##
install:
	sudo ./install.sh


## first time hopla usage ##
## note: On some machines, this command might require a restart of your terminal
##       to load the commands on your $PATH
configure:
	hopla set credentials


## hopla CLI examples ##
hopla_add_todo_checklist:
	hopla add todo --hard --due-date 2021-07-31 --checklist ~/.local/share/hopla/fake_tasks.txt "my todo thingy here"

tomorrow="$$(date --date tomorrow '+%Y-%m-%d')"
hopla_add_todo_checklist_tomorrow:
	hopla add todo --medium --due-date $(tomorrow) --checklist ~/checklist.md $(tomorrow) checklist


hopla_add_todo_no_checklist:
	hopla add todo --hard --due-date $$(date '+%Y-%m-%d')  "my todo thingy here"


hopla_enable_debug:
	hopla set config debug_enabled 1

hopla_disable_debug:
	hopla set config debug_enabled 1


hopla_buy_armoire:
	hopla buy enchanted-armoire


hopla_version:
	./hopla/hopla version

hopla_api_status:
	hopla api status

hopla_api_version:
	hopla api version

hopla_get_user_info_pets:
	hopla get user-info pets

hopla_get_user_info_gold:
	hopla get user-info gp

hopla_get_user_info_stats:
	hopla get user-info stats
