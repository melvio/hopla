
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
* [DONE] add project structure with proper imports
* [DONE] click autocomplete
* [DONE] Use click's context classes
* [DONE] get error checking for wrong commands
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


# TODO make goal list for hopla
# personal goals:
# -- full vim integration for todos, habits, and, tasks
# -- cast spells automaticallyu
# -- feed pets automatically (just one command to feed all favorite
#                             available to all pets available, no unfavorable feeding though)
#
# user focused:
# -- no 'dangerous' interactions  without confirmation (e.g. sending gems)
# -- interactivity when info is missing
# -- near complete autocompletion for all options arguments
# -- pipy installation
# -- password login
# -- open up habitica to get apiToken
# -- move userid to hopla.conf
# --
# -- easiest possible CLI setup
# -- completely automate habitica chores
#    * feed pets automatically
#    * accept quests
#    * buy enchanged armoire
#      + get summary autoput
# -- background infroamtion
# -- vim integration in any habitica task that requires typing
# -- CLI quest interactivity
# -- TODO MORE
# TODO
# -- respond to chats with vim integration (incl. smiley support that is better than habitica self)
# -- -- see if vim has smiley integration (wanted feature: type in :smiley: -> see actual smiley)

# development focused
# -- 95%+ test coverage
# -- high code quality (both linting and design)
# -- The above in a CI pipeline
