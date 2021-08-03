

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

hopla_add_todo_checklist_daily:
	hopla add todo --medium --due-date $$(date '+%Y-%m-%d') --checklist ~/checklist.md "$$(date '+%Y-%m-%d') + 1"


hopla_add_todo_no_checklist:
	hopla add todo --hard --due-date $$(date '+%Y-%m-%d')  "my todo thingy here"


hopla_enable_debug:
	hopla set config debug_enabled 1


hopla_version:
	./hopla/hopla version

hopla_api_status:
	hopla api status

hopla_api_version:
	hopla api version


