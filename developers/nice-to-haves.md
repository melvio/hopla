
Nice to haves:



### Python
* Use logging framework 
  + [DONE] add logging to entry command
  + [DONE] Enable reading of $HOPLA_CONFIG_FILE to get debug settings
  + [DONE] add python logging throughout the application
* Extract helper classes for common code
* consider @dataclasses for:
  + Environment data class 
  + Config data class 
  + Authorization data class
* add project structure with proper imports
* [DONE] click autocomplete
* Use click's context classes
* get error checking for wrong commands
* get quest info
* get next free rebirth
* [DONE] get gems
* [DONE] hopla support-development cmd
* [DONE] check uuid input format 
* after authenticate: ask the API for user info
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
* [DONE] add pytest-cov
  + increase coverage to 40%
  + increase coverage to 60%
  + increase coverage to 80%
  + increase coverage to 90%