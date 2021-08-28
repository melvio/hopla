
Nice to haves:



### Python
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
* [DONE] click autocomplete
* Use click's context classes
* support with gems functionality
* get error checking for wrong commands
* get quest info
* get next free rebirth
* get gems
* hopla support-development cmd
* check uuid input format (or even ask the api for confirmation using .data.auth.nogiets)
* --background flag 
* --json flag for json and CLI-user friendly output by default
   * get consistent output (e.g. double quoted & consistent 2-space indentation)
* Make this project installable with a respectable package manager (pip)
  + [DONE] local pip install
  + add hopla to PyPi (Python Package Index)
* implement goal_bnf.md CLI 



CI-CD:
* [DONE] add pytest buildstep
* add doctest build-step:
  + [DONE] add step
  + update the step s.t. it automatically picks up doctest in all the right locations
* add pytest-cov
* 