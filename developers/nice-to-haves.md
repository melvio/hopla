
Nice to haves:

### BASH
* do error handling after curls
* add preserve whitespace option for checklist
* provide error checking on typos in options
* apply: <http://redsymbol.net/articles/unofficial-bash-strict-mode/>
* hopla add todo --checklist {relative_file.md}
* support with gems functionality
* get automatic completion improvements (
  + options
  + config options
* get error checking for wrong commands
* get quest info
* check uuid input format (or even ask the api for confirmation using .data.auth.nogiets)
* --background flag 



### Python
* let python handle --help and -h
* Use logging framework 
  + [DONE] add logging to entry command
  + Enable reading of $HOPLA_CONFIG_FILE to get debug settings
  + add python logging throughout the application
* Extract helper classes for common code
* consider @dataclasses for:
  + Environment data class 
  + Config data class 
  + Authorization data class
* add project structure with proper imports


### general

* --json flag for json and CLI-user friendly output by default
* Make this project installable with a respectable package manager (e.g. apt, pip, snap, flatpak)
* deeper nesting of the `hopla` folder, only have the main `hopla` command itself in the root directory
  * [DONE] hopla.sh and hopla.py in main folder
  * cleanup migratory files in main folder

