

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

hopla_add_todo_no_checklist:
	hopla add todo --hard --due-date $$(date '+%Y-%m-%d')  "my todo thingy here"



hopla_version:
	./hopla/hopla version

hopla_api_status:
	hopla api status

hopla_api_version:
	hopla api version


