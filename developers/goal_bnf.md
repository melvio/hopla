

Goal structure for stable release:
```bash
hopla                     -- gets help
hopla --help              -- gets help
hopla {subcmd} --help     -- gets subcmd help

# global options:
hopla --debug {...}       -- provide debug logging (if not already enabled in config)

hopla version             -- gets hopla version

# hopla config
hopla config --list                   -- lists all config params
hopla config {key}                    -- prints specified config value in config file
hopla config {key} {value}            -- sets specified config key to value in config file

# hopla login
hopla login                           -- authorize yourself by providing uuid and api token
hopla login --browser                 -- authorize yourself by loging in with a browser

# hopla set
hopla set day-start [n]               -- set cron day start at the n-th hour (default: 0)

# hopla feed
All these should have a --json option:
    hopla feed {pet} {food}                    -- feed {pet} with {food} once
    hopla feed {pet} {food} --amount N         -- feed {pet} with {food} n times 
    hopla feed {pet} {food} --until-mount      -- feed {pet} with {food} until it is a mount
    hopla feed {pet} --favorite                -- feed {pet} with favorite food once
    hopla feed {pet} --favorite --until-mount  -- feed {pet} with favorite food until it is a mount (or favorite food runs out)
    hopla feed --all-favorite-until-mount      -- feed all pets with favorite food until they are mounts (or favorite food runs out)

# hopla guy
hopla buy enchanted-armoire                 -- buy from enchanted-armoire once and print result in 'everyday' user foramat
hopla buy enchanted-armoire --json          -- buy from enchanted-armoire and print result in json
mutually exclusive group: 
    hopla buy enchanted-armoire --times N       -- buy from enchanted-armoire n times
    hopla buy enchanted-armoire --until-poor    -- buy from enchanted-armoire until you run out of money
    
# hopla api
hopla api version                  -- prints habitica api version
hopla api models {model_name}      -- prints habitica api {model_name}
hopla api content                  -- prints habitica api content
hopla api status                   -- prints habitica api status for 'everyday' user
hopla api status --json            -- prints habitica api status as json

# hopla add todo
hopla add todo "name"                     -- create todo with specified name 
hopla add todo "name" --checklist FILE    -- create todo with checklist as provided in the file
mutually exclusive group:
    hopla add todo "name" --hard
    hopla add todo "name" --medium
    hopla add todo "name" --easy           -- add easy todo (DEFAULT)
    hopla add todo "name" --trivial        -- add trivial todo 
    
mutually exclusive group
    hopla add todo "name" --due-date YYYY-MM-DD  -- add todo with a due-date
    hopla add todo "name" --deadline YYYY-MM-DD  -- synonym for --due-date
    
# hopla complete
hopla complete {shell}            -- provide autocompletion for given shell (only support for bash)

# hopla support-development
hopla support-development                   -- send 3 gems to development (used for testing hopla development)
hopla support-development --gems N          -- send N gems to development 

# hopla get
these should have a mutually exclusive --json vs. 'everyday' user output:
    hopla get user-inventory                 -- get all user-items
    hopla get user-inventory pets            -- list pets
    hopla get user-inventory mounts          -- list mounts
    hopla get user-inventory food            -- list food
    hopla get user-stats --filter [FILTER]   -- filter yourself


these should have a mutually exclusive --json vs. 'everyday' user output:
    hopla get user-stats                     -- get all user-stats
    hopla get user-stats lvl|level           -- get level
    hopla get user-stats hp|health           -- get health
    hopla get user-stats xp|exp|experience   -- get exp
    hopla get user-stats mp|mana|manapoints  -- get mana
    hopla get user-stats gp|gold             -- get gold
    hopla get user-stats --filter [FILTER]   -- filter inventory yourself

these should have a mutually exclusive --json vs. 'everyday' user output:
    hopla get user-auth                    -- get all auth info
    hopla get user-auth user-id|userid     -- get user-id
    hopla get user-auth mail|email|e-mail  -- get user email
    hopla get user-auth name|username      -- get profile name
    hopla get user-auth profilename        -- get profile name
    hopla get user-auth --filter [FILTER]  -- filter auth yourself

these should have a mutually exclusive --json vs. 'everyday' user output:
    hopla get user-info --filter [FILTER]   -- filter on the core user information

```